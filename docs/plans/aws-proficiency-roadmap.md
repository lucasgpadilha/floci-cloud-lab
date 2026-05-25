# AWS Proficiency Roadmap Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Turn Floci Cloud Lab into a portfolio-grade AWS proficiency lab that demonstrates practical skill across core AWS domains while staying local-first and cost-free by default.

**Architecture:** The product is this portfolio lab repo. Floci is the local AWS-compatible platform used to validate AWS-shaped architecture at `http://localhost:4566`; it is not the app being deployed. Every phase must prefer local emulator resources, fake credentials, reproducible tests, docs, and evidence artifacts. Real AWS deployment is optional, future-only, and requires explicit approval.

**Tech Stack:** Floci, Docker Compose, Terraform, Python, boto3, pytest, Makefile, shell scripts, static frontend, local evidence docs. Optional future additions: SAM/CDK examples, OPA/Checkov/tfsec, OpenTelemetry-style instrumentation, containerized workers, real-AWS migration templates.

**Forbidden by default:** real AWS credentials, real AWS endpoints, GitHub Actions, GitLab runners, unapproved Terraform apply, committed tfstate, committed secrets.

**Updated:** 2026-05-24T22:12:49-03:00

---

## Definition of AWS proficient for this repo

This project should show that the owner can:

1. Design AWS architectures and explain service trade-offs.
2. Build infrastructure with Terraform modules and environment separation.
3. Use IAM concepts safely: identity, roles, policies, least privilege, and guardrails.
4. Build serverless APIs with Lambda-style handlers, API Gateway-style routing, DynamoDB, S3, queues, events, and workflows.
5. Operate workloads with logging, metrics, alarms, traces, runbooks, incident drills, backup/restore, and drift detection.
6. Secure cloud workloads with encryption, secret handling, policy scanning, endpoint safety, and threat-model docs.
7. Automate local CI/CD without GitHub Actions/GitLab runners, including quality gates and evidence capture.
8. Understand cost drivers and map local resources to real AWS billing implications.
9. Test cloud systems through unit, integration, smoke, contract, failure, and idempotency tests.
10. Communicate clearly with diagrams, ADRs, READMEs, evidence, and demos.

---

## Current baseline

Already implemented:

- Local Floci startup through Docker Compose.
- Terraform local environment targeting `http://localhost:4566`.
- S3-compatible object bucket.
- DynamoDB-compatible metadata table.
- CloudWatch-compatible log group.
- Python Lambda-style API handler.
- Local HTTP adapter and static frontend.
- Unit, smoke, and integration tests.
- DevOps audit with endpoint guardrails, forbidden CI checks, shell syntax, Compose validation, Terraform validation, drift detection, and full tests.
- Evidence docs for local apply and app demo.

Primary repo paths:

- Worktree used for implementation: `/home/lucas/agentic/runs/floci-cloud-lab-codex`
- Repository URL: `https://github.com/lucasgpadilha/floci-cloud-lab`

---

## Competency roadmap overview

| Phase | AWS competency | Portfolio outcome | Local-first validation |
| --- | --- | --- | --- |
| 1 | Repository polish | Clear public portfolio story | README/docs/evidence pass review |
| 2 | IAM and security foundations | Least-privilege design and guardrails | Policy docs/tests/static scans |
| 3 | API Gateway + Lambda patterns | Production-shaped serverless API | Local adapter + contract tests |
| 4 | DynamoDB proficiency | Data modeling, indexes, TTL, conditional writes | boto3 integration tests |
| 5 | S3 proficiency | Object lifecycle, versioning, presigned URLs, events | emulator smoke/integration tests |
| 6 | Event-driven architecture | SQS/SNS/EventBridge-style async workflows | local queue/event tests or documented emulator gaps |
| 7 | Step Functions/workflows | Orchestration, retries, compensation | local workflow simulator if Floci lacks support |
| 8 | Observability | Logs, metrics, alarms, dashboards, tracing docs | generated logs/metrics/evidence |
| 9 | Resilience and operations | Backup/restore, failure drills, idempotency, runbooks | scripted drills and tests |
| 10 | Network/VPC concepts | VPC, private/public subnet, endpoints explained | Terraform templates/docs, no real provisioning |
| 11 | Containers | ECS/Fargate-shaped worker pattern | local container worker and docs |
| 12 | CI/CD without forbidden runners | Local pipeline, release gates, agentic workflow | `make pipeline` and evidence capture |
| 13 | Compliance and governance | Tagging, policy-as-code, audit artifacts | static checks and docs |
| 14 | Cost engineering | Cost model and optimization playbook | cost docs and estimation worksheet |
| 15 | Optional real AWS migration | Safe path from local to cloud | templates only until explicit approval |

