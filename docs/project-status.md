# Project Status

Updated: 2026-05-30T13:46:07-03:00

## Current status

The merged lab now includes Floci Studio, a trace-first local workflow debugger for AWS-shaped emulator flows. Phase 14 is adding the runtime evidence pack that proves the first-click debugging path and keeps the local-only safety boundary explicit.

The active Phase 14 worktree is:

`/home/lucas/agentic/runs/floci-cloud-lab-gemini`


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
- Added Phase 11 Kubernetes platform baseline: portable Kubernetes manifests, static validation, EKS vs OKE comparison docs, and local-only evidence notes.
- Added Phase 12 local CI/CD and evidence capture: deterministic `make pipeline`, sanitized `make evidence`, release approval gates, and Hermes/agentic delivery workflow docs.
- Added Phase 13 Floci Studio: trace-first local workflow debugger, bounded demo traces, broken-flow debugger slice, sanitized report export, and browser workbench UI.
- Started Phase 14 Floci Studio runtime evidence: `scripts/floci-studio-evidence.sh`, `make floci-studio-evidence`, and `evidence/floci-studio-trace-debugger.md`.

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
- Phase 12 evidence capture writes sanitized output to `evidence/pipeline-latest.md` after local validation.
- Phase 14 local validation: unit suite currently reports `92 passed`; `bash -n scripts/floci-studio-evidence.sh` and `git diff --check` are required before commit.

## Safety notes

- Terraform provider is configured with fake credentials.
- Terraform provider uses local Floci service endpoints.
- `terraform-apply-local` refuses non-local Floci endpoints based on `FLOCI_ENDPOINT`.
- `.terraform/`, `*.tfstate`, `.venv/`, `.env`, and noisy cache directories are excluded from evidence capture.

## Remaining work

Recommended next phases:

1. Run the Floci Studio evidence capture against a provisioned local emulator runtime.
2. Review the generated `evidence/floci-studio-trace-debugger.md` for portfolio clarity.
3. If local bucket/table resources are missing, explicitly approve bounded local provisioning before rerunning runtime capture.
4. Next product increment: bounded trace replay (`inspect failed trace -> patch local input -> rerun -> compare reports`).

## Human approval still required

Before doing any of the following, get explicit approval:

- Commit
- Push
- Merge/rebase
- Any real AWS command or resource mutation
- Any GitHub Actions/GitLab runner configuration
