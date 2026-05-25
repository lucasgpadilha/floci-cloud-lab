from __future__ import annotations

import json
from typing import Any, Callable

from app.backend.functions.repository import ObjectRepository, repository_from_env

JsonDict = dict[str, Any]
Handler = Callable[[JsonDict, Any], JsonDict]


def create_handler(repository: ObjectRepository | None = None) -> Handler:
    repo = repository

    def handler(event: JsonDict, context: Any) -> JsonDict:
        active_repo = repo or repository_from_env()
        method = _method_from_event(event)
        path = _path_from_event(event)
        owner_id = _owner_from_event(event)

        if method == "GET" and path == "/health":
            return _json_response(
                200,
                {
                    "ok": True,
                    "service": "floci-cloud-lab-api",
                    "runtime": "local-floci",
                    "version": "0.1.0",
                },
            )

        if method == "POST" and path == "/objects":
            payload = _json_body(event)
            error = _validate_create_payload(payload)
            if error:
                return _error_response(400, "validation_error", error)

            record = active_repo.create_object(
                owner_id=owner_id,
                name=payload["name"].strip(),
                content=payload["content"],
                content_type=payload.get("content_type") or "text/plain",
                metadata=payload.get("metadata") or {},
            )
            return _json_response(201, {"data": record})

        if method == "GET" and path == "/objects":
            objects = active_repo.list_objects(owner_id=owner_id)
            return _json_response(200, {"data": {"count": len(objects), "objects": objects}})

        if method == "GET" and path.startswith("/objects/"):
            object_id = path.removeprefix("/objects/").strip()
            if not object_id:
                return _error_response(400, "validation_error", "object_id is required")
            record = active_repo.get_object(owner_id=owner_id, object_id=object_id)
            if not record:
                return _error_response(404, "not_found", f"object {object_id} was not found")
            return _json_response(200, {"data": record})

        return _error_response(404, "not_found", f"route {method} {path} is not implemented")

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


def _owner_from_event(event: JsonDict) -> str:
    headers = {str(k).lower(): str(v) for k, v in (event.get("headers") or {}).items()}
    return headers.get("x-floci-user", "local-user").strip() or "local-user"


def _json_body(event: JsonDict) -> JsonDict:
    raw_body = event.get("body")
    if not raw_body:
        return {}
    if event.get("isBase64Encoded"):
        return {}
    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _validate_create_payload(payload: JsonDict) -> str | None:
    name = payload.get("name")
    content = payload.get("content")
    metadata = payload.get("metadata", {})

    if not isinstance(name, str) or not name.strip():
        return "name is required and must be a non-empty string"
    if not isinstance(content, str):
        return "content is required and must be a string"
    if len(content.encode("utf-8")) > 256_000:
        return "content must be 256 KB or smaller for the local lab API"
    if not isinstance(metadata, dict):
        return "metadata must be an object when provided"
    return None


def _json_response(status_code: int, body: JsonDict) -> JsonDict:
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
        },
        "body": json.dumps(body, sort_keys=True),
    }


def _error_response(status_code: int, code: str, message: str) -> JsonDict:
    return _json_response(status_code, {"error": {"code": code, "message": message}})
