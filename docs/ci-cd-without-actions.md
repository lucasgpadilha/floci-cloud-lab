# CI/CD Without GitHub Actions or GitLab Runners

## Constraint

This project must not use GitHub Actions or GitLab runners.

## Local pipeline

The first pipeline is local and reproducible:

```bash
make pipeline
```

It will run docs checks, forbidden CI checks, Terraform checks, Python tests, Floci smoke tests, and local Terraform planning as implementation matures.

## Agentic pipeline

Hermes orchestrates development:

1. Create task file.
2. Create isolated worktree.
3. Dispatch Codex for implementation.
4. Run `make check` and targeted tests.
5. Run `agent-status` and `agent-review`.
6. Ask for human approval before commit/push.

## Floci dogfood pipeline

A later phase can use Floci-emulated CodeBuild:

- `buildspec.yml` defines build steps.
- Floci CodeBuild executes them locally through Docker.
- Artifacts can go to emulated S3.
- Logs can go to emulated CloudWatch Logs.

This demonstrates AWS-style CI/CD without using GitHub Actions, GitLab runners, or real AWS.
