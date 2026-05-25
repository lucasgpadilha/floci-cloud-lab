# Runbook

## Install local development dependencies

```bash
make install-dev
```

This creates `.venv/` and installs Python test dependencies.

## Start local lab

```bash
make floci-up
```

## Export local AWS environment

```bash
eval $(make floci-env)
```

## Validate Floci health

```bash
make floci-health
```

## Run smoke tests

```bash
make floci-smoke
```

Smoke tests use boto3 against `http://localhost:4566` and validate basic S3 and DynamoDB round trips.

## Validate Terraform locally

```bash
make terraform-fmt
make terraform-validate
make terraform-plan-local
```

## Stop local lab

```bash
make floci-down
```

## Troubleshooting

### Floci is not reachable

- Check Docker is running.
- Run `docker compose ps`.
- Check port 4566 is free.
- Check `docker compose logs floci`.
- On WSL, if Docker resolves to `/mnt/c/Program Files/Docker/...` but prints `The command 'docker' could not be found in this WSL 2 distro`, enable Docker Desktop WSL integration for this distro or install a Docker engine inside WSL before running Floci.

### AWS CLI or boto3 talks to real AWS by mistake

- Stop immediately.
- Confirm `AWS_ENDPOINT_URL=http://localhost:4566`.
- Prefer explicit endpoint arguments in scripts.
- Do not use real profiles.

### Terraform provider errors

- Confirm `infra/envs/local/providers.tf` endpoint overrides are local.
- Confirm Floci is running before planning/applying resources that require API calls.
- Confirm the resource/API is supported by Floci.

## Reset local state

The default Compose configuration uses memory mode. Restarting Floci resets state:

```bash
make floci-down
make floci-up
```
