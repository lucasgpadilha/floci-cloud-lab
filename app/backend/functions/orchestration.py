from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable

JsonDict = dict[str, Any]
TaskHandler = Callable[[JsonDict], JsonDict]


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    interval_seconds: int = 1
    backoff_rate: float = 2.0
    retry_on: tuple[str, ...] = ("TransientTaskError",)

    def delay_for_attempt(self, attempt: int) -> float:
        return self.interval_seconds * (self.backoff_rate ** max(attempt - 1, 0))

    def as_dict(self) -> JsonDict:
        return {
            "max_attempts": self.max_attempts,
            "interval_seconds": self.interval_seconds,
            "backoff_rate": self.backoff_rate,
            "retry_on": list(self.retry_on),
        }


class WorkflowTaskError(RuntimeError):
    error_name = "WorkflowTaskError"


class TransientTaskError(WorkflowTaskError):
    error_name = "TransientTaskError"


class ValidationTaskError(WorkflowTaskError):
    error_name = "ValidationTaskError"


class IntegrityTaskError(WorkflowTaskError):
    error_name = "IntegrityTaskError"


STATE_MACHINE = {
    "name": "LocalObjectIngestionWorkflow",
    "comment": "Step Functions-style local object ingestion workflow for Floci Cloud Lab.",
    "start_at": "ValidatePayload",
    "states": {
        "ValidatePayload": {"type": "Task", "next": "WriteObject", "catch": "FailValidation"},
        "WriteObject": {"type": "Task", "next": "EmitObjectCreatedEvent", "retry": RetryPolicy().as_dict(), "catch": "CompensatePartialWrite"},
        "EmitObjectCreatedEvent": {"type": "Task", "next": "ProcessEvent", "retry": RetryPolicy().as_dict(), "catch": "CompensateEventFailure"},
        "ProcessEvent": {"type": "Task", "next": "VerifyIntegrity", "retry": RetryPolicy(max_attempts=2).as_dict(), "catch": "CompensateEventFailure"},
        "VerifyIntegrity": {"type": "Task", "next": "Success", "catch": "CompensateIntegrityFailure"},
        "Success": {"type": "Succeed"},
        "FailValidation": {"type": "Fail"},
        "CompensatePartialWrite": {"type": "Fail"},
        "CompensateEventFailure": {"type": "Fail"},
        "CompensateIntegrityFailure": {"type": "Fail"},
    },
}


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def workflow_execution_id(input_payload: JsonDict) -> str:
    digest = hashlib.sha256(stable_json(input_payload).encode("utf-8")).hexdigest()[:16]
    return f"exec_{digest}"


def build_step_functions_mapping() -> JsonDict:
    return {
        "workflow": "AWS Step Functions Standard Workflow",
        "tasks": {
            "ValidatePayload": "Lambda task validating API/event input",
            "WriteObject": "Lambda task writing to S3 and DynamoDB",
            "EmitObjectCreatedEvent": "EventBridge PutEvents or SNS publish",
            "ProcessEvent": "SQS/Lambda consumer with idempotency key",
            "VerifyIntegrity": "Lambda task verifying S3 checksum and metadata consistency",
        },
        "observability": ["CloudWatch Logs", "CloudWatch Metrics", "X-Ray/OpenTelemetry trace correlation"],
        "reliability": ["Retry with exponential backoff", "Catch branches", "Compensation plan", "Idempotency keys"],
        "local_boundary": "No real AWS calls; deterministic in-process simulation only.",
    }


