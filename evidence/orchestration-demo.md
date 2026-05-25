# Phase 9 Evidence — Orchestration Demo

## Purpose

Show that Floci Cloud Lab includes Step Functions-style workflow design with retry, catch, compensation, and idempotency semantics while remaining local-only.

## Regenerate

```bash
make orchestration-demo
.venv/bin/python -m pytest tests/unit/test_orchestration.py -q
make check
make devops-audit
```

## Expected output shape

```text
orchestration demo: local Step Functions-style workflow simulation
{"summary": {"compensation_steps": 4, "failure_history_events": 11, "failure_status": "FAILED", "retry_events": 1, "states_modeled": 10, "success_history_events": 14, "success_status": "SUCCEEDED"}}
{"success_execution": {...}}
{"failure_execution": {...}}
{"aws_mapping": {...}}
```

## Safety

- No real AWS calls.
- No Step Functions deployment.
- No `terraform apply`.
- No emulator reset or data deletion.
- Deterministic in-process simulation only.
