# Project Status

Updated: 2026-05-25T12:20:08-03:00

## Current status

The local Floci Cloud Lab baseline is available in the isolated worktree:

`/home/lucas/agentic/runs/floci-cloud-lab-codex`

The primary repo checkout remains at:

`/home/lucas/projects/floci-cloud-lab`

The initial baseline was committed and pushed to GitHub on `main` after explicit approval.

A comprehensive AWS proficiency roadmap is now planned in:

`docs/plans/aws-proficiency-roadmap.md`

## Completed

- Created the local-first portfolio repo structure.
- Added documentation for architecture, Floci workflow, local IaC validation, CI/CD without GitHub Actions/GitLab runners, security, cost learning, observability, and runbook.
- Added Terraform local environment and modules for the first emulator-backed resources.
- Added Docker Compose Floci startup flow.
- Added Python/boto3 smoke tests against the local emulator endpoint.
- Added Makefile pipeline targets.
- Applied Terraform against the local Floci endpoint after explicit user approval.
- Added a guarded `terraform-apply-local` Makefile target.
- Implemented a Python Lambda-style API handler with `/health`, `POST /objects`, `GET /objects`, and `GET /objects/{id}`.
- Implemented S3-compatible object storage plus DynamoDB-compatible metadata persistence through boto3.
- Added unit and integration tests for the API and local Floci persistence path.
- Added a local HTTP adapter for browser testing with `make app-api-local`.
- Added a polished static frontend at `app/frontend/index.html`.
- Added a CLI demo at `scripts/app-demo.sh` exposed through `make app-demo`.
- Added DevOps-focused validation via `make devops-audit`: forbidden CI checks, local-only endpoint checks, shell syntax, Docker Compose validation, Terraform drift detection, and full test suite.
- Added `docs/devops-testing.md` describing the DevOps validation strategy.
- Added Phase 1 portfolio polish: `docs/portfolio-walkthrough.md`, `evidence/README.md`, and `evidence/portfolio-walkthrough.md`.
- Added Phase 2 IAM/security foundations: IAM policy JSON documents, Terraform IAM module outputs, security documentation, wildcard policy tests, and DevOps audit wildcard guard.
- Added Phase 3 API Gateway/Lambda proficiency: HTTP API v2 contract tests, request IDs, CORS behavior, OpenAPI documentation, frontend error/request-id display, and consistent error envelopes.
- Added Phase 4 DynamoDB proficiency: data-model documentation, conditional writes, category index fields with local fallback, pagination contract, version attributes, optional TTL fields, and model/contract/integration tests.
- Added Phase 5 S3 proficiency: safe object key naming, content-type and metadata persistence, SHA-256 integrity metadata, retrieval verification, local presigned URL evidence, and S3 docs covering lifecycle/multipart/security/cost trade-offs.
- Added Phase 6 event-driven architecture: ObjectCreated outbox events, event listing, idempotent local event processing, and SQS/SNS/EventBridge mapping documentation.
- Added Phase 7 observability/operations: structured JSON logs, CloudWatch-style local metrics, request/trace correlation, observability demo, deep-dive docs, evidence, and incident drills.
- Added Phase 8 resilience/operations drills: deterministic backup manifests, restore plan ordering, checksum validation, failure-injection taxonomy, idempotent event replay tests, and evidence.
- Added Phase 9 orchestration workflows: Step Functions-style state machine simulation, retry/catch modeling, compensation planning, deterministic execution history, tests, demo, and evidence.
- Added Phase 10 containers/ECS-style workflows: local app Docker image, Compose service, healthcheck demo, container config tests, ECS/Fargate mapping docs, and evidence.

## Local resources created in Floci

Terraform apply created 4 emulator-local resources:

- DynamoDB table: `floci-cloud-lab-local-metadata`
- S3 bucket: `floci-cloud-lab-local-objects`
- S3 bucket versioning for `floci-cloud-lab-local-objects`
- CloudWatch log group: `/floci-cloud-lab/local/app`

Endpoint:

`http://localhost:4566`

Credentials are fake local credentials only:

- `AWS_ACCESS_KEY_ID=test`
- `AWS_SECRET_ACCESS_KEY=test`
- `AWS_DEFAULT_REGION=us-east-1`

## Validation results

Commands run successfully:

```bash
make floci-up
make floci-health
make floci-smoke
terraform -chdir=infra/envs/local apply -auto-approve
make app-demo
make devops-audit
make check
make terraform-plan-local
agent-status
agent-review
```

Results:

- Floci health check: passed
- Smoke tests: passed
- Unit tests: passed
- Integration tests against Floci: passed
- Full Python test suite: `34 passed` before Phase 6; Phase 6 adds eventing tests
- Terraform validate: passed
- Terraform apply: `4 added, 0 changed, 0 destroyed`; rerun on 2026-05-25 to recreate local emulator resources after Floci restart
- Terraform plan after apply: no changes
- Terraform drift audit: passed with detailed exit code `0`
- Docker Compose config validation: passed
- Shell syntax checks: passed
- Forbidden CI check: passed; no GitHub Actions/GitLab runner config present

## Safety notes

- Terraform provider is configured with fake credentials.
- Terraform provider uses local Floci service endpoints.
- `terraform-apply-local` refuses non-local Floci endpoints based on `FLOCI_ENDPOINT`.
- `.terraform/`, `*.tfstate`, `.venv/`, `.env`, and evidence logs/json are ignored by git.

## Remaining work

Recommended next phases:

1. Complete review/approval for Phase 1 portfolio polish, Phase 2 IAM/security foundations, Phase 3 API Gateway/Lambda proficiency, Phase 4 DynamoDB proficiency, and Phase 5 S3 proficiency.
2. Review/approve Phases 6-10 and decide whether to run future local Terraform migrations for physical queues/topics/rules, CloudWatch alarms/dashboards, backup-oriented resources, Step Functions resources, or ECR/ECS resources.
3. Add CodeBuild-style local pipeline dogfooding or richer frontend/reviewer demo polish.
4. Add richer evidence capture for portfolio screenshots/logs.
5. Decide whether to copy or merge the isolated worktree result into the primary checkout after human review.

## Human approval still required

Before doing any of the following, get explicit approval:

- Commit
- Push
- Merge/rebase
- Any real AWS command or resource mutation
- Any GitHub Actions/GitLab runner configuration
