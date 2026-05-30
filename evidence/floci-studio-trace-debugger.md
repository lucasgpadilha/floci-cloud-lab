# Floci Studio — trace debugger evidence pack

This document is the Phase 14 evidence entry point for Floci Studio, the local cloud workflow debugger inside Floci Cloud Lab.

## Goal

Prove the Floci Studio differentiator in a way that is useful for portfolio review and AWS/OCI DevOps interview prep:

```text
request -> local API -> object storage -> metadata -> outbox event -> processor result -> sanitized report
```

The point is not to show another generic dashboard. The point is to show causal debugging for AWS-shaped workflows running locally on the Floci emulator.

## What this evidence should demonstrate

1. The API is reachable locally.
2. `/ops/session` describes the local-only workbench capabilities.
3. `/ops/demo/broken-trace` creates a deterministic failed workflow.
4. `/ops/traces/{trace_id}` explains the causal steps and failure reason.
5. `/ops/report?trace_id=...` exports sanitized reviewer-safe JSON.
6. Missing local emulator resources return an actionable dependency error instead of a generic 500.
7. Nothing touches real AWS, hosted CI, or production infrastructure.

## Capture command

From the repo root:

```bash
make app-api-local
```

In another terminal:

```bash
FLOCI_ENDPOINT=http://localhost:4566 \
AWS_ENDPOINT_URL=http://localhost:4566 \
API_URL=http://127.0.0.1:8080 \
OWNER_ID=portfolio-evidence \
bash scripts/floci-studio-evidence.sh
```

The script writes this file by default:

```text
evidence/floci-studio-trace-debugger.md
```

## Safety guarantees in the capture script

`scripts/floci-studio-evidence.sh` refuses to run unless all endpoints are local:

- `FLOCI_ENDPOINT` must be `http://localhost:4566` or `http://127.0.0.1:4566`.
- `AWS_ENDPOINT_URL` must be `http://localhost:4566` or `http://127.0.0.1:4566`.
- `API_URL` must be `http://localhost:8080` or `http://127.0.0.1:8080`.

The script does not run:

- `terraform apply`;
- real AWS commands;
- hosted CI;
- destructive cleanup.

Output is sanitized for common secret-looking values before being written.

## Expected runtime outcomes

### Fully provisioned local Floci resources

If the local bucket/table exist, the first-click path should produce:

- `GET /health` -> `200`
- `GET /ops/session` -> `200`
- `POST /ops/demo/broken-trace` -> `201`
- `GET /ops/traces/{trace_id}` -> `200`
- `GET /ops/report?trace_id=...` -> `200`

That is the portfolio-grade happy path.

### Missing local Floci resources

If Floci is running but bucket/table resources are missing, demo endpoints may return:

```text
503 local_dependency_unavailable
```

That is still a good product behavior. It means the API is not pretending the demo worked and is not exposing a generic internal error.

Do not auto-run `terraform apply`. Local emulator resource creation is still an infrastructure mutation and should be approved explicitly.

## Interview story

| Interview angle | What this proves locally | Cloud equivalent |
| --- | --- | --- |
| Serverless debugging | Follow a request through object write, metadata, event, processor failure | API Gateway, Lambda, S3, DynamoDB, EventBridge/SQS |
| Shift-left validation | Catch workflow contract errors before cloud deployment | LocalStack/SAM/CDK local-style workflows, pre-prod validation |
| Observability discipline | Export trace detail and sanitized evidence | CloudWatch Logs, X-Ray, ServiceLens, OpenTelemetry |
| AWS vs OCI comparison | Same workflow thinking applies across providers | OCI Functions, Object Storage, Events, Logging |
| Cost/safety | No real cloud spend or accidental retry storms | FinOps and safe developer environments |

## Current validation status

Last validation performed during Phase 14 setup:

```bash
.venv/bin/python -m pytest tests/unit -q
```

Expected current result after Phase 13 merge:

```text
92 passed
```

Script syntax validation:

```bash
bash -n scripts/floci-studio-evidence.sh
```

Whitespace validation:

```bash
git diff --check
```

## Next product step

After this evidence pack is captured against a provisioned local Floci runtime, the next high-value increment is:

```text
bounded trace replay: inspect failed trace -> patch local input -> rerun -> compare before/after report
```

That would turn Floci Studio from “trace viewer” into a stronger local cloud debugging workbench.
