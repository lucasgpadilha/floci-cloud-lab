from __future__ import annotations

import re
from typing import Any

JsonDict = dict[str, Any]
SECRET_NAME_PATTERN = r"(?:AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID|api[_-]?key|secret|password|passwd|token)"
SECRET_ASSIGNMENT = re.compile(
    rf"\b{SECRET_NAME_PATTERN}\b\s*[:=]\s*(?:'[^']*'|\"[^\"]*\"|[^\s,;}}]+)",
    re.IGNORECASE,
)
SECRET_NAMES = re.compile(rf"\b{SECRET_NAME_PATTERN}\b", re.IGNORECASE)


def build_sanitized_trace_report(*, trace: JsonDict, request_id: str) -> JsonDict:
    return {
        "format": "floci.trace-report.v1",
        "request_id": request_id,
        "trace": sanitize_secrets(trace),
        "safety": {
            "sanitized": True,
            "contains_real_credentials": False,
            "local_only": True,
            "allows_shell_execution": False,
        },
        "reproduction": {
            "local_only": True,
            "requires_real_cloud": False,
            "commands": sanitize_secrets(trace.get("commands", [])),
        },
    }


def sanitize_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize_secrets(item) for key, item in value.items() if not _is_sensitive_key(str(key))}
    if isinstance(value, list):
        return [sanitize_secrets(item) for item in value]
    if isinstance(value, str):
        sanitized = SECRET_ASSIGNMENT.sub("[REDACTED]", value)
        return SECRET_NAMES.sub("[REDACTED]", sanitized)
    return value


def _is_sensitive_key(key: str) -> bool:
    return bool(SECRET_NAMES.search(key))
