#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.backend.functions.api import create_handler
from app.backend.functions.observability import ObservabilitySink


def invoke(handler, method: str, path: str, body=None, user="observability-demo", headers=None, query=None):
    event = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "requestContext": {"requestId": f"obs-{method.lower()}-{path.strip('/').replace('/', '-') or 'root'}", "http": {"method": method, "path": path}},
        "headers": {"x-floci-user": user, "content-type": "application/json", **(headers or {})},
        "queryStringParameters": query or {},
        "body": json.dumps(body) if isinstance(body, dict) else body,
        "isBase64Encoded": False,
    }
    response = handler(event, None)
    print(f"{method} {path} -> {response['statusCode']}")
    return response


def main() -> int:
    sink = ObservabilitySink()
    handler = create_handler(observability_sink=sink)

    invoke(handler, "GET", "/health")
    created = invoke(
        handler,
        "POST",
        "/objects",
        {
            "name": "observability-demo.txt",
            "content": "created to demonstrate structured logs and local metrics",
            "content_type": "text/plain",
            "metadata": {"source": "observability-demo", "category": "operations"},
        },
    )
    object_id = json.loads(created["body"])["data"]["object_id"] if created["statusCode"] == 201 else "missing"
    invoke(handler, "GET", f"/objects/{object_id}")
    invoke(handler, "POST", "/objects", '{"name":"bad","content":"bad"}', headers={"content-type": "text/plain"})
    invoke(handler, "POST", "/events/process")

    print("\n== structured observability records ==")
    for record in sink.records:
        print(json.dumps(record, sort_keys=True))

    log_count = sum(1 for record in sink.records if record.get("type") == "log")
    metric_count = sum(1 for record in sink.records if record.get("type") == "metric")
    error_count = sum(1 for record in sink.records if record.get("metric_name") == "ApiErrorCount")
    print("\n== summary ==")
    print(json.dumps({"logs": log_count, "metrics": metric_count, "error_metrics": error_count}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