---

## Phase 1: Repository polish and portfolio narrative

**Objective:** Make the repo easy for recruiters/interviewers to understand in 3 minutes.

**Files:**

- Modify: `README.md`
- Modify: `docs/project-status.md`
- Create: `docs/portfolio-walkthrough.md`
- Create: `docs/plans/aws-proficiency-roadmap.md` (this file)
- Create: `evidence/README.md`

**Tasks:**

1. Add a prominent "What this demonstrates" section to `README.md` with bullet points mapped to AWS skills.
2. Add a "Quick demo in 5 commands" section.
3. Add a service matrix: implemented, planned, emulator support, real AWS equivalent.
4. Create `docs/portfolio-walkthrough.md` explaining the project as an interview story.
5. Create `evidence/README.md` listing all evidence artifacts and how to regenerate them.
6. Update `docs/project-status.md` so it reflects that the repo has already been committed and pushed.
7. Run `make check`.
8. Run `make devops-audit`.
9. Capture sanitized output in `evidence/portfolio-walkthrough.md`.

**Acceptance criteria:**

- A reviewer can identify the architecture, safety boundary, AWS skills, and demo path without reading code.
- No stale claim says the repo has not been committed/pushed.
- `make check` and `make devops-audit` pass.

---

## Phase 2: IAM and security foundations

**Objective:** Demonstrate IAM fluency without using real AWS accounts.

**Files:**

- Create: `infra/modules/iam/main.tf`
- Create: `infra/modules/iam/variables.tf`
- Create: `infra/modules/iam/outputs.tf`
- Create: `docs/iam-and-security.md`
- Create: `tests/unit/test_iam_policy_documents.py`
- Modify: `scripts/devops-audit.sh`

**Tasks:**

1. Define Terraform IAM policy documents for app access to only required S3, DynamoDB, CloudWatch, and future queue resources.
2. Add explicit deny examples for dangerous actions as educational docs, not necessarily enforced locally if emulator support is limited.
3. Add unit tests that parse generated policy JSON and assert no wildcard actions/resources unless justified.
4. Document IAM concepts: users vs roles, trust policies, permission policies, least privilege, policy evaluation, explicit deny.
5. Add devops audit checks for wildcard IAM policies.
6. Add a threat model covering accidental real AWS use, leaked local env files, public bucket risks, overbroad IAM, and untrusted uploads.

**Acceptance criteria:**

- IAM policies are generated or documented as JSON.
- Tests fail on `Action: "*"` or `Resource: "*"` unless a narrow allowlist comment exists.
- Security docs explain how the local design would translate to real AWS.

---

## Phase 3: API Gateway + Lambda proficiency

**Objective:** Evolve the current local HTTP adapter into a production-shaped serverless API design.

**Files:**

- Modify: `app/backend/functions/api.py`
- Modify: `app/backend/local_server.py`
- Create: `app/backend/functions/auth.py`
- Create: `app/backend/functions/errors.py`
- Create: `docs/api-gateway-lambda.md`
- Create: `tests/contract/test_api_contract.py`
- Modify: `app/frontend/index.html`

**Tasks:**

1. Define an OpenAPI document for `/health`, `/objects`, `/objects/{id}`, and future async endpoints.
2. Add consistent response envelopes and error mapping.
3. Add request validation for content type, size, and required fields.
4. Add CORS behavior matching API Gateway expectations.
5. Add Lambda event fixtures for HTTP API v2.
6. Add contract tests that call handlers using API Gateway-style events.
7. Add docs comparing API Gateway REST API vs HTTP API, stages, CORS, throttling, and authorizers.
8. Add frontend display for request IDs and error responses.

