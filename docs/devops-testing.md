# DevOps Testing

This project is intentionally local-first, so the DevOps validation strategy focuses on proving cloud engineering practices without real AWS spend.

## Main command

Run the full DevOps audit:

```bash
make devops-audit
```

The audit runs:

1. Forbidden CI guard
   - fails if `.github/workflows` exists
   - fails if GitLab runner config exists

2. Real AWS endpoint guard
   - fails if operational files contain `amazonaws.com`
   - fails if operational files contain AWS access-key shaped values such as `AKIA...`
   - requires explicit local Floci endpoint usage

3. Shell syntax checks
   - runs `bash -n` for every `scripts/*.sh`

4. Docker Compose validation
   - runs `docker compose config --quiet`

5. Terraform validation and drift detection
   - runs `terraform fmt -check`
   - runs `terraform init -backend=false`
   - runs `terraform validate`
   - runs `terraform plan -detailed-exitcode -no-color`
   - exit code `0` means no drift
   - exit code `2` means drift/change detected and the audit fails

6. Python tests
   - runs the full pytest suite

## Individual targets

```bash
make compose-validate
make shell-check
make terraform-drift-check
make devops-audit
```

## Why this matters for portfolio reviewers

These checks demonstrate practical DevOps habits:

- deterministic local pipelines
- drift detection
- infrastructure validation before mutation
- CI policy enforcement
- script hygiene
- local cloud-emulator safety guardrails
- repeatable evidence generation

## What this does not do

The audit does not:

- create real AWS resources
- use real AWS credentials
- run GitHub Actions or GitLab runners
- commit, push, merge, or deploy anything

## Current validation result

Latest local run:

```text
make devops-audit
12 passed
terraform plan has no drift
local-only DevOps audit passed
```
