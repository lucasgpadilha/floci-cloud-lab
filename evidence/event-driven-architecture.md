# Evidence — Event-driven Architecture

Phase 6 demonstrates local event-driven architecture patterns without real AWS calls.

## Implemented proof points

- `POST /objects` creates object metadata and an `ObjectCreated` outbox event.
- Event shape includes source, detail type, event type, time, detail payload, status, attempts, and idempotency key.
- `GET /events` lists the caller's event log.
- `GET /events?status=pending` filters pending work.
- `POST /events/process` marks pending events as processed.
- Re-running `POST /events/process` is idempotent and processes zero already-processed events.

## Local demo command

```bash
make app-demo
```

Expected eventing excerpts:

```text
GET /events -> 200
status: pending
event_type: ObjectCreated
source: floci-cloud-lab.objects

POST /events/process -> 200
processed_count: 1

POST /events/process -> 200
processed_count: 0  # if no pending work remains
```

## Validation

Unit tests cover event shape and idempotent processing semantics:

```bash
.venv/bin/python -m pytest tests/unit/test_eventing_model.py tests/unit/test_api_handler.py -q
```

Latest targeted result during implementation:

```text
11 passed
```