**Acceptance criteria:**

- Contract tests prove the handler behaves like a Lambda behind API Gateway.
- Docs explain how this would be wired with API Gateway in real AWS.
- Local server remains a thin adapter, not a separate business logic implementation.

---

## Phase 4: DynamoDB proficiency

**Objective:** Show data modeling, access patterns, indexes, conditional writes, pagination, and TTL.

**Files:**

- Modify: `infra/modules/database/main.tf`
- Modify: `app/backend/functions/repository.py`
- Create: `docs/dynamodb-data-model.md`
- Create: `tests/unit/test_dynamodb_model.py`
- Modify: `tests/integration/test_app_floci_integration.py`

**Tasks:**

1. Document access patterns: create object, get object by id, list recent objects, query by owner/category, soft delete, TTL cleanup.
2. Add table attributes and a GSI if Floci supports it; otherwise document the gap and simulate at repository level.
3. Add conditional writes to prevent accidental overwrite.
4. Add optimistic concurrency with a `version` attribute.
5. Add pagination support to `GET /objects`.
6. Add TTL field to records and docs for lifecycle behavior.
7. Add tests for conditional write failure, pagination, and version increments.
8. Add docs explaining partition keys, sort keys, hot partitions, GSIs, LSIs, capacity modes, and single-table design trade-offs.

**Acceptance criteria:**

- Tests verify at least one conditional-write scenario.
- Docs clearly connect the chosen table design to access patterns.
- Emulator support gaps are documented rather than hidden.

---

## Phase 5: S3 proficiency

**Objective:** Demonstrate object storage patterns beyond basic put/get.

**Files:**

- Modify: `infra/modules/object-storage/main.tf`
- Modify: `app/backend/functions/repository.py`
- Create: `app/backend/functions/storage.py`
- Create: `docs/s3-object-storage.md`
- Create: `tests/integration/test_s3_patterns.py`

**Tasks:**

1. Add object key naming conventions.
2. Add content-type and metadata persistence.
3. Add object versioning evidence if supported.
4. Add presigned URL generation locally if supported by boto3 + Floci.
5. Add multipart upload docs, even if not implemented.
6. Add lifecycle policy examples as Terraform or docs, depending on emulator support.
7. Add object integrity checks with SHA-256 metadata.
8. Add tests for content-type, metadata, and retrieval integrity.
9. Add docs covering bucket policies, encryption, public access block, lifecycle, replication, events, and cost drivers.

**Acceptance criteria:**

- Upload and download preserve metadata and integrity hash.
- S3 docs distinguish implemented local behavior from real AWS features.

---

## Phase 6: Event-driven architecture: SQS, SNS, EventBridge

**Objective:** Add asynchronous processing patterns.

**Files:**

- Create: `infra/modules/events/main.tf`
- Create: `infra/modules/events/variables.tf`
- Create: `infra/modules/events/outputs.tf`
- Create: `app/backend/functions/events.py`
- Create: `app/backend/functions/worker.py`
- Create: `scripts/worker-once.sh`
- Create: `docs/event-driven-architecture.md`
- Create: `tests/integration/test_event_flow.py`

**Tasks:**

1. Add Terraform for an SQS-style queue if Floci supports SQS.
2. Add an async endpoint such as `POST /objects/{id}/process` that enqueues a job.
3. Add a worker that reads one message, processes it idempotently, and updates DynamoDB metadata.
4. Add dead-letter queue design docs.
5. Add retry/backoff behavior in the worker.
6. Add idempotency keys.
7. Add docs comparing SQS, SNS, EventBridge, Kinesis, and when to use each.
8. If Floci lacks a service, create a local simulator wrapper and document the emulator gap.

**Acceptance criteria:**

- A local command can enqueue and process a job.
- Tests prove idempotent message processing.
- Docs explain retries, DLQs, visibility timeout, fanout, and event schemas.

---

## Phase 7: Step Functions/workflow orchestration

