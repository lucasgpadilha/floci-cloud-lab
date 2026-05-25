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

## Observability demo

```bash
make observability-demo
```

Use this when validating structured logs, local metrics, request correlation, and error visibility.

## Incident drill: API error spike

1. Run `make observability-demo`.
2. Confirm the deliberate unsupported-media-type request emits `status_code=415`, `status_class=4xx`, and `error_code=unsupported_media_type`.
3. In a real AWS deployment, inspect CloudWatch Logs by `request_id` and check an `ApiErrorCount` alarm/dashboard panel.
4. Locally, confirm tests still pass with `make check`.

## Incident drill: event worker backlog

1. Create objects with `make app-demo` or direct API calls.
2. List pending events with `GET /events?status=pending` through the local API.
3. Process pending events with `make app-events-process` or `POST /events/process`.
4. Confirm processed events include `worker=local-outbox-worker` and `status=processed`.
5. In real AWS, equivalent checks would inspect SQS queue depth, oldest message age, Lambda consumer errors, and DLQ count.

## Resilience drill: backup/restore and failure injection

```bash
make resilience-drill
```

Use this when validating backup manifest checksums, restore sequencing, failure classification, and idempotent event replay without mutating local emulator state.

### Backup/restore checklist

1. Confirm the target endpoint is local-only: `http://localhost:4566` or `http://127.0.0.1:4566`.
2. Generate or inspect a backup manifest.
3. Validate manifest object/event counts and checksums.
4. Restore object bodies before DynamoDB-compatible metadata records.
5. Restore/replay outbox events only after state is present.
6. Verify counts, checksums, `GET /objects/{object_id}`, and worker idempotency.

### Failure-injection checklist

- Missing object body: metadata exists but object fetch fails. Restore the body, then rerun integrity verification.
- Corrupted object body: SHA-256 mismatch. Quarantine, restore last known-good body, and audit logs by `request_id`/`trace_id`.
- Duplicate event replay: same `idempotency_key` appears more than once. Skip duplicates and preserve the first processed result.
- Emulator unavailable: run `make floci-health`, inspect Docker/Floci logs, restart the local lab only if needed, then rerun smoke/plan checks.
