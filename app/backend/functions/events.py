from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

EVENT_SOURCE = "floci-cloud-lab.objects"
OBJECT_CREATED = "ObjectCreated"


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def build_object_created_event(*, object_record: dict[str, Any], created_at: str | None = None) -> dict[str, Any]:
    event_time = created_at or utc_now_iso()
    event_id = f"evt_{uuid4().hex}"
    owner_id = str(object_record["owner_id"])
    object_id = str(object_record["object_id"])
    return {
        "pk": f"OWNER#{owner_id}",
        "sk": f"EVENT#{event_time}#{event_id}",
        "event_id": event_id,
        "event_type": OBJECT_CREATED,
        "source": EVENT_SOURCE,
        "detail_type": "Object Created",
        "owner_id": owner_id,
        "object_id": object_id,
        "time": event_time,
        "status": "pending",
        "attempts": 0,
        "idempotency_key": f"{OBJECT_CREATED}:{owner_id}:{object_id}",
        "detail": {
            "bucket": object_record.get("s3_bucket"),
            "key": object_record.get("s3_key"),
            "name": object_record.get("name"),
            "content_type": object_record.get("content_type"),
            "size_bytes": object_record.get("size_bytes"),
            "sha256": object_record.get("sha256"),
            "category": object_record.get("category"),
            "s3_version_id": object_record.get("s3_version_id"),
        },
    }


def public_event(event: dict[str, Any]) -> dict[str, Any]:
    hidden = {"pk", "sk"}
    return {key: value for key, value in event.items() if key not in hidden}


def mark_event_processed(event: dict[str, Any], *, processed_at: str | None = None) -> dict[str, Any]:
    if event.get("status") == "processed":
        return dict(event)
    updated = dict(event)
    updated["status"] = "processed"
    updated["processed_at"] = processed_at or utc_now_iso()
    updated["attempts"] = int(updated.get("attempts", 0)) + 1
    updated["worker"] = "local-outbox-worker"
    return updated


def mark_event_failed(event: dict[str, Any], *, reason: str, code: str, failed_at: str | None = None) -> dict[str, Any]:
    updated = dict(event)
    updated["status"] = "failed"
    updated["failed_at"] = failed_at or utc_now_iso()
    updated["attempts"] = max(int(updated.get("attempts", 0)), 1)
    updated["worker"] = "local-outbox-worker"
    updated["failure"] = {"code": code, "reason": reason, "retryable": True}
    detail = dict(updated.get("detail") or {})
    detail["failure_code"] = code
    detail["failure_reason"] = reason
    updated["detail"] = detail
    return updated
