# Release Process

Floci Cloud Lab uses a local-first release process. The repository demonstrates AWS-shaped delivery discipline without hosted CI runners, real AWS endpoints, or cloud spend by default.

## Canonical local CI

Run the canonical local CI pipeline from the repository root:

```bash
make pipeline
```

The pipeline runs safe local checks in a deterministic order:

1. Documentation/file presence checks.
2. Forbidden hosted CI guard (`.github/workflows/`, `.gitlab-ci.yml`, and `gitlab-ci.yml` are blocked).
3. Shell syntax checks for scripts.
4. Docker Compose configuration validation.
5. Container Compose configuration validation.
6. Kubernetes static manifest validation.
7. Terraform formatting and validation for the local environment.
8. Python tests.
9. Local Floci health and smoke checks.
10. Terraform plan against the local Floci endpoint only.

`make devops-audit` remains available for a stricter audit, including drift detection, after local resources have been created with explicit human approval.

`make pipeline` must not run `terraform apply`, create real AWS resources, push commits, create tags, or depend on GitHub Actions/GitLab runners.

## Evidence capture

Capture the latest local CI evidence with:

```bash
make evidence
```

This writes sanitized command output to:

```text
evidence/pipeline-latest.md
```

The capture script records timestamps, command exit codes, `make pipeline`, `make check`, `git diff --check`, and the forbidden CI guard. It refuses non-local `FLOCI_ENDPOINT` values and does not collect `.env`, `.terraform/`, `*.tfstate`, `.venv/`, cache directories, or full environment dumps.

## Human approval gates

A human reviewer must explicitly approve before any of the following actions:

- Commit.
- Push.
- Merge or rebase.
- Create or move a tag.
- Run any real AWS command.
- Use real AWS credentials or non-local AWS endpoints.
- Run `terraform apply`, including against local Floci.
- Add hosted CI configuration such as GitHub Actions or GitLab runners.

## Local semantic versioning and tags

Versioning is documented as a human-controlled local process; this phase does not create tags.

Recommended process after review approval:

1. Confirm `make pipeline`, `make evidence`, `make check`, and `git diff --check` pass.
2. Review `evidence/pipeline-latest.md` for failures, secrets, real endpoints, or noisy/generated content.
3. Choose the semantic version bump:
   - `MAJOR` for incompatible portfolio/release-process changes.
   - `MINOR` for new lab capability phases.
   - `PATCH` for fixes or documentation-only corrections.
4. Commit only after explicit approval.
5. Create an annotated local tag only after explicit approval, for example `v0.12.0`.
6. Push branch and tags only after explicit approval.

## Future plan: local CodeBuild-style emulation

A CodeBuild-style local pipeline can be considered later if Floci supports the relevant APIs or a reliable local emulation story. Until then, the Makefile pipeline is the source of truth for local CI/CD evidence.
