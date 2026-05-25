# Phase 8 Evidence — Resilience and Operations Drill

## Purpose

Show that the Floci Cloud Lab includes local-only backup/restore planning, failure-injection taxonomy, and idempotent event replay evidence.

## Regenerate

```bash
make resilience-drill
.venv/bin/python -m pytest tests/unit/test_resilience.py -q
make check
make devops-audit
```

## Expected drill output shape

```text
resilience drill: local-only backup/restore/failure-injection
{"summary": {"events_in_manifest": 3, "failure_scenarios": 4, "manifest_valid": true, "objects_in_manifest": 1, "processed_events": 1, "restore_steps": 6, "skipped_events": 2}}
{"manifest_checksum": "<sha256>"}
{"restore_step_names": ["confirm-local-endpoint", "ensure-bucket-and-table", "restore-object-bodies", "restore-metadata-records", "restore-outbox-events", "verify-checksums-and-counts"]}
{"failure_scenarios": ["missing_object_body", "corrupted_object_body", "duplicate_event_replay", "emulator_unavailable"]}
```

## Safety

- Local model only; no real AWS calls.
- No Terraform apply.
- No reset/delete operations.
- No secrets or raw object bodies in evidence.
