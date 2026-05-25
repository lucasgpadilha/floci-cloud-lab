# Floci Cloud Lab

A personal AWS learning and portfolio project that uses [Floci](https://github.com/floci-io/floci), a free local AWS emulator, to validate cloud architectures without an AWS account, auth token, feature gates, or cloud costs.

This repository is not the Floci emulator itself. It is a hands-on lab that runs AWS-shaped infrastructure and tests against Floci at `http://localhost:4566`.

## Goals

- Learn AWS by using familiar AWS APIs locally.
- Build a portfolio-quality cloud engineering project without AWS spend.
- Validate Terraform infrastructure against a local AWS-compatible endpoint.
- Test S3, DynamoDB, Lambda, API Gateway v2, Cognito, IAM/STS, CloudWatch, and eventing patterns where supported by Floci.
- Demonstrate CI/CD thinking without GitHub Actions or GitLab runners.
- Produce clear docs, runbooks, ADRs, and evidence artifacts.

## Chosen stack

- AWS emulator: Floci via Docker Compose.
- IaC: Terraform.
- Backend/tests: Python, boto3, pytest.
- Frontend: static HTML first, React/Vite optional later.
- Pipeline: Makefile local pipeline + Hermes agentic workflow + future Floci-emulated CodeBuild dogfood.

## Quick start

Start Floci:

```bash
make floci-up
make floci-health
```

Initialize and validate the local Terraform environment:

```bash
make check
make terraform-plan-local
```

The local resources have already been designed to target only:

```text
http://localhost:4566
```

After an approved local apply, exercise the app API:

```bash
make app-demo
```

Run the local HTTP adapter for the static frontend:

```bash
make app-api-local
```

Then open:

```text
app/frontend/index.html
```

## Safety

Default workflows must not create real AWS resources. Local credentials in this repo are fake development values for Floci only.

Do not use:

- GitHub Actions
- GitLab runners
- real AWS credentials
- real AWS endpoints by default
- `terraform apply` against real AWS

## Project status

Current phase: local app demo implemented on top of the Floci-backed Terraform baseline.

Implemented locally:

- Terraform-managed S3-compatible object bucket.
- Terraform-managed DynamoDB-compatible metadata table.
- Terraform-managed CloudWatch-compatible app log group.
- Python Lambda-style API handler with `/health`, `POST /objects`, `GET /objects`, and `GET /objects/{id}`.
- Static frontend in `app/frontend/index.html`.
- Local HTTP adapter via `make app-api-local`.
- CLI demo via `make app-demo`.
- DevOps audit via `make devops-audit` for drift detection, Compose validation, shell syntax, forbidden CI guardrails, and local-only endpoint checks.
