from __future__ import annotations

from typing import Any

JsonDict = dict[str, Any]


def normalized_headers(event: JsonDict) -> dict[str, str]:
    return {str(key).lower(): str(value) for key, value in (event.get("headers") or {}).items()}


def owner_from_event(event: JsonDict) -> str:
    headers = normalized_headers(event)
    return headers.get("x-floci-user", "local-user").strip() or "local-user"


def request_id_from_event(event: JsonDict) -> str:
    headers = normalized_headers(event)
    request_context = event.get("requestContext") or {}
    return (
        headers.get("x-request-id")
        or request_context.get("requestId")
        or request_context.get("request_id")
        or "local-request"
    )
