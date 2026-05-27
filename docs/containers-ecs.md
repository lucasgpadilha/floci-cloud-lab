# Containers and ECS-style Workflows

Phase 10 containerizes the Floci Cloud Lab local API adapter and documents how the same operational patterns map to ECS/Fargate/ECR without deploying real AWS resources.

## Local boundary

The container workflow is local-only:

```bash
make app-container-build
make app-container-demo
```

It builds a local image named `floci-cloud-lab-app:local`, starts the app beside the local Floci emulator, checks `/health`, prints compact evidence, and tears the stack down. It does not push to ECR or create ECS resources.

## Files

| File | Purpose |
| --- | --- |
| `Dockerfile` | Python runtime for the local HTTP adapter. |
| `.dockerignore` | Keeps venvs, Terraform state, caches, and secrets out of the image context. |
| `compose.container.yaml` | Runs a container-demo stack with `floci` and the `app` service without binding Floci's host port. |
| `scripts/container-demo.sh` | Reproducible build/run/health demo. |
| `tests/unit/test_container_config.py` | Static guardrails for image, compose, healthcheck, fake credentials, and no secret copying. |

## Runtime shape

The app container runs:

```text
python -m app.backend.local_server --host 0.0.0.0 --port 8080
```

Local defaults inside the container:

```text
FLOCI_ENDPOINT=http://floci:4566
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
FLOCI_OBJECT_BUCKET=floci-cloud-lab-local-objects
FLOCI_METADATA_TABLE=floci-cloud-lab-local-metadata
```

`/health` is used for both local demo checks and Docker healthcheck evidence.

## ECS/Fargate mapping

| Local container concept | ECS/Fargate equivalent |
| --- | --- |
| `Dockerfile` image | Image built and pushed to ECR. |
| `compose.container.yaml` app service | ECS service running a Fargate task. |
| `ports: 8080:8080` | ALB target group forwarding to container port 8080. |
| Docker `HEALTHCHECK` and `/health` | ALB target health check + ECS container health check. |
| Fake local env vars | Task definition environment/secrets references. |
| `FLOCI_ENDPOINT=http://floci:4566` | Real AWS SDK default endpoints in production. |
| `docker compose ps/logs` | `aws ecs describe-services`, task events, and CloudWatch Logs. |

## Production notes

If this were promoted to real AWS, prefer ECS on Fargate for a production service. A real task definition should use:

- `networkMode: awsvpc` for Fargate;
- a valid CPU/memory pair such as 512 CPU and 1024 MiB memory;
- separate execution role and task role;
- ECR image scanning/lifecycle policies;
- CloudWatch Logs with explicit retention;
- deployment circuit breaker with rollback;
- `healthCheckGracePeriodSeconds` when behind an ALB;
- Secrets Manager or SSM Parameter Store for secrets, not image-baked credentials.

This repository intentionally stops at local container evidence until real AWS work is explicitly approved.
