# Project Status

Updated: 2026-05-24T21:40:10-03:00

## Current status

The local Floci Cloud Lab baseline is created in the isolated worktree:

`/home/lucas/agentic/runs/floci-cloud-lab-codex`

The primary repo checkout remains at:

`/home/lucas/projects/floci-cloud-lab`

No commit, push, merge, rebase, or real AWS mutation has been performed.

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
- Full Python test suite: `12 passed`
- Terraform validate: passed
- Terraform apply: `4 added, 0 changed, 0 destroyed`
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

Recommended next phase:

1. Implement the minimal backend application.
2. Add local app tests beyond smoke tests.
3. Add optional local API/Lambda emulation if Floci compatibility is sufficient.
4. Add richer evidence capture for portfolio screenshots/logs.
5. Decide whether to copy or merge the isolated worktree result into the primary checkout after human review.

## Human approval still required

Before doing any of the following, get explicit approval:

- Commit
- Push
- Merge/rebase
- Any real AWS command or resource mutation
- Any GitHub Actions/GitLab runner configuration
