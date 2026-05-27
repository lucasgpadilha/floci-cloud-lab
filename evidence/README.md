# Evidence Index

This directory stores sanitized, reviewable evidence that the Floci Cloud Lab can be validated locally.

Evidence files should avoid secrets, personal tokens, real AWS account IDs, real AWS ARNs, and machine-specific noise unless it is necessary context.

## Current evidence artifacts

| File | Purpose | How to regenerate |
| --- | --- | --- |
| `app-demo.md` | Captures the local app demo path and example behavior. | Run `make app-demo` after Floci is healthy. |
| `local-apply.md` | Captures the approved local Terraform apply evidence against Floci. | Only regenerate after explicit human approval for local apply. |
| `portfolio-walkthrough.md` | Captures Phase 1 portfolio validation checks. | Run `make check` and `make devops-audit`, then summarize sanitized output. |
| `iam-security.md` | Captures Phase 2 IAM/security validation checks. | Run `terraform -chdir=infra/envs/local fmt -recursive ../..`, `make check`, and `make devops-audit`. |
| `api-gateway-lambda.md` | Captures Phase 3 API Gateway/Lambda contract validation. | Run `make check`, `make devops-audit`, and `make app-demo`. |
| `dynamodb-data-model.md` | Captures Phase 4 DynamoDB model, pagination, conditional write, TTL, and GSI-gap validation. | Run `make check`, `make devops-audit`, and `make app-demo`. |
| `s3-object-storage.md` | Captures Phase 5 S3 key naming, metadata, integrity, versioning, and presigned URL validation. | Run `make check`, `make devops-audit`, and `make app-demo`. |
| `event-driven-architecture.md` | Captures Phase 6 outbox event and idempotent worker validation. | Run `make check`, `make devops-audit`, and `make app-demo`. |
| `observability-demo.md` | Captures Phase 7 structured logs, local metrics, request correlation, and CloudWatch-style operations evidence. | Run `make observability-demo`, `make check`, and `make devops-audit`. |
| `resilience-drill.md` | Captures Phase 8 backup/restore planning, failure injection, and idempotent replay evidence. | Run `make resilience-drill`, `make check`, and `make devops-audit`. |
| `orchestration-demo.md` | Captures Phase 9 Step Functions-style orchestration, retry/catch, compensation, and idempotency evidence. | Run `make orchestration-demo`, `make check`, and `make devops-audit`. |
| `container-demo.md` | Captures Phase 10 local container build/run healthcheck and ECS/Fargate mapping evidence. | Run `make app-container-demo`, `make check`, and `make devops-audit`. |

## Recommended regeneration flow

```bash
make floci-up
make floci-health
make check
make devops-audit
make terraform-plan-local
make app-demo
```

## Safety rules

- Do not include real AWS credentials.
- Do not include real AWS account IDs.
- Do not include real `.env` values.
- Do not capture `.terraform/`, `*.tfstate`, `.venv/`, or cache directories.
- Keep evidence focused on reviewer-useful outcomes: command, date, result, and short sanitized output.

## Review checklist

Before adding evidence to git, verify:

- The command used a local endpoint such as `http://localhost:4566`.
- The output does not include tokens or secrets.
- The output is short enough for a reviewer to scan.
- The evidence states whether the command passed, failed, or was skipped.


