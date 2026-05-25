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
