from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Any

JsonDict = dict[str, Any]


@dataclass(frozen=True)
class TraceEvent:
    id: str
    type: str
    owner_id: str
    object_id: str
    status: str
    attempts: int
    detail: JsonDict
    failure: JsonDict | None = None

    @classmethod
    def from_repository_event(cls, event: JsonDict) -> "TraceEvent":
        return cls(
            id=str(event.get("event_id", "unknown-event")),
            type=str(event.get("event_type", "ObjectCreated")),
            owner_id=str(event.get("owner_id", "unknown-owner")),
            object_id=str(event.get("object_id", "unknown-object")),
            status=str(event.get("status", "unknown")),
            attempts=int(event.get("attempts") or 0),
            detail=dict(event.get("detail") or {}),
            failure=dict(event.get("failure") or {}) or None,
        )


def trace_id_for_event(event: TraceEvent) -> str:
    return f"trace_{event.object_id}_{event.id}"


def build_trace_list(events: list[TraceEvent]) -> JsonDict:
    traces = [build_trace_summary(event) for event in events]
    return {"count": len(traces), "traces": traces}


def build_trace_summary(event: TraceEvent) -> JsonDict:
    trace_id = trace_id_for_event(event)
    return {
        "id": trace_id,
        "owner_id": event.owner_id,
        "status": trace_status(event),
        "method": "POST",
        "path": "/objects",
        "summary": trace_summary(event),
        "artifact": {"object_id": event.object_id, "event_id": event.id, "event_type": event.type},
        "links": {"detail": f"/ops/traces/{trace_id}"},
    }


def find_trace_event(*, trace_id: str, events: list[TraceEvent]) -> TraceEvent | None:
    for event in events:
        if trace_id_for_event(event) == trace_id:
            return event
    return None


def build_trace_detail(event: TraceEvent, *, owner_id: str) -> JsonDict:
    status = trace_status(event)
    detail = {
        "id": trace_id_for_event(event),
        "owner_id": owner_id,
        "status": status,
        "summary": trace_summary(event),
        "artifact": {"object_id": event.object_id, "event_id": event.id, "event_type": event.type},
        "steps": trace_steps(event=event, status=status),
        "commands": trace_commands(owner_id=owner_id),
        "actions": trace_actions(trace_id_for_event(event)),
    }
    if event.failure:
        detail["failure"] = event.failure
    return detail


def trace_steps(*, event: TraceEvent, status: str) -> list[JsonDict]:
    processor_status = "ok" if status == "complete" else "waiting" if status == "pending" else "failed"
    object_detail = event.detail.get("key") or event.object_id
    return [
        {"id": "request", "label": "API request received", "status": "ok", "detail": "POST /objects accepted by local API adapter"},
        {"id": "payload", "label": "Payload validated", "status": "ok", "detail": "Content and metadata passed bounded local validation"},
        {"id": "object-store", "label": "Object stored", "status": "ok", "detail": f"{object_detail} written to local S3-compatible storage"},
        {"id": "metadata", "label": "Metadata indexed", "status": "ok", "detail": "DynamoDB-compatible metadata row links owner, category, object id, and key"},
        {"id": "outbox", "label": "Outbox event emitted", "status": "ok", "detail": f"{event.id} captured as {event.type}"},
        {"id": "processor", "label": "Outbox processed", "status": processor_status, "detail": processor_detail(event=event, status=status)},
    ]


def processor_detail(*, event: TraceEvent, status: str) -> str:
    if status == "complete":
        return "Bounded local processor consumed the event"
    if status == "pending":
        return "Event is waiting for bounded local processing"
    if event.failure:
        return str(event.failure.get("reason") or "Processor failed with actionable local reason")
    return "Processor failed with unknown local reason"


def trace_actions(trace_id: str) -> list[JsonDict]:
    return [
        {"id": "inspect-payload", "label": "Inspect payload", "method": "GET", "path": f"/ops/traces/{trace_id}", "safe": True},
        {"id": "export-report", "label": "Export report", "method": "GET", "path": f"/ops/report?trace_id={trace_id}", "safe": True},
        {"id": "process-pending", "label": "Process pending events", "method": "POST", "path": "/events/process?limit=10", "safe": True},
    ]


def trace_commands(*, owner_id: str) -> list[JsonDict]:
    create_argv = [
        "curl",
        "-X",
        "POST",
        "-H",
        "content-type: application/json",
        "-H",
        f"x-floci-user: {owner_id}",
        "http://127.0.0.1:8080/objects",
    ]
    process_argv = [
        "curl",
        "-X",
        "POST",
        "-H",
        f"x-floci-user: {owner_id}",
        "http://127.0.0.1:8080/events/process?limit=10",
    ]
    return [
        {
            "label": "replay object create",
            "kind": "curl",
            "argv": create_argv,
            "command": shell_command(create_argv),
        },
        {
            "label": "process pending events",
            "kind": "curl",
            "argv": process_argv,
            "command": shell_command(process_argv),
        },
    ]


def shell_command(argv: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in argv)


def trace_status(event: TraceEvent) -> str:
    if event.status == "processed":
        return "complete"
    if event.status == "pending":
        return "pending"
    return "failed"


def trace_summary(event: TraceEvent) -> str:
    if event.status == "processed":
        return "request stored object, indexed metadata, emitted event, processed outbox"
    if event.status == "pending":
        return "request stored object, indexed metadata, emitted event, awaiting processor"
    if event.status == "failed" and event.failure:
        return "request stored object, indexed metadata, emitted event, processor failed with actionable reason"
    return "request flow failed or has unknown processor state"
