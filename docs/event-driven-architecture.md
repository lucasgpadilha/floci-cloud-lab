# Event-driven Architecture

Phase 6 adds an event-driven architecture pattern to the local Floci Cloud Lab without mutating real AWS or requiring an unapproved Terraform apply.

## What is implemented locally

The application now emits an `ObjectCreated` event whenever `POST /objects` stores a new object. The event is written to an outbox/event-log item in the same DynamoDB-compatible metadata table:

```text
pk = OWNER#<owner_id>
sk = EVENT#<event_time>#<event_id>
```

This keeps the lab runnable against the already-applied local Floci table and avoids Terraform drift. The shape intentionally mirrors EventBridge/SNS/SQS concepts:

- `event_id`: unique event id
- `event_type`: `ObjectCreated`
- `source`: `floci-cloud-lab.objects`
- `detail_type`: `Object Created`
- `time`: event timestamp
- `detail`: object storage metadata such as bucket, key, content type, SHA-256, category, and version id
- `status`: `pending` or `processed`
- `attempts`: local worker processing count
- `idempotency_key`: deterministic key for duplicate-safe consumers

## API and worker surface

The Lambda-style handler exposes local event operations:

- `GET /events?status=pending` lists event-log records for the caller.
- `POST /events/process` processes pending events with a local outbox worker.

The worker is intentionally idempotent: already processed events are skipped, so rerunning `POST /events/process` returns `processed_count: 0` when there is no pending work.

## AWS mapping

A production AWS version could map the same pattern to:

1. API Gateway + Lambda receives `POST /objects`.
2. Lambda writes the object to S3 and metadata to DynamoDB.
3. Lambda publishes an `ObjectCreated` event to EventBridge or SNS.
4. EventBridge/SNS fans out to SQS queues for async processors.
5. Workers consume from SQS with idempotency based on `idempotency_key`.
6. Dead-letter queues retain failed messages after bounded retries.

The local lab models these responsibilities with an outbox table because it is safe, deterministic, and works without new emulator resources.

## Terraform boundary

No new physical SQS/SNS/EventBridge resources were added in Phase 6 because the current local emulator resources were already applied. Adding queues/topics/rules would require an explicit local `terraform apply`.

Future approved migration candidates:

- SQS queue: `floci-cloud-lab-local-object-events`
- SQS DLQ: `floci-cloud-lab-local-object-events-dlq`
- SNS topic or EventBridge bus for fanout
- Event source mapping from SQS to a worker Lambda
- Alarm/log metrics for DLQ depth and processing failures

## Operational considerations

- Prefer at-least-once processing semantics.
- Consumers must be idempotent.
- Store enough event detail for consumers to operate without re-querying every field.
- Use DLQs and bounded retries for poison messages.
- Monitor queue depth, oldest message age, failures, and DLQ count.
- Keep local and real AWS endpoints clearly separated.