def run_object_ingestion_workflow(
    input_payload: JsonDict,
    *,
    fail_at: str | None = None,
    transient_failures: dict[str, int] | None = None,
) -> JsonDict:
    """Run a deterministic local orchestration simulation.

    `fail_at` injects a permanent failure at a state. `transient_failures` maps a state name to
    the number of attempts that should fail before succeeding, allowing retry/backoff evidence.
    """

    execution_id = workflow_execution_id(input_payload)
    context: JsonDict = {"input": deepcopy(input_payload), "execution_id": execution_id, "artifacts": {}, "idempotency_keys": []}
    history: list[JsonDict] = []
    transient_failures = dict(transient_failures or {})
    handlers = _task_handlers()
    current = STATE_MACHINE["start_at"]
    while True:
        state = STATE_MACHINE["states"][current]
        if state["type"] == "Succeed":
            history.append(_history_event(current, "succeeded", 1, context=context))
            return _execution_result("SUCCEEDED", execution_id, context, history, compensation=[])
        if state["type"] == "Fail":
            history.append(_history_event(current, "failed-terminal", 1, context=context))
            return _execution_result("FAILED", execution_id, context, history, compensation=build_compensation_plan(current, context))

        retry_policy = _retry_policy_from_state(state)
        attempt = 1
        while True:
            history.append(_history_event(current, "started", attempt, context=context))
            try:
                if fail_at == current:
                    raise _failure_for_state(current)(f"injected permanent failure at {current}")
                remaining_transient = transient_failures.get(current, 0)
                if remaining_transient > 0:
                    transient_failures[current] = remaining_transient - 1
                    raise TransientTaskError(f"injected transient failure at {current}")
                context = handlers[current](context)
                history.append(_history_event(current, "succeeded", attempt, context=context))
                current = state["next"]
                break
            except WorkflowTaskError as exc:
                error_name = getattr(exc, "error_name", type(exc).__name__)
                history.append(_history_event(current, "failed", attempt, context=context, error=error_name, message=str(exc)))
                if error_name in retry_policy.retry_on and attempt < retry_policy.max_attempts:
                    history.append(
                        _history_event(
                            current,
                            "retry-scheduled",
                            attempt,
                            context=context,
                            error=error_name,
                            delay_seconds=retry_policy.delay_for_attempt(attempt),
                        )
                    )
                    attempt += 1
                    continue
                current = state.get("catch", "CompensatePartialWrite")
                break


def build_compensation_plan(failure_state: str, context: JsonDict) -> list[JsonDict]:
    artifacts = context.get("artifacts", {})
    plan: list[JsonDict] = []
    if artifacts.get("event_processed"):
        plan.append({"order": len(plan) + 1, "action": "record-idempotent-replay-safe", "reason": "processed event should not be processed again"})
    if artifacts.get("event_id"):
        plan.append({"order": len(plan) + 1, "action": "mark-event-compensated", "event_id": artifacts["event_id"]})
    if artifacts.get("object_id"):
        plan.append({"order": len(plan) + 1, "action": "delete-or-quarantine-object-metadata", "object_id": artifacts["object_id"]})
    if artifacts.get("s3_key"):
        plan.append({"order": len(plan) + 1, "action": "delete-or-quarantine-object-body", "s3_key": artifacts["s3_key"]})
    if not plan:
        plan.append({"order": 1, "action": "no-data-mutation", "reason": f"failure reached before durable writes via {failure_state}"})
    return plan


def run_orchestration_demo() -> JsonDict:
    input_payload = {
        "owner_id": "lucas",
        "name": "orchestration-demo.txt",
        "content": "phase 9 local workflow orchestration",
        "content_type": "text/plain",
        "metadata": {"category": "workflow", "source": "orchestration-demo"},
    }
    success = run_object_ingestion_workflow(input_payload, transient_failures={"WriteObject": 1})
    failure = run_object_ingestion_workflow(input_payload, fail_at="VerifyIntegrity")
    return {
        "demo": "phase9-orchestration-workflows",
        "local_only": True,
        "state_machine": STATE_MACHINE,
        "step_functions_mapping": build_step_functions_mapping(),
        "success_execution": _compact_execution(success),
        "failure_execution": _compact_execution(failure),
        "summary": {
            "success_status": success["status"],
            "failure_status": failure["status"],
            "success_history_events": len(success["history"]),
            "failure_history_events": len(failure["history"]),
            "retry_events": sum(1 for item in success["history"] if item["event"] == "retry-scheduled"),
            "compensation_steps": len(failure["compensation"]),
            "states_modeled": len(STATE_MACHINE["states"]),
        },
    }


