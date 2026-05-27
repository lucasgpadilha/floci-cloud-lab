# Floci Cloud Lab

A personal AWS learning and portfolio project that uses [Floci](https://github.com/floci-io/floci), a free local AWS emulator, to validate cloud architectures without an AWS account, auth token, feature gates, or cloud costs.

This repository is not the Floci emulator itself. It is a hands-on lab that runs AWS-shaped infrastructure and tests against Floci at `http://localhost:4566`.

## What this demonstrates

This project is designed to be understandable in a 3-minute portfolio review and deep enough for a technical interview.

- Local cloud engineering: AWS-shaped services exercised through a local emulator instead of a paid cloud account.
- Infrastructure as Code: Terraform modules, local environment wiring, provider endpoint overrides, validation, and plan/drift checks.
- Serverless application design: Lambda-style Python handler, API routes, object metadata, and a local HTTP adapter for browser testing.
- Data services: S3-compatible object storage with versioning, content-type/metadata preservation, SHA-256 integrity checks, presigned URL evidence, DynamoDB-compatible metadata persistence, conditional writes, pagination, TTL modeling, and service integration tests.
- DevOps discipline: Makefile pipeline, shell checks, Docker Compose validation, local-only endpoint guardrails, and evidence artifacts.
- Resilience/operations discipline: backup manifest modeling, restore sequencing, failure-injection taxonomy, and idempotent replay drills.
- Orchestration discipline: Step Functions-style workflow modeling, retries, catch branches, compensation plans, and idempotency evidence.
- Container discipline: local Docker image, Compose app service, `/health` healthcheck, and ECS/Fargate mapping without ECR/ECS deployment.
- Kubernetes platform discipline: portable manifests for namespace, service account, deployment, service, HPA, and network policy with EKS vs OKE comparison notes.
- Security and cost awareness: fake local credentials, no default real AWS endpoints, no GitHub Actions/GitLab runners, and no cloud spend by default.
- Documentation quality: architecture notes, runbook, status tracking, roadmap, and interview-oriented walkthroughs.

## Quick demo in 5 commands

From this repository/worktree:

```bash
make floci-up
make floci-health
make check
make terraform-plan-local
make app-demo
```

Optional browser demo:

```bash
make app-api-local
```

Then open:

```text
app/frontend/index.html
```

The local resources target only:

```text
http://localhost:4566
```

## Service matrix

| Capability | Status in this repo | Floci/local support used | Real AWS equivalent |
| --- | --- | --- | --- |
| Object storage | Implemented with Phase 5 S3 polish | S3-compatible bucket, versioning, content type/metadata preservation, SHA-256 integrity metadata, and presigned URL generation | Amazon S3 |
| Metadata store | Implemented with Phase 4 data-model polish | DynamoDB-compatible table operations, conditional writes, category index fields, pagination, version, and TTL modeling | Amazon DynamoDB |
| App logging baseline | Implemented | CloudWatch-compatible log group IaC | Amazon CloudWatch Logs |
| Lambda-style API | Implemented locally | Python handler and local adapter | AWS Lambda |
| HTTP API surface | Implemented with HTTP API v2 contract tests and OpenAPI docs | Local HTTP adapter for `/health` and object routes | Amazon API Gateway HTTP API |
| Infrastructure validation | Implemented | Terraform against local endpoint | Terraform AWS provider targeting AWS |
| DevOps audit | Implemented | Local-only checks, Compose validation, drift check | CI/CD quality gates |
| IAM/security modeling | Implemented as policy documents, tests, and docs | Local JSON/Terraform module validation; no real IAM mutation | AWS IAM roles, trust policies, permission policies, IAM Access Analyzer |
| Event-driven workflows | Implemented with Phase 6 outbox pattern | DynamoDB-compatible outbox/event log, `GET /events`, and idempotent `POST /events/process` local worker | SQS, SNS, EventBridge, Lambda event source mappings |
| Orchestration workflows | Implemented with Phase 9 local simulation | Step Functions-style state machine, retry/catch modeling, compensation plans, deterministic execution history | AWS Step Functions, Lambda tasks, EventBridge/SQS, CloudWatch/X-Ray |
| Containers | Implemented with Phase 10 local workflow | Dockerfile, Compose app service, container healthcheck, local build/run demo, static config tests | ECS/Fargate, ECR, ALB target groups, CloudWatch Logs |
| Kubernetes platform baseline | Implemented with Phase 11 local/reference workflow | Portable Kubernetes manifests and static validation for namespace, service account, deployment, service, HPA, and network policy | EKS clusters, managed node groups/Fargate profiles, ECR, AWS Load Balancer Controller, CloudWatch Container Insights |
| Observability depth | Implemented with Phase 7 local signals | Structured JSON logs, CloudWatch-style metric records, request/trace correlation, demo evidence, runbook drills | CloudWatch Logs, Metrics, Alarms, Dashboards, X-Ray/OpenTelemetry |
| Resilience/operations | Implemented with Phase 8 local drills | Backup manifest, restore plan, checksum verification, failure-injection taxonomy, idempotent event replay | AWS Backup, S3 version restore, DynamoDB PITR/export, SQS/Lambda idempotency runbooks |

## Chosen stack

- AWS emulator: Floci via Docker Compose.
- IaC: Terraform.
- Backend/tests: Python, boto3, pytest.
- Frontend: static HTML first, React/Vite optional later.
- Pipeline: Makefile local pipeline + Hermes agentic workflow + future Floci-emulated CodeBuild dogfood.

## Safety boundary

Default workflows must not create real AWS resources. Local credentials in this repo are fake development values for Floci only.

Do not use:

- GitHub Actions
- GitLab runners
- real AWS credentials
- real AWS endpoints by default
- `terraform apply` against real AWS

Safe defaults used by the lab:

```text
FLOCI_ENDPOINT=http://localhost:4566
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

## Project status

Current phase: Kubernetes platform baseline for EKS vs OKE comparison is implemented locally in the Phase 11 isolated worktree. Phases 1-10 are already merged on `main`.

Roadmap for becoming AWS-proficient with this project:

```text
docs/plans/aws-proficiency-roadmap.md
```

Portfolio walkthrough:

```text
docs/portfolio-walkthrough.md
```

Evidence index:

```text
evidence/README.md
```

Implemented locally:

- Terraform-managed S3-compatible object bucket with versioning, safe key naming, content-type/metadata preservation, SHA-256 integrity checks, and local presigned URL evidence.
- Terraform-managed DynamoDB-compatible metadata table with owner/object keys, conditional writes, category index fields, pagination, version attributes, and optional TTL fields.
- Terraform-managed CloudWatch-compatible app log group.
- Educational IAM policy documents for app permissions and explicit-deny guardrails, validated without real IAM mutation.
- Python Lambda-style API handler with `/health`, `POST /objects`, `GET /objects`, and `GET /objects/{id}`.
- API Gateway HTTP API v2-shaped contract tests, request IDs, CORS behavior, and OpenAPI documentation.
- Static frontend in `app/frontend/index.html`.
- Local HTTP adapter via `make app-api-local`.
- CLI demo via `make app-demo`.
- DevOps audit via `make devops-audit` for drift detection, Compose validation, shell syntax, forbidden CI guardrails, and local-only endpoint checks.
- Observability demo via `make observability-demo` for structured logs, local metrics, request correlation, and error visibility.
- Resilience drill via `make resilience-drill` for backup manifests, restore ordering, failure taxonomy, and idempotent event replay.
- Orchestration demo via `make orchestration-demo` for Step Functions-style state transitions, retries, catch branches, compensation, and idempotency.
- Container demo via `make app-container-demo` for local image build/run, Compose service health, and ECS/Fargate-ready runtime documentation.
- Kubernetes baseline via `make k8s-validate` for portable manifests and EKS vs OKE comparison documentation without requiring a live cluster.

## Recommended review path

1. Read this README for the 3-minute overview.
2. Read `docs/portfolio-walkthrough.md` for the interview narrative.
3. Read `docs/architecture.md` for the technical shape.
4. Run the 5-command demo above.
5. Review `evidence/README.md` and `evidence/portfolio-walkthrough.md` for reproducible validation output.
