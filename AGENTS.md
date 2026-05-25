# Agent Instructions for Floci Cloud Lab

## Project intent

This is a personal portfolio lab that uses the Floci AWS emulator locally to learn, validate, and test AWS architectures without cloud cost.

Do not treat this as the Floci emulator source repository and do not treat it as a project that deploys to real AWS by default.

## Agent roles

- Hermes: orchestration, backlog, documentation, review, and approval gates.
- Codex: implementation in isolated worktrees.
- Antigravity: only if work becomes too large or multi-step complex.
- Kiro: architecture/specs if installed later; currently optional.

## Critical constraints

Never do these without explicit human approval:

- Commit, push, merge, or rebase.
- Create or mutate real AWS resources.
- Use real AWS credentials or profiles.
- Edit `~/.aws`, `~/.ssh`, `~/.kube`, or real `.env` secret files.
- Add GitHub Actions workflows.
- Add GitLab runner configuration.

## Allowed local actions

- Edit files in this repository/worktree.
- Run Docker Compose for Floci.
- Run Terraform commands against the local Floci endpoint only.
- Use fake local credentials such as `test`/`test`.
- Run Python tests and smoke tests against Floci.

## Architecture defaults

- Floci endpoint: `http://localhost:4566`.
- Region: `us-east-1`.
- Access key: `test`.
- Secret key: `test`.
- IaC: Terraform.
- Local state for the lab environment.

## Validation expectation

Before handoff, run available safe checks:

- `make check`
- `git status --short`
- `agent-status`
- `agent-review`

If a tool is missing, record it as skipped with the reason.
