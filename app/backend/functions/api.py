from __future__ import annotations

import base64
import json
from typing import Any, Callable

from app.backend.functions.auth import normalized_headers, owner_from_event, request_id_from_event
from app.backend.functions.errors import ApiError, BadRequest, NotFound, PayloadTooLarge, UnsupportedMediaType
from app.backend.functions.observability import (
    ObservabilitySink,
    extract_object_id_from_body,
    metrics_for_request,
    monotonic_ms,
    structured_log,
)
from app.backend.functions.ops.reports import build_sanitized_trace_report
from app.backend.functions.ops.session import build_ops_session
from app.backend.functions.ops.traces import TraceEvent, build_trace_detail, build_trace_list, find_trace_event
from app.backend.functions.repository import ObjectRepository, repository_from_env

JsonDict = dict[str, Any]
Handler = Callable[[JsonDict, Any], JsonDict]
MAX_CONTENT_BYTES = 256_000

CORS_HEADERS = {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "content-type,x-floci-user,x-request-id",
    "access-control-expose-headers": "x-request-id",
    "access-control-max-age": "300",
}


def create_handler(repository: ObjectRepository | None = None, observability_sink: ObservabilitySink | None = None) -> Handler:
    repo = repository
    sink = observability_sink or ObservabilitySink()

    def handler(event: JsonDict, context: Any) -> JsonDict:
        request_id = request_id_from_event(event)
        method = _method_from_event(event)
        path = _path_from_event(event)
        owner_id = owner_from_event(event)
        start_ms = monotonic_ms()
        response_body: JsonDict | None = None
        error_code: str | None = None
        try:
            active_repo = repo or repository_from_env()

            if method == "OPTIONS":
                response_body = {"request_id": request_id}
                return _observed_response(204, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path == "/health":
                response_body = {
                    "ok": True,
                    "service": "floci-cloud-lab-api",
                    "runtime": "local-floci",
                    "version": "0.1.0",
                    "request_id": request_id,
                }
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path == "/ops/status":
                response_body = _ops_status_response(request_id)
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path == "/ops/resources":
                response_body = _ops_resources_response(request_id)
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path == "/ops/session":
                response_body = build_ops_session(request_id=request_id, owner_id=owner_id)
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path == "/ops/traces":
                query = _query_parameters_from_event(event)
                events = _trace_events(active_repo.list_events(owner_id=owner_id, status=query.get("status"), limit=_limit_from_query(query))["events"])
                response_body = {"data": build_trace_list(events), "request_id": request_id}
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path.startswith("/ops/traces/"):
                trace_id = path.removeprefix("/ops/traces/").strip()
                if not trace_id:
                    raise BadRequest("validation_error", "trace_id is required")
                events = _trace_events(active_repo.list_events(owner_id=owner_id, limit=100)["events"])
                trace_event = find_trace_event(trace_id=trace_id, events=events)
                if not trace_event:
                    raise NotFound(f"trace {trace_id} was not found")
                response_body = {"trace": build_trace_detail(trace_event, owner_id=owner_id), "request_id": request_id}
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path == "/ops/report":
                query = _query_parameters_from_event(event)
                events = _trace_events(active_repo.list_events(owner_id=owner_id, limit=100)["events"])
                trace_event = find_trace_event(trace_id=query["trace_id"], events=events) if query.get("trace_id") else (events[0] if events else None)
                if not trace_event:
                    raise NotFound("no trace was found for report export")
                trace = build_trace_detail(trace_event, owner_id=owner_id)
                response_body = {"report": build_sanitized_trace_report(trace=trace, request_id=request_id), "request_id": request_id}
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "POST" and path == "/ops/demo/trace":
                record = active_repo.create_object(
                    owner_id=owner_id,
                    name="floci-studio-demo.md",
                    content="# Floci Studio demo\n\nThis object was created by a bounded local trace demo.",
                    content_type="text/markdown",
                    metadata={"category": "flow-demo", "source": "ops-demo-trace"},
                )
                active_repo.process_pending_events(owner_id=owner_id, limit=1)
                response_body = {"trace": _trace_from_record(record, owner_id=owner_id, processed=True), "request_id": request_id}
                return _observed_response(201, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "POST" and path == "/objects":
                _require_json_content_type(event)
                payload = _json_body(event)
                _validate_create_payload(payload)
                record = active_repo.create_object(
                    owner_id=owner_id,
                    name=payload["name"].strip(),
                    content=payload["content"],
                    content_type=payload.get("content_type") or "text/plain",
                    metadata=payload.get("metadata") or {},
                )
                response_body = {"data": record, "request_id": request_id}
                return _observed_response(201, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path == "/objects":
                query = _query_parameters_from_event(event)
                page = active_repo.list_objects(
                    owner_id=owner_id,
                    limit=_limit_from_query(query),
                    cursor=query.get("cursor"),
                    category=query.get("category"),
                )
                response_body = {"data": page, "request_id": request_id}
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path == "/events":
                query = _query_parameters_from_event(event)
                events = active_repo.list_events(
                    owner_id=owner_id,
                    status=query.get("status"),
                    limit=_limit_from_query(query),
                )
                response_body = {"data": events, "request_id": request_id}
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "POST" and path == "/events/process":
                query = _query_parameters_from_event(event)
                result = active_repo.process_pending_events(
                    owner_id=owner_id,
                    limit=_limit_from_query(query),
                )
                response_body = {"data": result, "request_id": request_id}
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            if method == "GET" and path.startswith("/objects/"):
                object_id = path.removeprefix("/objects/").strip()
                if not object_id:
                    raise BadRequest("validation_error", "object_id is required")
                record = active_repo.get_object(owner_id=owner_id, object_id=object_id)
                if not record:
                    raise NotFound(f"object {object_id} was not found")
                response_body = {"data": record, "request_id": request_id}
                return _observed_response(200, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms)

            raise NotFound(f"route {method} {path} is not implemented")
        except ApiError as error:
            error_code = error.code
            response_body = {"error": {"code": error.code, "message": error.message}, "request_id": request_id}
            return _observed_response(error.status_code, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms, error_code=error_code)
        except Exception as error:  # pragma: no cover - defensive Lambda error mapping
            error_code = "internal_error"
            response_body = {"error": {"code": error_code, "message": "unexpected server error"}, "request_id": request_id}
            return _observed_response(500, response_body, request_id=request_id, sink=sink, method=method, path=path, owner_id=owner_id, start_ms=start_ms, error_code=error_code)

    return handler


def lambda_handler(event: JsonDict, context: Any) -> JsonDict:
    return create_handler()(event, context)


def _method_from_event(event: JsonDict) -> str:
    return (
        event.get("requestContext", {})
        .get("http", {})
        .get("method", event.get("httpMethod", "GET"))
        .upper()
    )


def _path_from_event(event: JsonDict) -> str:
    path = event.get("rawPath") or event.get("path")
    if path:
        return path
    return event.get("requestContext", {}).get("http", {}).get("path", "/")


def _query_parameters_from_event(event: JsonDict) -> dict[str, str]:
    params = event.get("queryStringParameters") or {}
    if not isinstance(params, dict):
        return {}
    return {str(key): str(value) for key, value in params.items() if value is not None}


def _limit_from_query(query: dict[str, str]) -> int:
    raw_limit = query.get("limit")
    if raw_limit is None:
        return 25
    try:
        limit = int(raw_limit)
    except ValueError as exc:
        raise BadRequest("validation_error", "limit must be an integer") from exc
    if limit < 1 or limit > 100:
        raise BadRequest("validation_error", "limit must be between 1 and 100")
    return limit


def _require_json_content_type(event: JsonDict) -> None:
    headers = normalized_headers(event)
    content_type = headers.get("content-type", "")
    if not content_type.startswith("application/json"):
        raise UnsupportedMediaType("POST /objects requires content-type application/json")


def _json_body(event: JsonDict) -> JsonDict:
    raw_body = event.get("body")
    if not raw_body:
        return {}
    if event.get("isBase64Encoded"):
        try:
            raw_body = base64.b64decode(raw_body).decode("utf-8")
        except Exception as exc:  # pragma: no cover - defensive decode branch
            raise BadRequest("invalid_json", "request body base64 could not be decoded as UTF-8") from exc
    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise BadRequest("invalid_json", "request body must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise BadRequest("validation_error", "request body must be a JSON object")
    return parsed


def _validate_create_payload(payload: JsonDict) -> None:
    name = payload.get("name")
    content = payload.get("content")
    metadata = payload.get("metadata", {})
    content_type = payload.get("content_type", "text/plain")

    if not isinstance(name, str) or not name.strip():
        raise BadRequest("validation_error", "name is required and must be a non-empty string")
    if not isinstance(content, str):
        raise BadRequest("validation_error", "content is required and must be a string")
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise PayloadTooLarge(f"content must be {MAX_CONTENT_BYTES // 1000} KB or smaller for the local lab API")
    if not isinstance(metadata, dict):
        raise BadRequest("validation_error", "metadata must be an object when provided")
    if not isinstance(content_type, str) or "/" not in content_type:
        raise BadRequest("validation_error", "content_type must be a valid media type when provided")


def _ops_status_response(request_id: str) -> JsonDict:
    components = [
        {
            "id": "api",
            "name": "Backend API",
            "category": "compute",
            "status": "online",
            "engine": "Python Lambda-style HTTP adapter",
            "aws_equivalent": "AWS::Lambda::Function",
            "capabilities": ["http-api", "object-crud", "event-processing", "cors"],
        },
        {
            "id": "storage",
            "name": "Object Storage",
            "category": "storage",
            "status": "online",
            "engine": "S3 (Local)",
            "aws_equivalent": "AWS::S3::Bucket",
            "capabilities": ["put-object", "get-object", "list-objects", "versioning"],
        },
        {
            "id": "database",
            "name": "Metadata Store",
            "category": "database",
            "status": "online",
            "engine": "DynamoDB (Local)",
            "aws_equivalent": "AWS::DynamoDB::Table",
            "capabilities": ["metadata-index", "event-outbox", "pagination", "category-filter"],
        },
        {
            "id": "observability",
            "name": "Local Observability",
            "category": "observability",
            "status": "configured",
            "engine": "Structured logs and in-process metrics",
            "aws_equivalent": "AWS::Logs::LogGroup",
            "capabilities": ["structured-logs", "request-metrics", "request-id-correlation"],
        },
    ]
    return {
        "status": "ready",
        "mode": "local",
        "service": "floci-cloud-lab-api",
        "runtime": "local-floci",
        "environment": {
            "local_only": True,
            "cloud_provider": "aws-compatible",
            "emulator": "floci",
            "region": "us-east-1",
            "account_id": "000000000000",
        },
        "emulator": {
            "name": "Floci",
            "endpoint": "http://localhost:4566",
            "connected": True,
            "status": "online",
        },
        "database": {"engine": "DynamoDB (Local)", "status": "online"},
        "storage": {"engine": "S3 (Local)", "status": "online"},
        "components": components,
        "safety": {
            "local_only": True,
            "uses_real_cloud": False,
            "uses_real_credentials": False,
            "allows_shell_execution": False,
            "bounded_mutations_only": True,
        },
        "dashboard": {
            "recommended_refresh_seconds": 5,
            "primary_actions": [
                {"id": "create-demo-object", "label": "Create demo object", "method": "POST", "path": "/objects", "safe": True},
                {"id": "process-events", "label": "Process pending events", "method": "POST", "path": "/events/process?limit=10", "safe": True},
            ],
        },
        "request_id": request_id,
    }


def _ops_resources_response(request_id: str) -> JsonDict:
    resources = [
        _resource(
            id="api-function",
            name="floci-cloud-lab-local-api",
            type="AWS::Lambda::Function",
            category="compute",
            local_id="local-api-handler",
            service="lambda",
            resource_type="function",
            description="Local API handler equivalent to a Lambda-backed HTTP API",
            capabilities=["http-routing", "validation", "cors", "observability"],
            display_order=5,
            badge="API",
            contains_demo_data=False,
        ),
        _resource(
            id="objects-bucket",
            name="floci-cloud-lab-local-objects",
            type="AWS::S3::Bucket",
            category="storage",
            local_id="local-objects-bucket",
            service="s3",
            resource_type="bucket",
            description="Primary object storage",
            capabilities=["put-object", "get-object", "list-objects", "versioning"],
            display_order=10,
            badge="Storage",
        ),
        _resource(
            id="metadata-table",
            name="floci-cloud-lab-local-metadata",
            type="AWS::DynamoDB::Table",
            category="database",
            local_id="local-metadata-table",
            service="dynamodb",
            resource_type="table",
            description="Object metadata and event store",
            capabilities=["object-metadata", "event-outbox", "query-by-owner", "pagination"],
            display_order=20,
            badge="Database",
        ),
        _resource(
            id="app-logs",
            name="/floci-cloud-lab/local/app",
            type="AWS::Logs::LogGroup",
            category="observability",
            local_id="local-app-logs",
            service="cloudwatch",
            resource_type="log-group",
            description="Application logs and request traces",
            capabilities=["structured-logs", "request-id-correlation", "error-tracking"],
            display_order=30,
            badge="Logs",
        ),
    ]
    return {
        "resources": resources,
        "categories": [
            {"id": "compute", "label": "Compute", "description": "Local API and request handling"},
            {"id": "storage", "label": "Storage", "description": "S3-compatible object storage"},
            {"id": "database", "label": "Database", "description": "DynamoDB-compatible metadata and events"},
            {"id": "observability", "label": "Observability", "description": "Logs, metrics, and traces"},
        ],
        "summary": {"count": len(resources), "available": len(resources), "degraded": 0, "offline": 0, "local_only": True},
        "request_id": request_id,
    }


def _resource(
    *,
    id: str,
    name: str,
    type: str,
    category: str,
    local_id: str,
    service: str,
    resource_type: str,
    description: str,
    capabilities: list[str],
    display_order: int,
    badge: str,
    contains_demo_data: bool = True,
) -> JsonDict:
    return {
        "id": id,
        "name": name,
        "type": type,
        "category": category,
        "local_id": local_id,
        "aws_equivalent": {"service": service, "resource_type": resource_type, "cloudformation_type": type},
        "status": "available",
        "description": description,
        "capabilities": capabilities,
        "safety": {"local_only": True, "contains_demo_data": contains_demo_data, "uses_real_cloud": False, "allows_shell_execution": False},
        "dashboard": {"display_order": display_order, "badge": badge, "recommended_view": "resource-card"},
    }


def _trace_events(events: list[JsonDict]) -> list[TraceEvent]:
    return [TraceEvent.from_repository_event(event) for event in events]


def _trace_from_record(record: JsonDict, *, owner_id: str, processed: bool) -> JsonDict:
    event = dict(record.get("event") or {})
    if processed:
        event["status"] = "processed"
        event["attempts"] = max(int(event.get("attempts") or 0), 1)
    return build_trace_detail(TraceEvent.from_repository_event(event), owner_id=owner_id)


def _observed_response(
    status_code: int,
    body: JsonDict,
    *,
    request_id: str,
    sink: ObservabilitySink,
    method: str,
    path: str,
    owner_id: str,
    start_ms: float,
    error_code: str | None = None,
) -> JsonDict:
    latency_ms = monotonic_ms() - start_ms
    object_id = extract_object_id_from_body(body)
    sink.emit(
        structured_log(
            level="ERROR" if status_code >= 500 else "WARN" if status_code >= 400 else "INFO",
            message="api request completed",
            request_id=request_id,
            method=method,
            path=path,
            status_code=status_code,
            latency_ms=latency_ms,
            owner_id=owner_id,
            object_id=object_id,
            error_code=error_code,
        )
    )
    sink.emit_many(metrics_for_request(method=method, path=path, status_code=status_code, latency_ms=latency_ms, error_code=error_code))
    return _json_response(status_code, body, request_id=request_id)


def _json_response(status_code: int, body: JsonDict, *, request_id: str) -> JsonDict:
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "x-request-id": request_id,
            **CORS_HEADERS,
        },
        "body": "" if status_code == 204 else json.dumps(body, sort_keys=True),
        "isBase64Encoded": False,
    }


def _error_response(status_code: int, code: str, message: str, *, request_id: str) -> JsonDict:
    return _json_response(
        status_code,
        {"error": {"code": code, "message": message}, "request_id": request_id},
        request_id=request_id,
    )
