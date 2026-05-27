# Phase 10 Evidence — Container Demo

## Purpose

Show that the Floci Cloud Lab backend can run as a local container with a Docker healthcheck and ECS/Fargate-ready operational shape.

## Regenerate

```bash
make app-container-build
make app-container-demo
.venv/bin/python -m pytest tests/unit/test_container_config.py -q
make check
make devops-audit
```

If Docker is unavailable, `make app-container-demo` reports a skipped local demo instead of implying a cloud dependency.

## Expected output shape

```text
container demo: build local app image
container demo: start floci + app
container demo: wait for app health on http://127.0.0.1:8080/health
container demo: health {"ok": true, "service": "floci-cloud-lab-api", ...}
container demo: docker health healthy
container demo: services
[{"health": "healthy", "name": "...", "service": "app", "state": "running"}, ...]
```

## Safety

- No real AWS calls.
- No ECR push.
- No ECS/Fargate service creation.
- No `terraform apply`.
- Fake local credentials only.
- `.dockerignore` excludes venvs, Terraform state, caches, and `.env` files.
