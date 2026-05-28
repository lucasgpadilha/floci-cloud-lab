# Agentic Delivery Workflow

This project uses Hermes/agentic delivery as a local review workflow around isolated Git worktrees. The goal is to get repeatable implementation evidence without letting an agent mutate release history or cloud resources without human approval.

## Workflow stages

1. Task definition
   - A human writes a task file under the agentic task directory.
   - The task defines the branch, isolated worktree, allowed files, validation commands, and forbidden actions.

2. Isolated worktree
   - Work happens in a dedicated worktree under `/home/lucas/agentic/runs/`.
   - The primary checkout remains separate for review and comparison.

3. Dispatch
   - Hermes or a focused subagent receives the task file and branch context.
   - The agent must operate only in the assigned worktree.

4. Implementation
   - The agent edits files, adds tests/docs when appropriate, and keeps the project local-first.
   - The agent must not commit, push, tag, merge, rebase, delete worktrees, run real AWS commands, or run `terraform apply` unless explicitly approved.

5. Validation and evidence
   - The agent runs the requested validations, normally:

```bash
make pipeline
make evidence
make check
git diff --check
git status --short
```

   - `make evidence` writes sanitized output to `evidence/pipeline-latest.md` for reviewer inspection.

6. Review
   - A human or reviewer agent inspects the diff, evidence, tests, and status.
   - Review focuses on safety boundaries, local-only endpoints, forbidden CI config, deterministic pipeline behavior, and documentation accuracy.

7. Approval gates
   - Only a human approval can authorize commit, push, merge/rebase, tag creation, real AWS use, or Terraform apply.
   - Approval should name the exact action and scope.

8. Delivery
   - After approval, the change can be committed and integrated by the human/operator.
   - The pipeline evidence remains as a portfolio artifact for what was validated locally.

## Safety boundaries

The agentic workflow is intentionally local-only:

- Floci endpoint: `http://localhost:4566` or `http://127.0.0.1:4566`.
- Credentials: fake local values such as `AWS_ACCESS_KEY_ID=test` and `AWS_SECRET_ACCESS_KEY=test`.
- Hosted CI: no `.github/workflows/`, `.gitlab-ci.yml`, or `gitlab-ci.yml`.
- Terraform: validate and plan are acceptable; apply requires explicit human approval.
- Git history: no commits, pushes, tags, merges, or rebases without explicit human approval.

## Evidence expectations

Good handoff evidence includes:

- Changed files summary.
- Exact validation commands and outcomes.
- Current `git status --short`.
- Confirmation that forbidden hosted CI config was not added.
- Confirmation that no real AWS resources or credentials were used.
- Any skipped checks with clear reasons.
