# Orchestration Workflows

Phase 9 adds a local Step Functions-style orchestration model to the Floci Cloud Lab. It shows how a multi-step object ingestion workflow can be designed, tested, and explained without creating real AWS Step Functions state machines or cloud resources.

## Local boundary

The orchestration demo is deterministic and in-process:

```text
make orchestration-demo
```

It does not require a running emulator and does not call real AWS. The production mapping is documented for learning/interview purposes only.

## Workflow shape

The local workflow models object ingestion as a state machine:

1. `ValidatePayload`
2. `WriteObject`
3. `EmitObjectCreatedEvent`
4. `ProcessEvent`
5. `VerifyIntegrity`
6. `Success`

Failure/catch states:

- `FailValidation`
- `CompensatePartialWrite`
- `CompensateEventFailure`
- `CompensateIntegrityFailure`

## Reliability patterns

The module demonstrates:

- retry policies with max attempts, interval, and exponential backoff;
- catch branches for validation, write, event, and integrity failures;
- compensation plans for partial writes;
- idempotency keys for event processing;
- deterministic execution history for evidence.

## AWS mapping

| Local concept | AWS equivalent |
| --- | --- |
| State machine dictionary | AWS Step Functions state machine definition |
| `ValidatePayload` task | Lambda task for input validation |
| `WriteObject` task | Lambda task writing S3 object and DynamoDB metadata |
| `EmitObjectCreatedEvent` task | EventBridge `PutEvents` or SNS publish |
| `ProcessEvent` task | SQS/Lambda consumer with idempotency key |
| `VerifyIntegrity` task | Lambda task verifying S3 checksum and metadata consistency |
| Execution history | Step Functions execution history + CloudWatch Logs |
| Retry/catch policy | Step Functions `Retry` and `Catch` fields |
| Compensation plan | Saga-style rollback/remediation runbook |

## Demo evidence

`make orchestration-demo` prints:

- a successful execution with a retry on `WriteObject`;
- a failed execution at `VerifyIntegrity`;
- compensation steps for already-written object metadata/body and emitted event;
- a compact AWS mapping for Step Functions/Lambda/EventBridge/SQS/CloudWatch.

## Why this belongs in the portfolio

Many AWS projects show only CRUD APIs. This phase demonstrates the operational thinking behind production workflows: state transitions, retries, compensation, idempotency, and observability. The implementation stays local and safe while mapping cleanly to real AWS architecture vocabulary.
