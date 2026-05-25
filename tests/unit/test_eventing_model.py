from app.backend.functions.events import build_object_created_event, mark_event_processed, public_event


def test_build_object_created_event_has_eventbridge_sqs_friendly_shape():
    record = {
        "owner_id": "lucas",
        "object_id": "obj_123",
        "name": "note.txt",
        "content_type": "text/plain",
        "size_bytes": 11,
        "s3_bucket": "floci-cloud-lab-local-objects",
        "s3_key": "objects/lucas/obj_123/note.txt",
        "sha256": "abc123",
        "category": "notes",
        "s3_version_id": "v1",
    }

    event = build_object_created_event(object_record=record, created_at="2026-05-25T15:00:00Z")

    assert event["pk"] == "OWNER#lucas"
    assert event["sk"].startswith("EVENT#2026-05-25T15:00:00Z#evt_")
    assert event["event_type"] == "ObjectCreated"
    assert event["source"] == "floci-cloud-lab.objects"
    assert event["status"] == "pending"
    assert event["attempts"] == 0
    assert event["idempotency_key"] == "ObjectCreated:lucas:obj_123"
    assert event["detail"]["key"] == "objects/lucas/obj_123/note.txt"
    assert event["detail"]["sha256"] == "abc123"


def test_mark_event_processed_is_idempotent():
    event = {"event_id": "evt_1", "status": "pending", "attempts": 0}

    processed = mark_event_processed(event, processed_at="2026-05-25T15:01:00Z")
    processed_again = mark_event_processed(processed, processed_at="2026-05-25T15:02:00Z")

    assert processed["status"] == "processed"
    assert processed["attempts"] == 1
    assert processed_again["attempts"] == 1
    assert processed_again["processed_at"] == "2026-05-25T15:01:00Z"


def test_public_event_hides_dynamodb_keys():
    assert public_event({"pk": "OWNER#x", "sk": "EVENT#x", "event_id": "evt"}) == {"event_id": "evt"}