**Objective:** Demonstrate orchestration, retries, branches, and compensation.

**Files:**

- Create: `app/workflows/object_processing.json`
- Create: `app/workflows/local_runner.py`
- Create: `docs/step-functions-workflows.md`
- Create: `tests/unit/test_workflow_runner.py`

**Tasks:**

1. Define a simple Amazon States Language workflow for validate -> process -> persist -> notify.
2. Add a local runner if Step Functions is unsupported in Floci.
3. Implement retry and catch semantics in the local runner only as much as needed for the demo.
4. Add tests for success path, validation failure, retryable failure, and compensation path.
5. Document Standard vs Express workflows and cost/reliability trade-offs.

**Acceptance criteria:**

- Workflow file is valid JSON and documented.
- Tests prove branching and retry semantics.
- Docs explain what is local simulation vs AWS-native behavior.

---

## Phase 8: Observability

**Objective:** Show operational maturity: logs, metrics, alarms, dashboards, and traces.

**Files:**

- Modify: `infra/modules/observability/main.tf`
- Create: `app/backend/functions/observability.py`
- Create: `docs/observability-deep-dive.md`
- Create: `evidence/observability-demo.md`
- Create: `tests/unit/test_observability.py`

**Tasks:**

1. Add structured JSON logging with request ID, route, status, latency, object ID, and error code.
2. Add custom metrics abstraction for counts and latency.
3. Add alarm definitions as Terraform or documented templates depending on emulator support.
4. Add dashboard JSON template.
5. Add tracing propagation fields and docs for X-Ray/OpenTelemetry concepts.
6. Add a script that runs demo requests and captures logs/metrics output.
7. Add tests asserting logs contain required fields without secrets.

**Acceptance criteria:**

- Demo evidence shows structured logs from a real local request.
- Tests verify no secret-looking values appear in logs.
- Docs explain CloudWatch Logs, Metrics, Alarms, Dashboards, X-Ray, and operational KPIs.

---

## Phase 9: Resilience, backup, restore, and incident operations

**Objective:** Demonstrate how to run and recover the system.

**Files:**

- Create: `scripts/backup-local.sh`
- Create: `scripts/restore-local.sh`
- Create: `scripts/chaos-drill.sh`
- Create: `docs/incident-response.md`
- Create: `docs/backup-restore.md`
- Create: `tests/integration/test_backup_restore.py`

**Tasks:**

1. Add local backup export for DynamoDB records and S3 object metadata/content.
2. Add local restore script.
3. Add an incident drill: stop Floci, verify failure mode, restart, re-run health, verify data.
4. Add idempotent retry behavior to app/repository where appropriate.
5. Add runbook sections for common incidents: emulator down, drift, failed apply, object missing, data corruption.
6. Add RTO/RPO definitions for the learning lab.

**Acceptance criteria:**

- Backup/restore test proves data round-trip locally.
- Incident docs include symptoms, diagnosis commands, remediation, and prevention.

---

## Phase 10: Network/VPC concepts

**Objective:** Demonstrate networking knowledge even if the local emulator cannot create real VPC networking.

**Files:**

- Create: `infra/envs/dev-template/network.tf`
- Create: `infra/modules/networking/main.tf`
- Create: `infra/modules/networking/variables.tf`
- Create: `infra/modules/networking/outputs.tf`
- Create: `docs/networking-vpc.md`
- Create: `docs/diagrams/networking.svg` or `docs/diagrams/networking.md`

**Tasks:**

1. Add Terraform templates for VPC, public/private subnets, route tables, NAT Gateway, VPC endpoints, and security groups as documentation/template only.
2. Do not apply these templates locally unless explicitly supported and safe.
3. Document DNS, security groups vs NACLs, NAT, internet gateway, private endpoints, and VPC flow logs.
4. Add architecture diagram showing public API edge, private compute/data plane, endpoints, and logs.
5. Add tests or static checks that networking templates have tags and no `0.0.0.0/0` ingress except documented HTTP/HTTPS examples.

**Acceptance criteria:**

- Networking templates are clearly marked as real-AWS migration templates, not local Floci resources.
- Docs explain how the current local architecture maps to a real VPC deployment.