def _task_handlers() -> dict[str, TaskHandler]:
    return {
        "ValidatePayload": _validate_payload,
        "WriteObject": _write_object,
        "EmitObjectCreatedEvent": _emit_event,
        "ProcessEvent": _process_event,
        "VerifyIntegrity": _verify_integrity,
    }


def _validate_payload(context: JsonDict) -> JsonDict:
    payload = context["input"]
    for key in ("owner_id", "name", "content"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise ValidationTaskError(f"{key} is required")
    context["artifacts"]["payload_validated"] = True
    return context


def _write_object(context: JsonDict) -> JsonDict:
    payload = context["input"]
    object_id = f"obj_{hashlib.sha256((payload['owner_id'] + payload['name']).encode()).hexdigest()[:12]}"
    safe_name = payload["name"].replace("/", "-").strip()
    content_bytes = payload["content"].encode("utf-8")
    context["artifacts"].update(
        {
            "object_id": object_id,
            "s3_key": f"objects/{payload['owner_id']}/{object_id}/{safe_name}",
            "sha256": hashlib.sha256(content_bytes).hexdigest(),
            "size_bytes": len(content_bytes),
            "metadata_record_written": True,
        }
    )
    return context


def _emit_event(context: JsonDict) -> JsonDict:
    owner_id = context["input"]["owner_id"]
    object_id = context["artifacts"]["object_id"]
    context["artifacts"]["event_id"] = f"evt_{hashlib.sha256(object_id.encode()).hexdigest()[:12]}"
    context["idempotency_keys"].append(f"ObjectCreated:{owner_id}:{object_id}")
    return context


def _process_event(context: JsonDict) -> JsonDict:
    if not context["artifacts"].get("event_id"):
        raise WorkflowTaskError("event must be emitted before processing")
    context["artifacts"]["event_processed"] = True
    return context


def _verify_integrity(context: JsonDict) -> JsonDict:
    if not context["artifacts"].get("sha256"):
        raise IntegrityTaskError("missing object checksum")
    context["artifacts"]["integrity_verified"] = True
    return context


def _retry_policy_from_state(state: JsonDict) -> RetryPolicy:
    raw = state.get("retry") or {}
    return RetryPolicy(
        max_attempts=int(raw.get("max_attempts", 1)),
        interval_seconds=int(raw.get("interval_seconds", 1)),
        backoff_rate=float(raw.get("backoff_rate", 2.0)),
        retry_on=tuple(raw.get("retry_on", [])),
    )


def _failure_for_state(state_name: str) -> type[WorkflowTaskError]:
    return {
        "ValidatePayload": ValidationTaskError,
        "VerifyIntegrity": IntegrityTaskError,
    }.get(state_name, WorkflowTaskError)


def _history_event(state: str, event: str, attempt: int, *, context: JsonDict, error: str | None = None, message: str | None = None, delay_seconds: float | None = None) -> JsonDict:
    item: JsonDict = {"state": state, "event": event, "attempt": attempt, "artifacts": sorted(context.get("artifacts", {}).keys())}
    if error:
        item["error"] = error
    if message:
        item["message"] = message
    if delay_seconds is not None:
        item["delay_seconds"] = delay_seconds
    return item


def _execution_result(status: str, execution_id: str, context: JsonDict, history: list[JsonDict], compensation: list[JsonDict]) -> JsonDict:
    return {"execution_id": execution_id, "status": status, "context": context, "history": history, "compensation": compensation}


def _compact_execution(execution: JsonDict) -> JsonDict:
    return {
        "execution_id": execution["execution_id"],
        "status": execution["status"],
        "history_events": len(execution["history"]),
        "last_event": execution["history"][-1],
        "compensation": execution["compensation"],
    }
