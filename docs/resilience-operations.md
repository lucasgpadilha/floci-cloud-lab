# Resilience and Operations Drills

This phase adds local-only resilience evidence to the Floci Cloud Lab. It demonstrates how the application would be backed up, restored, and recovered during common operational incidents without touching real AWS.

## Local boundary

All drills are modeled against the local Floci lab boundary:

```text
http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

No drill requires real AWS credentials, GitHub Actions, GitLab runners, or `terraform apply`.

## What the drill covers

`make resilience-drill` exercises a deterministic in-repo model for:

- backup manifest creation for object metadata and outbox event records;
- manifest checksums for object entries, event entries, and the manifest itself;
- restore ordering so object bodies are restored before DynamoDB-compatible metadata that points at those keys;
- outbox event replay with idempotency-key dedupe;
- failure classification for missing objects, corrupted object bodies, duplicate event replay, and local emulator unavailability.

## Backup manifest model

The local manifest records reviewer-safe metadata:

- `owner_id`
- `object_id`
- `s3_bucket`
- `s3_key`
- `sha256`
- `size_bytes`
- event status and `idempotency_key`

It intentionally does not store raw object bodies in evidence files. The real AWS equivalent would combine S3 object versioning/inventory, DynamoDB export or point-in-time recovery, and application-level checksum evidence.

## Restore plan

The generated restore plan uses this order:

1. Confirm the restore target is local-only.
2. Ensure the bucket and table exist.
3. Restore object bodies.
4. Restore metadata records.
5. Restore outbox events.
6. Verify counts and checksums.

The ordering matters because metadata records reference S3-compatible keys. Restoring metadata before object bodies can produce false-positive records that fail during `GET /objects/{object_id}`.

## Failure injection catalog

| Scenario | Detection signal | Local recovery | Real AWS mapping |
| --- | --- | --- | --- |
| `missing_object_body` | Metadata exists but object fetch returns 404/NoSuchKey | Restore object body, rerun integrity check | S3 version restore + DynamoDB consistency check |
| `corrupted_object_body` | Body SHA-256 differs from metadata/manifest | Quarantine corrupt body, restore last known-good body, audit request IDs | S3 version rollback, checksum validation, trace correlation |
| `duplicate_event_replay` | Duplicate `idempotency_key` or already processed event | Skip duplicate, preserve first `processed_at` | SQS at-least-once delivery and Lambda idempotency |
| `emulator_unavailable` | `make floci-health` fails or times out | Inspect Docker/Floci logs and restart local lab | Service availability runbook and retry budgets |

## Commands

```bash
make resilience-drill
.venv/bin/python -m pytest tests/unit/test_resilience.py -q
make check
make devops-audit
```

## Portfolio talking points

- The lab covers not only happy-path provisioning, but also failure recovery and evidence collection.
- Checksums make backup/restore results auditable.
- Event processing is explicitly idempotent, which maps to SQS/Lambda at-least-once delivery semantics.
- Recovery steps are documented before introducing destructive reset workflows.
