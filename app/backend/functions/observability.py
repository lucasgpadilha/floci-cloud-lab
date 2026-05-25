from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

JsonDict = dict[str, Any]

_SECRET_FIELD_HINTS = ("secret", "token", "password", "credential", "access_key")


def monotonic_ms() -> float:
    return time.perf_counter() * 1000


def route_template(method: str, path: str) -> str:
    if path.startswith("/objects/"):
        return f"{method} /objects/{{object_id}}"
    return f"{method} {path}"


def status_class(status_code: int) -> str:
    return f"{status_code // 100}xx"


def safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): safe_value("***" if any(hint in str(key).lower() for hint in _SECRET_FIELD_HINTS) else item) for key, item in value.items()}
    if isinstance(value, list):
        return [safe_value(item) for item in value]
    if isinstance(value, tuple):
        return [safe_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def structured_log(
    *,
    level: str,
    message: str,
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    latency_ms: float,
    owner_id: str | None = None,
    object_id: str | None = None,
    error_code: str | None = None,
    extra: JsonDict | None = None,
) -> JsonDict:
    record: JsonDict = {
        "type": "log",
        "service": "floci-cloud-lab-api",
        "runtime": "local-floci",
        "level": level.upper(),
        "message": message,
        "request_id": request_id,
        "trace_id": request_id,
        "method": method,
        "path": path,
        "route": route_template(method, path),
        "status_code": status_code,
        "status_class": status_class(status_code),
        "latency_ms": round(latency_ms, 3),
    }
    if owner_id:
        record["owner_id"] = owner_id
    if object_id:
        record["object_id"] = object_id
    if error_code:
        record["error_code"] = error_code
    if extra:
        record["extra"] = safe_value(extra)
    return record


def metric(name: str, value: float, *, unit: str = "Count", dimensions: JsonDict | None = None) -> JsonDict:
    return {
        "type": "metric",
        "namespace": "FlociCloudLab/Local",
        "metric_name": name,
        "value": value,
        "unit": unit,
        "dimensions": safe_value(dimensions or {}),
    }


def metrics_for_request(*, method: str, path: str, status_code: int, latency_ms: float, error_code: str | None = None) -> list[JsonDict]:
    route = route_template(method, path)
    dimensions = {"route": route, "method": method, "status_class": status_class(status_code)}
    items = [
        metric("ApiRequestCount", 1, dimensions=dimensions),
        metric("ApiLatencyMs", round(latency_ms, 3), unit="Milliseconds", dimensions=dimensions),
    ]
    if status_code >= 400:
        error_dimensions = {**dimensions, "error_code": error_code or "unknown"}
        items.append(metric("ApiErrorCount", 1, dimensions=error_dimensions))
    if method == "POST" and path == "/objects" and status_code == 201:
        items.append(metric("ObjectCreateCount", 1, dimensions={"route": route}))
    if method == "POST" and path == "/events/process" and status_code == 200:
        items.append(metric("EventProcessRequestCount", 1, dimensions={"route": route}))
    return items


@dataclass
class ObservabilitySink:
    records: list[JsonDict] = field(default_factory=list)
    emit_to_stdout: bool = field(default_factory=lambda: os.getenv("FLOCI_OBSERVABILITY_STDOUT", "0") == "1")

    def emit(self, record: JsonDict) -> None:
        safe_record = safe_value(record)
        self.records.append(safe_record)
        if self.emit_to_stdout:
            print(json.dumps(safe_record, sort_keys=True))

    def emit_many(self, records: list[JsonDict]) -> None:
        for record in records:
            self.emit(record)


def extract_object_id_from_body(body: JsonDict | None) -> str | None:
    if not isinstance(body, dict):
        return None
    data = body.get("data")
    if isinstance(data, dict) and isinstance(data.get("object_id"), str):
        return data["object_id"]
    return None