---

## Phase 11: Containers and ECS/Fargate-shaped workloads

**Objective:** Add a containerized worker pattern to show non-serverless compute knowledge.

**Files:**

- Create: `app/worker/Dockerfile`
- Create: `app/worker/main.py`
- Modify: `compose.yaml`
- Create: `docs/containers-ecs-fargate.md`
- Create: `tests/integration/test_worker_container.py`

**Tasks:**

1. Package the async worker as a Docker image.
2. Add local Compose service for the worker.
3. Add health checks and structured logs.
4. Document how the worker would map to ECS/Fargate, task definitions, services, autoscaling, IAM task roles, and CloudWatch logs.
5. Add local integration test that starts the worker or runs it once against a queued message.

**Acceptance criteria:**

- Worker can run locally and process one job.
- Docs explain Lambda vs ECS/Fargate trade-offs.

---

## Phase 12: CI/CD without GitHub Actions or GitLab runners

**Objective:** Demonstrate delivery automation while honoring the no-hosted-runner constraint.

**Files:**

- Modify: `Makefile`
- Modify: `scripts/devops-audit.sh`
- Create: `scripts/capture-evidence.sh`
- Create: `docs/release-process.md`
- Create: `docs/agentic-delivery-workflow.md`
- Create: `evidence/pipeline-latest.md`

**Tasks:**

1. Expand `make pipeline` to run all safe checks in deterministic order.
2. Add `make evidence` to capture sanitized command output.
3. Add release checklist with human approval gates.
4. Add local semantic version tagging docs, but do not tag without approval.
5. Add guard that fails if `.github/workflows/` or `.gitlab-ci.yml` appears.
6. Document the Hermes/agentic workflow: task file, isolated worktree, dispatch, review, approval, commit/push.
7. Add optional CodeBuild-style local emulation plan if Floci supports relevant APIs.

**Acceptance criteria:**

- `make pipeline` is the canonical local CI command.
- Evidence file can be regenerated.
- Forbidden hosted CI config remains absent.

---

## Phase 13: Compliance, governance, and policy-as-code

**Objective:** Show governance practices expected in AWS environments.

**Files:**

- Create: `policy/terraform.rego` or `policy/cloud-guardrails.py`
- Create: `docs/governance.md`
- Modify: `scripts/devops-audit.sh`
- Create: `tests/unit/test_governance_policy.py`

**Tasks:**

1. Add tagging standard: Project, Environment, Owner, ManagedBy, CostCenter.
2. Add static check for required tags in Terraform resources.
3. Add checks for no public S3 access, no real AWS endpoints, no committed secrets, no broad IAM wildcards.
4. Add docs for AWS Organizations, SCPs, Config, CloudTrail, Security Hub, GuardDuty, and IAM Access Analyzer.
5. Add an audit evidence template.

**Acceptance criteria:**

- DevOps audit fails if required tags are missing.
- Governance docs explain which controls are implemented locally vs conceptual for real AWS.

---

## Phase 14: Cost engineering and Well-Architected review

**Objective:** Demonstrate AWS cost awareness and architecture review skills.

**Files:**

- Modify: `docs/cost-learning.md`
- Create: `docs/well-architected-review.md`
- Create: `docs/cost-model.md`
- Create: `scripts/cost-model.py`
- Create: `tests/unit/test_cost_model.py`

**Tasks:**

1. Create a simple cost model for real AWS equivalents: Lambda requests/duration, API Gateway requests, DynamoDB read/write/storage, S3 storage/requests, CloudWatch logs, NAT Gateway risk.
2. Add examples showing why local Floci avoids spend.
3. Add Well-Architected review across operational excellence, security, reliability, performance efficiency, cost optimization, and sustainability.
4. Add optimization notes: DynamoDB on-demand vs provisioned, log retention, S3 lifecycle, avoiding NAT costs, right-sizing Lambda memory.
5. Add a small Python calculator with tests.

**Acceptance criteria:**

- Docs show what would cost money in real AWS and how to control it.
- Cost calculator has unit tests and sample output.

