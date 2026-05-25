# Evidence — Observability Demo

Phase 7 demonstrates structured logs and local CloudWatch-style metrics for the Floci Cloud Lab API.

## Command

```bash
make observability-demo
```

## Expected output shape

The demo prints request outcomes followed by JSON Lines records. Example fields:

```json
{
  "type": "log",
  "service": "floci-cloud-lab-api",
  "runtime": "local-floci",
  "level": "INFO",
  "request_id": "obs-post-objects",
  "trace_id": "obs-post-objects",
  "method": "POST",
  "path": "/objects",
  "route": "POST /objects",
  "status_code": 201,
  "status_class": "2xx",
  "latency_ms": 10.0,
  "owner_id": "observability-demo",
  "object_id": "obj_example"
}
```

Metric examples:

```json
{"type":"metric","namespace":"FlociCloudLab/Local","metric_name":"ApiRequestCount","value":1,"unit":"Count"}
{"type":"metric","namespace":"FlociCloudLab/Local","metric_name":"ApiLatencyMs","value":10.0,"unit":"Milliseconds"}
{"type":"metric","namespace":"FlociCloudLab/Local","metric_name":"ApiErrorCount","value":1,"unit":"Count"}
```

## Validation

Targeted tests:

```bash
.venv/bin/python -m pytest tests/unit/test_observability.py tests/unit/test_api_handler.py -q
```

Latest targeted result during implementation:

```text
14 passed
```

Latest demo result during implementation:

```text
GET /health -> 200
POST /objects -> 201
GET /objects/{object_id} -> 200
POST /objects -> 415
POST /events/process -> 200
summary: {"error_metrics": 1, "logs": 5, "metrics": 13}
```

Full validation run during implementation:

```text
make check: 45 passed
make devops-audit: ok: local-only DevOps audit passed
```
