# Portfolio Walkthrough

This document frames Floci Cloud Lab as an interview story: what problem it solves, what it proves, how it is built, and what should be expanded next.

## 30-second pitch

Floci Cloud Lab is a local-first AWS learning lab. It uses the Floci AWS emulator at `http://localhost:4566` so I can design, validate, test, and document AWS-shaped architectures without a paid AWS account or accidental cloud spend.

The goal is not to deploy this repository to AWS by default. The goal is to prove cloud engineering habits locally: Infrastructure as Code, serverless-style application design, test automation, local pipelines, observability thinking, and safety guardrails.

## Problem

Learning AWS deeply usually requires either:

- paying for real cloud resources;
- using toy examples that do not exercise real engineering workflows;
- or relying on diagrams without runnable validation.

This project takes a different path: build a portfolio-quality lab that behaves like an AWS project, but runs locally and safely.

## Architecture story

The current baseline has four layers:

1. Local emulator layer
   - Floci runs through Docker Compose.
   - AWS-shaped API traffic targets `http://localhost:4566`.
   - Credentials are fake local values: `test`/`test`.

2. Infrastructure layer
   - Terraform defines local resources.
   - Provider endpoint overrides keep operations pointed at Floci.
   - Validation targets include formatting, init, validate, plan, and drift checks.

3. Application layer
   - A Python Lambda-style handler exposes object APIs.
   - The handler stores object content through S3-compatible APIs.
   - Metadata is stored through DynamoDB-compatible APIs.
   - A local HTTP adapter lets the app be tested from a browser without deploying API Gateway.

4. Portfolio evidence layer
   - Makefile targets provide repeatable commands.
   - Tests validate unit and integration behavior.
   - DevOps audit checks guardrails, Docker Compose config, shell syntax, and drift.
   - Evidence documents capture sanitized validation output.

## What I would highlight in an interview

### Local-first cloud discipline

This project shows how to learn and validate cloud patterns while minimizing risk and cost. Every default is local-only, and the repo documents the boundary clearly.

### Terraform with endpoint control

The Terraform environment is configured for emulator-backed validation. This demonstrates provider configuration, module boundaries, resource modeling, and drift awareness without mutating real AWS.

### Serverless-style design

The API is written as a Lambda-style handler so the core application logic stays close to AWS serverless patterns even while the runtime is local.

### Data integration testing

The app path exercises object storage and metadata persistence through boto3, which is closer to real AWS client behavior than pure mocks.

### DevOps and safety

The repo intentionally avoids GitHub Actions and GitLab runners for this phase. Instead, it uses local quality gates to demonstrate CI/CD thinking without adding external runners or cloud-side automation.

## Current implemented path

A reviewer can currently run:

```bash
make floci-up
make floci-health
make check
make terraform-plan-local
make app-demo
```

The expected result is a local Floci-backed demo that validates docs, guardrails, Terraform, Python tests, and application behavior without real AWS credentials.

## Design decisions

- Static frontend first: keeps the portfolio demo easy to inspect and avoids premature framework complexity.
- Lambda-style handler first: keeps migration to real Lambda/API Gateway conceptually straightforward later.
- Local evidence files: makes validation reproducible for reviewers.
- Explicit forbidden CI guardrails: prevents accidental addition of GitHub Actions/GitLab runner config while the project goal is local validation.
- Fake local credentials only: reinforces that the default path is not intended for production or real AWS accounts.

## Known boundaries

- Floci compatibility determines which AWS APIs can be validated locally.
- Local emulation does not prove AWS production readiness by itself.
- Real AWS deployment templates, if added later, should remain optional and clearly separated from the default local path.
- `terraform apply` should remain a local-only action guarded by endpoint checks.

## Next increments

The roadmap in `docs/plans/aws-proficiency-roadmap.md` expands the lab through IAM/security, API Gateway/Lambda shape, DynamoDB depth, S3 depth, event-driven architecture, workflows, observability, resilience, networking, containers, local CI/CD, governance, and cost engineering.

The immediate next portfolio increment after this polish phase should be one of:

1. IAM and policy modeling with explicit local/real-AWS boundaries.
2. API Gateway/Lambda parity documentation and tests.
3. Richer evidence capture with screenshots/log excerpts for the app demo.

## How to review this repository

1. Start with `README.md`.
2. Run the 5-command quick demo.
3. Inspect `docs/architecture.md` and `docs/floci-local-workflow.md`.
4. Review `evidence/README.md` and `evidence/portfolio-walkthrough.md`.
5. Use `docs/plans/aws-proficiency-roadmap.md` to understand where the project is going.