---

## Phase 15: Optional real AWS migration templates

**Objective:** Provide a safe future path to real AWS without making real AWS the default.

**Files:**

- Create: `infra/envs/dev-template/providers.tf`
- Create: `infra/envs/dev-template/main.tf`
- Create: `infra/envs/prod-template/providers.tf`
- Create: `infra/envs/prod-template/main.tf`
- Create: `docs/real-aws-migration.md`
- Create: `docs/real-aws-safety-checklist.md`

**Tasks:**

1. Add template provider config for real AWS with no credentials committed.
2. Add remote state design docs, but do not configure a real backend without approval.
3. Add migration checklist: account setup, MFA, budget alarm, least-privilege role, backend bucket, state lock, plan review, approval, apply.
4. Add destructive-operation checklist.
5. Add docs for promoting from local -> dev -> prod.
6. Keep real apply commands documentation-only unless the user explicitly approves a real AWS run.

**Acceptance criteria:**

- Templates make migration understandable but safe.
- Default commands still only target Floci/local.

---

## Cross-cutting quality gates for every phase

Every phase must pass:

```bash
make check
make devops-audit
make terraform-plan-local
```

When the phase touches app behavior, also run:

```bash
make app-demo
```

When the phase touches Floci resources, also run:

```bash
make floci-health
make floci-smoke
```

Before any commit/push:

```bash
git status --short
git diff --check
git diff --cached --name-only
```

Guardrails:

- Do not commit `.venv/`, `.terraform/`, `*.tfstate`, `.env`, `.env.local`, caches, or secret files.
- Do not add `.github/workflows/` or `.gitlab-ci.yml`.
- Do not run real AWS commands.
- Do not use real AWS credentials.
- Do not commit, push, merge, rebase, or tag without explicit human approval.

---

## Suggested implementation order

1. Phase 1: repository polish.
2. Phase 2: IAM/security foundations.
3. Phase 3: API Gateway/Lambda contract.
4. Phase 4: DynamoDB depth.
5. Phase 5: S3 depth.
6. Phase 6: event-driven flow.
7. Phase 8: observability.
8. Phase 9: resilience/operations.
9. Phase 12: CI/CD and evidence capture.
10. Phase 13: governance.
11. Phase 14: cost/Well-Architected.
12. Phase 10: networking templates.
13. Phase 11: containers.
14. Phase 7: workflow orchestration.
15. Phase 15: optional real AWS migration templates.

Reasoning: build visible portfolio value first, deepen the already implemented services next, then add async/ops/governance/cost, and only then expand into templates or optional real-AWS paths.

---

## Interview story this roadmap should support

After completing most phases, the portfolio story should be:

> I built a local-first AWS cloud lab using Floci, Terraform, Python, and boto3. It provisions AWS-shaped infrastructure locally, runs a Lambda-style API over S3 and DynamoDB, includes event-driven processing, observability, security guardrails, drift detection, policy checks, backup/restore drills, and a local CI pipeline. The project avoids real AWS spend by default, but the docs explain exactly how each local pattern maps to production AWS services.

---

## Backlog labels

Use these labels in future task files or issues:

- `aws-foundation`
- `iam-security`
- `serverless-api`
- `dynamodb`
- `s3`
- `event-driven`
- `observability`
- `resilience`
- `networking`
- `containers`
- `ci-cd-local`
- `governance`
- `cost-optimization`
- `well-architected`
- `real-aws-optional`

---

## Next recommended task

Start with Phase 1 because it converts the existing work into a stronger public portfolio without large technical risk.

First task file to create in the agentic control plane:

```text
/home/lucas/agentic/tasks/floci-cloud-lab-phase1-portfolio-polish.md
```

Recommended prompt:

```text
Polish Floci Cloud Lab as a public AWS proficiency portfolio repo. Work in an isolated worktree. Implement Phase 1 from docs/plans/aws-proficiency-roadmap.md only. Do not commit, push, merge, rebase, tag, add GitHub Actions/GitLab CI, or run real AWS commands. Run make check, make devops-audit, and make terraform-plan-local. Return changed files and verification output.
```
