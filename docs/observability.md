# Observability

## Goal

Show how serverless systems are monitored using AWS-shaped observability practices while running locally through Floci.

## Implemented local signals

Phase 7 adds:

- structured JSON request logs from the Lambda-style handler;
- request and trace correlation through `request_id` / `trace_id`;
- route, method, status, latency, owner, object, and error-code fields;
- local CloudWatch-style metric records;
- secret redaction for observability payloads;
- a reproducible observability demo through `make observability-demo`;
- unit tests for log/metric shape and secret hygiene.

## Deep dive

See:

```text
docs/observability-deep-dive.md
```

## Evidence

See:

```text
evidence/observability-demo.md
```

## Local vs AWS

The current implementation emits observability records locally for deterministic tests and portfolio evidence. In real AWS, the same shape maps to:

- CloudWatch Logs;
- CloudWatch custom metrics or Embedded Metric Format;
- CloudWatch alarms;
- CloudWatch dashboards;
- AWS X-Ray or OpenTelemetry trace correlation.

No real AWS observability resources are created by default.
