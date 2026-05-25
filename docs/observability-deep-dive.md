# Observability Deep Dive

Phase 7 adds local observability signals that map cleanly to AWS operational practices while staying safe in the Floci emulator environment.

## Signals implemented

The Lambda-style API handler now emits in-memory structured observability records during each request. The demo script prints them as JSON Lines for portfolio evidence.

### Structured logs

Each API request emits a log record with:

- `type=log`
- `service=floci-cloud-lab-api`
- `runtime=local-floci`
- `level`
- `message`
- `request_id`
- `trace_id`
- `method`
- `path`
- `route`
- `status_code`
- `status_class`
- `latency_ms`
- `owner_id` when available
- `object_id` when available
- `error_code` for handled errors

The local `trace_id` is equal to `request_id` so every request can be correlated across API responses, logs, and local metrics.

### Metrics

Each API request emits CloudWatch-style metric records in the local namespace:

```text
FlociCloudLab/Local
```

Metrics currently modeled:

- `ApiRequestCount`
- `ApiLatencyMs`
- `ApiErrorCount`
- `ObjectCreateCount`
- `EventProcessRequestCount`

Dimensions include route, method, status class, and error code where relevant.

### Secret hygiene

The observability helper redacts secret-like field names such as `secret`, `token`, `password`, `credential`, and `access_key` before emission. Tests assert that sensitive header values do not appear in records.

## Demo

Run:

```bash
make observability-demo
```

The script performs:

1. `GET /health`
2. `POST /objects`
3. `GET /objects/{object_id}`
4. a deliberate `415` validation failure
5. `POST /events/process`

Then it prints all structured logs and metric records as JSON Lines plus a count summary.

## AWS production mapping

| Local signal | AWS equivalent | Purpose |
| --- | --- | --- |
| JSON log record | CloudWatch Logs | Request-level troubleshooting and audit trail |
| `request_id` / `trace_id` | API Gateway request ID, Lambda request ID, X-Ray trace ID | Correlation across services |
| Metric JSON record | CloudWatch custom metric / EMF | Dashboards and alarms |
| `ApiErrorCount` | CloudWatch alarm on 4xx/5xx count/rate | Detect client/server error spikes |
| `ApiLatencyMs` | p95/p99 latency alarm | Detect performance regressions |
| `EventProcessRequestCount` | Worker throughput metric | Detect queue/worker stalls |

## Alarm templates

The repo documents the alarm model but does not add physical CloudWatch metric alarms yet, because adding resources would require a local Terraform migration/apply. Future approved alarms:

- high API 5xx count or rate;
- high API p95 latency;
- event-processing failures;
- pending event backlog age/count;
- DLQ message count when physical queues are introduced.

## Dashboard concept

A useful dashboard would show:

- request count by route/status class;
- p50/p95/p99 latency by route;
- error count by error code;
- object creation count;
- event processing count;
- pending/processed event backlog;
- recent structured log search by request id.

## Local-vs-real boundary

This phase intentionally keeps logs/metrics local and deterministic. It demonstrates the shape, fields, tests, and operational reasoning expected in AWS without requiring CloudWatch API mutations beyond the already-applied log group.
