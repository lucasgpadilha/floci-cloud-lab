from __future__ import annotations

import re
from typing import Any

JsonDict = dict[str, Any]
SAFE_OWNER_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._:/=-]{1,128}$")


def normalized_headers(event: JsonDict) -> dict[str, str]:
    return {str(key).lower(): str(value) for key, value in (event.get("headers") or {}).items()}


def owner_from_event(event: JsonDict) -> str:
    headers = normalized_headers(event)
    owner_id = headers.get("x-floci-user", "local-user").strip() or "local-user"
    if not SAFE_OWNER_ID.fullmatch(owner_id):
        return "local-user"
    return owner_id


def request_id_from_event(event: JsonDict) -> str:
    headers = normalized_headers(event)
    request_context = event.get("requestContext") or {}
    candidates = [
        headers.get("x-request-id"),
        request_context.get("requestId"),
        request_context.get("request_id"),
    ]
    for candidate in candidates:
        value = str(candidate or "").strip()
        if SAFE_REQUEST_ID.fullmatch(value):
            return value
    return "local-request"
