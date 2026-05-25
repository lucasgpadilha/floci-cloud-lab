from app.backend.functions.resilience import (
    build_backup_manifest,
    build_restore_plan,
    classify_failure,
    run_resilience_drill,
    simulate_event_replay,
    validate_backup_manifest,
)


def test_backup_manifest_is_deterministic_and_validates_counts_and_checksums():
    objects = [
        {"owner_id": "lucas", "object_id": "obj_b", "name": "b.txt", "s3_bucket": "bucket", "s3_key": "k/b", "sha256": "bbb", "size_bytes": 2},
        {"owner_id": "lucas", "object_id": "obj_a", "name": "a.txt", "s3_bucket": "bucket", "s3_key": "k/a", "sha256": "aaa", "size_bytes": 1},
    ]
    events = [
        {"event_id": "evt_b", "event_type": "ObjectCreated", "owner_id": "lucas", "object_id": "obj_b", "status": "pending", "attempts": 0, "idempotency_key": "b"},
        {"event_id": "evt_a", "event_type": "ObjectCreated", "owner_id": "lucas", "object_id": "obj_a", "status": "pending", "attempts": 0, "idempotency_key": "a"},
    ]

    first = build_backup_manifest(objects=objects, events=events, created_at="2026-05-25T15:00:00Z")
    second = build_backup_manifest(objects=list(reversed(objects)), events=list(reversed(events)), created_at="2026-05-25T15:00:00Z")

    assert first == second
    assert validate_backup_manifest(first)["ok"] is True
    assert first["object_count"] == 2
    assert first["event_count"] == 2


def test_restore_plan_requires_manifest_validation_and_orders_object_bodies_before_metadata():
    manifest = build_backup_manifest(
        objects=[{"owner_id": "lucas", "object_id": "obj_1", "name": "x", "s3_bucket": "bucket", "s3_key": "k", "sha256": "abc", "size_bytes": 3}],
        events=[],
        created_at="2026-05-25T15:00:00Z",
    )

    plan = build_restore_plan(manifest)
    step_names = [step["name"] for step in plan["steps"]]

    assert plan["ready"] is True
    assert step_names.index("restore-object-bodies") < step_names.index("restore-metadata-records")
    assert step_names[0] == "confirm-local-endpoint"
    assert step_names[-1] == "verify-checksums-and-counts"


def test_corrupt_manifest_is_not_ready_for_restore():
    manifest = build_backup_manifest(objects=[], events=[], created_at="2026-05-25T15:00:00Z")
    manifest["object_count"] = 99

    plan = build_restore_plan(manifest)

    assert plan["ready"] is False
    assert plan["validation"]["checks"]["object_count_matches"] is False


def test_failure_catalog_maps_local_detection_to_aws_recovery_concepts():
    missing = classify_failure("missing_object_body")
    duplicate = classify_failure("duplicate_event_replay")

    assert missing["severity"] == "high"
    assert "NoSuchKey" in missing["detection_signal"]
    assert "SQS at-least-once" in duplicate["aws_mapping"]


def test_event_replay_is_idempotent_for_duplicate_and_processed_events():
    events = [
        {"event_id": "evt_1", "status": "pending", "attempts": 0, "idempotency_key": "same"},
        {"event_id": "evt_2", "status": "pending", "attempts": 0, "idempotency_key": "same"},
        {"event_id": "evt_3", "status": "processed", "attempts": 1, "idempotency_key": "done"},
    ]

    result = simulate_event_replay(events)

    assert result["processed_count"] == 1
    assert result["skipped_count"] == 2
    assert result["processed"][0]["attempts"] == 1
    assert {event["skip_reason"] for event in result["skipped"]} == {"duplicate_idempotency_key", "already_processed"}


def test_resilience_drill_evidence_summary_is_portfolio_friendly():
    drill = run_resilience_drill()

    assert drill["local_only"] is True
    assert drill["summary"] == {
        "objects_in_manifest": 1,
        "events_in_manifest": 3,
        "restore_steps": 6,
        "failure_scenarios": 4,
        "processed_events": 1,
        "skipped_events": 2,
        "manifest_valid": True,
    }
