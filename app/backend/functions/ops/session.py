from __future__ import annotations

from typing import Any

JsonDict = dict[str, Any]


def build_ops_session(*, owner_id: str, request_id: str) -> JsonDict:
    return {
        "session": {
            "id": f"local-{owner_id}",
            "owner_id": owner_id,
            "mode": "local",
            "scope": "disposable-emulator-workflow",
        },
        "positioning": "local-cloud-workflow-debugger",
        "adapter": {
            "name": "floci",
            "endpoint": "http://localhost:4566",
            "runtime": "aws-compatible-local-emulator",
            "account_id": "000000000000",
            "region": "us-east-1",
        },
        "safety": {
            "local_only": True,
            "uses_real_cloud": False,
            "uses_real_credentials": False,
            "allows_shell_execution": False,
            "bounded_mutations_only": True,
        },
        "capabilities": [
            {"id": "flow-traces", "label": "Flow traces", "description": "Correlate request, object, metadata, outbox, and processor state"},
            {"id": "payload-inspection", "label": "Payload inspection", "description": "Inspect local payloads and metadata without cloud credentials"},
            {"id": "bounded-replay", "label": "Bounded replay", "description": "Replay deterministic local events only"},
            {"id": "namespace-reset", "label": "Namespace reset", "description": "Reset disposable local state by owner/namespace"},
            {"id": "report-export", "label": "Report export", "description": "Export sanitized local reproduction artifacts"},
        ],
        "service_map": [
            {"id": "client", "label": "Client", "kind": "http-client"},
            {"id": "api", "label": "API adapter", "kind": "lambda-style-handler"},
            {"id": "object-store", "label": "Object store", "kind": "s3-compatible"},
            {"id": "metadata-store", "label": "Metadata store", "kind": "dynamodb-compatible"},
            {"id": "event-outbox", "label": "Event outbox", "kind": "local-event-store"},
            {"id": "processor", "label": "Processor", "kind": "bounded-local-action"},
        ],
        "request_id": request_id,
    }
