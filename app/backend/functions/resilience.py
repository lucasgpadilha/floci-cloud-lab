from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

JsonDict = dict[str, Any]


@dataclass(frozen=True)
class FailureClassification:
    scenario: str
    severity: str
    detection_signal: str
    local_recovery: list[str]
    aws_mapping: str

    def as_dict(self) -> JsonDict:
        return {
            "scenario": self.scenario,
            "severity": self.severity,
            "detection_signal": self.detection_signal,
            "local_recovery": self.local_recovery,
            "aws_mapping": self.aws_mapping,
        }


def stable_json(value: Any) -> str:
    """Serialize data deterministically for manifests and evidence hashes."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def build_backup_manifest(
    *,
    objects: list[JsonDict],
    events: list[JsonDict],
    created_at: str | None = None,
) -> JsonDict:
    """Build a deterministic local backup manifest for object metadata and outbox events.

    The manifest intentionally stores metadata, keys, sizes, and checksums rather than raw object bodies.
    In a real AWS deployment this maps to S3 inventory/versioning plus DynamoDB export/PITR metadata.
    """

    timestamp = created_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    object_entries = [_manifest_object_entry(item) for item in sorted(objects, key=lambda item: item.get("object_id", ""))]
    event_entries = [_manifest_event_entry(item) for item in sorted(events, key=lambda item: item.get("event_id", ""))]
    body = {
        "manifest_version": "2026-05-25.phase8.v1",
        "created_at": timestamp,
        "scope": "local-floci-emulator",
        "object_count": len(object_entries),
        "event_count": len(event_entries),
        "objects": object_entries,
        "events": event_entries,
    }
    body["objects_checksum"] = sha256_hex(object_entries)
    body["events_checksum"] = sha256_hex(event_entries)
    body["manifest_checksum"] = sha256_hex({k: v for k, v in body.items() if k != "manifest_checksum"})
    return body


def validate_backup_manifest(manifest: JsonDict) -> JsonDict:
    objects = manifest.get("objects", [])
    events = manifest.get("events", [])
    expected_manifest_checksum = manifest.get("manifest_checksum")
    without_checksum = {k: v for k, v in manifest.items() if k != "manifest_checksum"}
    checks = {
        "object_count_matches": manifest.get("object_count") == len(objects),
        "event_count_matches": manifest.get("event_count") == len(events),
        "objects_checksum_matches": manifest.get("objects_checksum") == sha256_hex(objects),
        "events_checksum_matches": manifest.get("events_checksum") == sha256_hex(events),
        "manifest_checksum_matches": expected_manifest_checksum == sha256_hex(without_checksum),
    }
    return {"ok": all(checks.values()), "checks": checks}


def build_restore_plan(manifest: JsonDict) -> JsonDict:
    validation = validate_backup_manifest(manifest)
    steps = [
        {"order": 1, "name": "confirm-local-endpoint", "reason": "avoid real AWS restore target"},
        {"order": 2, "name": "ensure-bucket-and-table", "reason": "restore target primitives before data"},
        {"order": 3, "name": "restore-object-bodies", "count": manifest.get("object_count", 0), "reason": "S3 bodies must exist before metadata points at keys"},
        {"order": 4, "name": "restore-metadata-records", "count": manifest.get("object_count", 0), "reason": "DynamoDB metadata references restored object keys"},
        {"order": 5, "name": "restore-outbox-events", "count": manifest.get("event_count", 0), "reason": "events can be replayed idempotently after state exists"},
        {"order": 6, "name": "verify-checksums-and-counts", "reason": "prove backup and restore consistency"},
    ]
    return {"ready": validation["ok"], "validation": validation, "steps": steps}


def classify_failure(scenario: str) -> JsonDict:
    classifications = {
        "missing_object_body": FailureClassification(
            scenario="missing_object_body",
            severity="high",
            detection_signal="metadata exists but S3-compatible get_object returns 404/NoSuchKey",
            local_recovery=[
                "pause delete/reset operations",
                "inspect the backup manifest for the expected s3_key and sha256",
                "restore the object body first",
                "rerun GET /objects/{object_id} and integrity verification",
            ],
            aws_mapping="S3 versioning/object restore plus DynamoDB metadata consistency check",
        ),
        "corrupted_object_body": FailureClassification(
            scenario="corrupted_object_body",
            severity="critical",
            detection_signal="retrieved body SHA-256 does not match metadata or backup manifest checksum",
            local_recovery=[
                "quarantine the corrupt object version",
                "restore the last known-good body from backup",
                "recompute SHA-256 and update evidence",
                "audit recent writes by request_id/trace_id",
            ],
            aws_mapping="S3 version rollback, checksum validation, CloudTrail/X-Ray request correlation",
        ),
        "duplicate_event_replay": FailureClassification(
            scenario="duplicate_event_replay",
            severity="medium",
            detection_signal="same idempotency_key appears more than once or processed event is replayed",
            local_recovery=[
                "skip already-processed event ids",
                "dedupe by idempotency_key",
                "preserve first processed_at timestamp",
                "record replay as an operational metric, not a data mutation",
            ],
            aws_mapping="SQS at-least-once delivery with Lambda idempotency key / DynamoDB condition checks",
        ),
        "emulator_unavailable": FailureClassification(
            scenario="emulator_unavailable",
            severity="high",
            detection_signal="health check to http://localhost:4566 fails or times out",
            local_recovery=[
                "run make floci-health",
                "check docker compose ps and logs",
                "restart with make floci-down && make floci-up if needed",
                "rerun terraform plan and smoke tests after recovery",
            ],
            aws_mapping="regional/service availability incident runbook with health checks and retry budgets",
        ),
    }
    if scenario not in classifications:
        return FailureClassification(
            scenario=scenario,
            severity="unknown",
            detection_signal="scenario is not part of the local drill catalog",
            local_recovery=["capture evidence", "classify blast radius", "add the scenario to docs/tests"],
            aws_mapping="incident taxonomy backlog item",
        ).as_dict()
    return classifications[scenario].as_dict()


def simulate_event_replay(events: list[JsonDict]) -> JsonDict:
    """Process events idempotently, skipping processed records and duplicate idempotency keys."""

    processed: list[JsonDict] = []
    skipped: list[JsonDict] = []
    seen_keys: set[str] = set()
    for event in copy.deepcopy(events):
        key = str(event.get("idempotency_key") or event.get("event_id"))
        if key in seen_keys:
            event["skip_reason"] = "duplicate_idempotency_key"
            skipped.append(event)
            continue
        seen_keys.add(key)
        if event.get("status") == "processed":
            event["skip_reason"] = "already_processed"
            skipped.append(event)
            continue
        event["status"] = "processed"
        event["attempts"] = int(event.get("attempts", 0)) + 1
        event.setdefault("processed_at", "2026-05-25T15:30:00Z")
        processed.append(event)
    return {"processed_count": len(processed), "skipped_count": len(skipped), "processed": processed, "skipped": skipped}


def run_resilience_drill() -> JsonDict:
    objects = [
        {
            "owner_id": "lucas",
            "object_id": "obj_phase8",
            "name": "resilience-note.txt",
            "s3_bucket": "floci-cloud-lab-local-objects",
            "s3_key": "objects/lucas/obj_phase8/resilience-note.txt",
            "sha256": "0b7058d9b6f5d0c7e53e9d3d46fbabcf9d6b38e3e5cb8530aa9d96dc2f7e558c",
            "size_bytes": 34,
            "version": 1,
            "created_at": "2026-05-25T15:00:00Z",
        }
    ]
    events = [
        {
            "event_id": "evt_phase8_a",
            "event_type": "ObjectCreated",
            "owner_id": "lucas",
            "object_id": "obj_phase8",
            "status": "pending",
            "attempts": 0,
            "idempotency_key": "ObjectCreated:lucas:obj_phase8",
        },
        {
            "event_id": "evt_phase8_duplicate",
            "event_type": "ObjectCreated",
            "owner_id": "lucas",
            "object_id": "obj_phase8",
            "status": "pending",
            "attempts": 0,
            "idempotency_key": "ObjectCreated:lucas:obj_phase8",
        },
        {
            "event_id": "evt_phase8_done",
            "event_type": "ObjectIndexed",
            "owner_id": "lucas",
            "object_id": "obj_phase8",
            "status": "processed",
            "attempts": 1,
            "idempotency_key": "ObjectIndexed:lucas:obj_phase8",
            "processed_at": "2026-05-25T15:05:00Z",
        },
    ]
    manifest = build_backup_manifest(objects=objects, events=events, created_at="2026-05-25T15:30:00Z")
    restore_plan = build_restore_plan(manifest)
    replay = simulate_event_replay(events)
    failure_scenarios = [
        classify_failure("missing_object_body"),
        classify_failure("corrupted_object_body"),
        classify_failure("duplicate_event_replay"),
        classify_failure("emulator_unavailable"),
    ]
    return {
        "drill": "phase8-resilience-operations",
        "local_only": True,
        "manifest": manifest,
        "restore_plan": restore_plan,
        "event_replay": replay,
        "failure_scenarios": failure_scenarios,
        "summary": {
            "objects_in_manifest": manifest["object_count"],
            "events_in_manifest": manifest["event_count"],
            "restore_steps": len(restore_plan["steps"]),
            "failure_scenarios": len(failure_scenarios),
            "processed_events": replay["processed_count"],
            "skipped_events": replay["skipped_count"],
            "manifest_valid": restore_plan["ready"],
        },
    }


def _manifest_object_entry(item: JsonDict) -> JsonDict:
    return {
        "owner_id": item["owner_id"],
        "object_id": item["object_id"],
        "name": item.get("name"),
        "s3_bucket": item.get("s3_bucket"),
        "s3_key": item.get("s3_key"),
        "sha256": item.get("sha256"),
        "size_bytes": int(item.get("size_bytes", 0)),
        "version": int(item.get("version", 1)),
    }


def _manifest_event_entry(item: JsonDict) -> JsonDict:
    return {
        "event_id": item["event_id"],
        "event_type": item.get("event_type"),
        "owner_id": item.get("owner_id"),
        "object_id": item.get("object_id"),
        "status": item.get("status"),
        "attempts": int(item.get("attempts", 0)),
        "idempotency_key": item.get("idempotency_key"),
    }
