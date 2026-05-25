from app.backend.functions.orchestration import (
    STATE_MACHINE,
    build_compensation_plan,
    build_step_functions_mapping,
    run_object_ingestion_workflow,
    run_orchestration_demo,
)


def valid_payload():
    return {"owner_id": "lucas", "name": "note.txt", "content": "hello", "content_type": "text/plain"}


def test_state_machine_models_step_functions_like_shape():
    assert STATE_MACHINE["start_at"] == "ValidatePayload"
    assert STATE_MACHINE["states"]["WriteObject"]["retry"]["max_attempts"] == 3
    assert STATE_MACHINE["states"]["Success"]["type"] == "Succeed"
    assert STATE_MACHINE["states"]["CompensateIntegrityFailure"]["type"] == "Fail"


def test_successful_execution_records_deterministic_history_and_artifacts():
    result = run_object_ingestion_workflow(valid_payload())

    assert result["status"] == "SUCCEEDED"
    assert result["context"]["artifacts"]["integrity_verified"] is True
    assert result["context"]["idempotency_keys"] == [f"ObjectCreated:lucas:{result['context']['artifacts']['object_id']}"]
    assert result["history"][-1]["state"] == "Success"


def test_transient_failure_retries_with_backoff_then_succeeds():
    result = run_object_ingestion_workflow(valid_payload(), transient_failures={"WriteObject": 1})
    retry_events = [item for item in result["history"] if item["event"] == "retry-scheduled"]

    assert result["status"] == "SUCCEEDED"
    assert retry_events == [
        {
            "state": "WriteObject",
            "event": "retry-scheduled",
            "attempt": 1,
            "artifacts": ["payload_validated"],
            "error": "TransientTaskError",
            "delay_seconds": 1.0,
        }
    ]


def test_validation_failure_uses_catch_branch_without_data_compensation():
    result = run_object_ingestion_workflow({"owner_id": "lucas", "content": "missing name"})

    assert result["status"] == "FAILED"
    assert result["history"][-1]["state"] == "FailValidation"
    assert result["compensation"] == [{"order": 1, "action": "no-data-mutation", "reason": "failure reached before durable writes via FailValidation"}]


def test_integrity_failure_generates_compensation_in_safe_order():
    result = run_object_ingestion_workflow(valid_payload(), fail_at="VerifyIntegrity")
    actions = [step["action"] for step in result["compensation"]]

    assert result["status"] == "FAILED"
    assert actions == [
        "record-idempotent-replay-safe",
        "mark-event-compensated",
        "delete-or-quarantine-object-metadata",
        "delete-or-quarantine-object-body",
    ]


def test_compensation_plan_for_partial_context_is_explainable():
    plan = build_compensation_plan("CompensatePartialWrite", {"artifacts": {"object_id": "obj_1", "s3_key": "objects/x/obj_1/a.txt"}})

    assert plan[0]["action"] == "delete-or-quarantine-object-metadata"
    assert plan[1]["action"] == "delete-or-quarantine-object-body"


def test_aws_mapping_is_local_only_but_interview_ready():
    mapping = build_step_functions_mapping()

    assert mapping["workflow"] == "AWS Step Functions Standard Workflow"
    assert "Retry with exponential backoff" in mapping["reliability"]
    assert mapping["local_boundary"].startswith("No real AWS calls")


def test_orchestration_demo_summary_is_stable():
    demo = run_orchestration_demo()

    assert demo["local_only"] is True
    assert demo["summary"] == {
        "success_status": "SUCCEEDED",
        "failure_status": "FAILED",
        "success_history_events": 14,
        "failure_history_events": 11,
        "retry_events": 1,
        "compensation_steps": 4,
        "states_modeled": 10,
    }
