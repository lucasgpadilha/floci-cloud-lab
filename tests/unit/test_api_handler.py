import json

from botocore.exceptions import ClientError

from app.backend.functions.api import create_handler


class UnprovisionedLocalRepository:
    def create_object(self, **_kwargs):
        raise ClientError({"Error": {"Code": "NoSuchBucket", "Message": "The specified bucket does not exist."}}, "PutObject")

    def list_objects(self, **_kwargs):
        raise AssertionError("not used")

    def get_object(self, **_kwargs):
        raise AssertionError("not used")

    def list_events(self, **_kwargs):
        raise AssertionError("not used")

    def process_pending_events(self, **_kwargs):
        raise AssertionError("not used")

    def mark_event_failed(self, **_kwargs):
        raise AssertionError("not used")


class InMemoryRepository:
    def __init__(self):
        self.objects = {}
        self.events = []

    def create_object(self, *, owner_id, name, content, content_type, metadata):
        record = {
            "object_id": "obj_test123",
            "owner_id": owner_id,
            "name": name,
            "content_type": content_type,
            "size_bytes": len(content.encode("utf-8")),
            "metadata": metadata,
            "s3_key": f"objects/{owner_id}/obj_test123",
            "created_at": "2026-05-24T21:00:00Z",
        }
        event = {"event_id": "evt_test123", "event_type": "ObjectCreated", "owner_id": owner_id, "object_id": record["object_id"], "status": "pending", "attempts": 0}
        self.objects[record["object_id"]] = {**record, "content": content}
        self.events.append(event)
        return {**record, "event": event}

    def list_objects(self, *, owner_id, limit=25, cursor=None, category=None):
        items = [
            {k: v for k, v in item.items() if k != "content"}
            for item in self.objects.values()
            if item["owner_id"] == owner_id
        ]
        if category:
            items = [item for item in items if item.get("metadata", {}).get("category") == category]
        page = items[:limit]
        return {"count": len(page), "objects": page, "next_cursor": None}

    def get_object(self, *, owner_id, object_id):
        item = self.objects.get(object_id)
        if not item or item["owner_id"] != owner_id:
            return None
        return dict(item)

    def list_events(self, *, owner_id, status=None, limit=25):
        events = [event for event in self.events if event["owner_id"] == owner_id]
        if status:
            events = [event for event in events if event["status"] == status]
        return {"count": len(events[:limit]), "events": events[:limit]}

    def process_pending_events(self, *, owner_id, limit=25):
        processed = []
        for event in self.events:
            if event["owner_id"] == owner_id and event["status"] == "pending" and len(processed) < limit:
                event["status"] = "processed"
                event["attempts"] += 1
                processed.append(dict(event))
        return {"processed_count": len(processed), "events": processed}

    def mark_event_failed(self, *, owner_id, event_id, reason, code):
        for event in self.events:
            if event["owner_id"] == owner_id and event["event_id"] == event_id:
                event["status"] = "failed"
                event["attempts"] = max(int(event.get("attempts") or 0), 1)
                event["failure"] = {"code": code, "reason": reason, "retryable": True}
                event.setdefault("detail", {})["failure_code"] = code
                event.setdefault("detail", {})["failure_reason"] = reason
                return dict(event)
        raise AssertionError(f"event {event_id} not found")


def invoke(handler, method, path, body=None, headers=None, query=None):
    event = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "requestContext": {"requestId": "unit-request", "http": {"method": method, "path": path}},
        "headers": headers or {},
        "queryStringParameters": query or {},
        "body": json.dumps(body) if isinstance(body, dict) else body,
        "isBase64Encoded": False,
    }
    return handler(event, None)


def parse_body(response):
    return json.loads(response["body"])


def test_health_endpoint_returns_portfolio_status():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "GET", "/health")

    assert response["statusCode"] == 200
    body = parse_body(response)
    assert body["ok"] is True
    assert body["service"] == "floci-cloud-lab-api"
    assert body["runtime"] == "local-floci"
    assert body["request_id"] == "unit-request"


def test_ops_status_endpoint_returns_ready():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "GET", "/ops/status")

    assert response["statusCode"] == 200
    body = parse_body(response)
    assert body["status"] == "ready"
    assert body["mode"] == "local"
    assert body["environment"]["local_only"] is True
    assert body["environment"]["emulator"] == "floci"
    assert body["emulator"]["endpoint"] == "http://localhost:4566"
    assert body["emulator"]["status"] == "online"
    assert body["database"]["status"] == "online"
    assert body["storage"]["engine"] == "S3 (Local)"
    components = {component["id"]: component for component in body["components"]}
    assert set(components) == {"api", "storage", "database", "observability"}
    assert components["api"]["aws_equivalent"] == "AWS::Lambda::Function"
    assert "event-outbox" in components["database"]["capabilities"]
    assert body["safety"] == {
        "local_only": True,
        "uses_real_cloud": False,
        "uses_real_credentials": False,
        "allows_shell_execution": False,
        "bounded_mutations_only": True,
    }
    assert body["dashboard"]["recommended_refresh_seconds"] == 5
    assert body["dashboard"]["primary_actions"][1]["path"] == "/events/process?limit=10"
    assert body["request_id"] == "unit-request"


def test_ops_resources_endpoint_returns_known_resources():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "GET", "/ops/resources")

    assert response["statusCode"] == 200
    body = parse_body(response)
    resources = body["resources"]
    assert len(resources) == 4
    by_id = {resource["id"]: resource for resource in resources}
    assert set(by_id) == {"api-function", "objects-bucket", "metadata-table", "app-logs"}
    assert by_id["objects-bucket"]["name"] == "floci-cloud-lab-local-objects"
    assert by_id["objects-bucket"]["type"] == "AWS::S3::Bucket"
    assert by_id["objects-bucket"]["aws_equivalent"]["service"] == "s3"
    assert by_id["metadata-table"]["name"] == "floci-cloud-lab-local-metadata"
    assert by_id["metadata-table"]["aws_equivalent"]["service"] == "dynamodb"
    assert by_id["app-logs"]["name"] == "/floci-cloud-lab/local/app"
    assert by_id["api-function"]["type"] == "AWS::Lambda::Function"
    assert all(resource["status"] == "available" for resource in resources)
    assert all(resource["safety"]["local_only"] is True for resource in resources)
    assert body["summary"] == {"count": 4, "available": 4, "degraded": 0, "offline": 0, "local_only": True}
    assert {category["id"] for category in body["categories"]} == {"compute", "storage", "database", "observability"}
    assert body["request_id"] == "unit-request"


def test_ops_session_endpoint_describes_debugging_wedge():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "GET", "/ops/session", headers={"x-floci-user": "lucas"})

    assert response["statusCode"] == 200
    body = parse_body(response)
    assert body["session"]["id"] == "local-lucas"
    assert body["session"]["mode"] == "local"
    assert body["positioning"] == "local-cloud-workflow-debugger"
    assert body["adapter"]["name"] == "floci"
    assert body["adapter"]["endpoint"] == "http://localhost:4566"
    assert body["safety"]["uses_real_cloud"] is False
    assert body["safety"]["allows_shell_execution"] is False
    capability_ids = {capability["id"] for capability in body["capabilities"]}
    assert {"flow-traces", "payload-inspection", "bounded-replay", "namespace-reset", "report-export"}.issubset(capability_ids)
    assert [node["id"] for node in body["service_map"]] == ["client", "api", "object-store", "metadata-store", "event-outbox", "processor"]
    assert body["request_id"] == "unit-request"


def test_demo_trace_endpoint_creates_replayable_flow_trace():
    repo = InMemoryRepository()
    handler = create_handler(repository=repo)

    response = invoke(handler, "POST", "/ops/demo/trace", headers={"x-floci-user": "lucas"})

    assert response["statusCode"] == 201
    body = parse_body(response)
    trace = body["trace"]
    assert trace["id"].startswith("trace_obj_test123")
    assert trace["owner_id"] == "lucas"
    assert trace["status"] == "complete"
    assert trace["summary"] == "request stored object, indexed metadata, emitted event, processed outbox"
    assert trace["artifact"]["object_id"] == "obj_test123"
    assert trace["artifact"]["event_id"] == "evt_test123"
    assert [step["id"] for step in trace["steps"]] == ["request", "payload", "object-store", "metadata", "outbox", "processor"]
    assert all(step["status"] == "ok" for step in trace["steps"])
    assert trace["commands"][0]["label"] == "replay object create"
    assert "curl" in trace["commands"][0]["command"]
    assert body["request_id"] == "unit-request"

    events = repo.list_events(owner_id="lucas")
    assert events["events"][0]["status"] == "processed"


def test_ops_traces_endpoint_returns_recent_trace_summaries_from_events():
    repo = InMemoryRepository()
    repo.create_object(owner_id="lucas", name="demo.md", content="hello", content_type="text/markdown", metadata={"category": "demo"})
    handler = create_handler(repository=repo)

    response = invoke(handler, "GET", "/ops/traces", headers={"x-floci-user": "lucas"})

    assert response["statusCode"] == 200
    body = parse_body(response)
    assert body["data"]["count"] == 1
    trace = body["data"]["traces"][0]
    assert trace["id"] == "trace_obj_test123_evt_test123"
    assert trace["status"] == "pending"
    assert trace["method"] == "POST"
    assert trace["path"] == "/objects"
    assert trace["artifact"]["object_id"] == "obj_test123"
    assert trace["artifact"]["event_id"] == "evt_test123"
    assert trace["links"]["detail"] == "/ops/traces/trace_obj_test123_evt_test123"


def test_ops_trace_detail_endpoint_returns_causal_steps():
    repo = InMemoryRepository()
    repo.create_object(owner_id="lucas", name="demo.md", content="hello", content_type="text/markdown", metadata={"category": "demo"})
    handler = create_handler(repository=repo)

    response = invoke(handler, "GET", "/ops/traces/trace_obj_test123_evt_test123", headers={"x-floci-user": "lucas"})

    assert response["statusCode"] == 200
    trace = parse_body(response)["trace"]
    assert trace["id"] == "trace_obj_test123_evt_test123"
    assert trace["status"] == "pending"
    assert trace["steps"][-1]["id"] == "processor"
    assert trace["steps"][-1]["status"] == "waiting"
    assert trace["commands"][1]["label"] == "process pending events"
    assert trace["commands"][1]["kind"] == "curl"
    assert "/events/process" in trace["commands"][1]["command"]


def test_ops_trace_report_endpoint_returns_sanitized_report():
    repo = InMemoryRepository()
    repo.create_object(owner_id="lucas", name="demo.md", content="hello", content_type="text/markdown", metadata={"category": "demo"})
    handler = create_handler(repository=repo)

    response = invoke(handler, "GET", "/ops/report", headers={"x-floci-user": "lucas"})

    assert response["statusCode"] == 200
    body = parse_body(response)
    assert body["report"]["format"] == "floci.trace-report.v1"
    assert body["report"]["trace"]["id"] == "trace_obj_test123_evt_test123"
    assert body["report"]["safety"]["sanitized"] is True
    assert body["report"]["reproduction"]["local_only"] is True


def test_ops_trace_report_endpoint_can_select_trace_id():
    repo = InMemoryRepository()
    repo.create_object(owner_id="lucas", name="demo.md", content="hello", content_type="text/markdown", metadata={"category": "demo"})
    handler = create_handler(repository=repo)

    response = invoke(handler, "GET", "/ops/report", headers={"x-floci-user": "lucas"}, query={"trace_id": "trace_obj_test123_evt_test123"})

    assert response["statusCode"] == 200
    assert parse_body(response)["report"]["trace"]["id"] == "trace_obj_test123_evt_test123"


def test_broken_trace_demo_creates_failed_flow_that_is_reportable():
    repo = InMemoryRepository()
    handler = create_handler(repository=repo)

    response = invoke(handler, "POST", "/ops/demo/broken-trace", headers={"x-floci-user": "lucas"})

    assert response["statusCode"] == 201
    trace = parse_body(response)["trace"]
    assert trace["status"] == "failed"
    assert trace["failure"]["code"] == "processor.validation_failed"
    assert trace["steps"][-1]["id"] == "processor"
    assert trace["steps"][-1]["status"] == "failed"
    assert "missing required metadata" in trace["steps"][-1]["detail"]
    assert trace["actions"][0]["id"] == "inspect-payload"
    assert trace["actions"][1]["id"] == "export-report"

    detail = invoke(handler, "GET", f"/ops/traces/{trace['id']}", headers={"x-floci-user": "lucas"})
    assert detail["statusCode"] == 200
    assert parse_body(detail)["trace"]["status"] == "failed"

    report = invoke(handler, "GET", "/ops/report", headers={"x-floci-user": "lucas"}, query={"trace_id": trace["id"]})
    assert report["statusCode"] == 200
    assert parse_body(report)["report"]["trace"]["failure"]["retryable"] is True


def test_ops_traces_endpoint_can_filter_failed_broken_flows():
    repo = InMemoryRepository()
    handler = create_handler(repository=repo)
    invoke(handler, "POST", "/ops/demo/broken-trace", headers={"x-floci-user": "lucas"})

    response = invoke(handler, "GET", "/ops/traces", headers={"x-floci-user": "lucas"}, query={"status": "failed"})

    assert response["statusCode"] == 200
    traces = parse_body(response)["data"]["traces"]
    assert len(traces) == 1
    assert traces[0]["status"] == "failed"
    assert traces[0]["summary"] == "request stored object, indexed metadata, emitted event, processor failed with actionable reason"


def test_create_object_validates_required_name():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "POST", "/objects", {"content": "hello"}, headers={"content-type": "application/json"})

    assert response["statusCode"] == 400
    body = parse_body(response)
    assert body["error"]["code"] == "validation_error"
    assert "name" in body["error"]["message"]
    assert body["request_id"] == "unit-request"


def test_create_object_rejects_non_json_content_type():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "POST", "/objects", '{"name":"x","content":"y"}', headers={"content-type": "text/plain"})

    assert response["statusCode"] == 415
    assert parse_body(response)["error"]["code"] == "unsupported_media_type"


def test_create_object_rejects_large_content():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(
        handler,
        "POST",
        "/objects",
        {"name": "big.txt", "content": "x" * 256_001},
        headers={"content-type": "application/json"},
    )

    assert response["statusCode"] == 413
    assert parse_body(response)["error"]["code"] == "payload_too_large"


def test_create_list_and_get_object_round_trip():
    repo = InMemoryRepository()
    handler = create_handler(repository=repo)

    created = invoke(
        handler,
        "POST",
        "/objects",
        {
            "name": "demo-note.txt",
            "content": "hello from the local cloud lab",
            "content_type": "text/plain",
            "metadata": {"source": "unit-test"},
        },
        headers={"x-floci-user": "lucas", "content-type": "application/json"},
    )

    assert created["statusCode"] == 201
    assert created["headers"]["x-request-id"] == "unit-request"
    created_body = parse_body(created)
    assert created_body["data"]["object_id"] == "obj_test123"
    assert created_body["data"]["owner_id"] == "lucas"
    assert created_body["data"]["metadata"] == {"source": "unit-test"}

    listed = invoke(handler, "GET", "/objects", headers={"x-floci-user": "lucas"})
    assert listed["statusCode"] == 200
    listed_body = parse_body(listed)
    assert listed_body["data"]["count"] == 1
    assert listed_body["data"]["objects"][0]["name"] == "demo-note.txt"

    fetched = invoke(handler, "GET", "/objects/obj_test123", headers={"x-floci-user": "lucas"})
    assert fetched["statusCode"] == 200
    fetched_body = parse_body(fetched)
    assert fetched_body["data"]["content"] == "hello from the local cloud lab"


def test_options_returns_cors_headers_without_body():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "OPTIONS", "/objects")

    assert response["statusCode"] == 204
    assert response["body"] == ""
    assert response["headers"]["access-control-allow-methods"] == "GET,POST,OPTIONS"


def test_unknown_route_returns_404():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "DELETE", "/objects/obj_test123")

    assert response["statusCode"] == 404
    assert parse_body(response)["error"]["code"] == "not_found"


def test_local_dependency_errors_are_actionable_not_internal_errors():
    handler = create_handler(repository=UnprovisionedLocalRepository())

    response = invoke(
        handler,
        "POST",
        "/ops/demo/broken-trace",
        headers={"x-floci-user": "lucas", "content-type": "application/json"},
    )

    assert response["statusCode"] == 503
    body = parse_body(response)
    assert body["error"]["code"] == "local_dependency_unavailable"
    assert "local Floci resources are not provisioned" in body["error"]["message"]
    assert "terraform apply" not in body["error"]["message"]


def test_create_object_emits_event_and_worker_processes_it():
    repo = InMemoryRepository()
    handler = create_handler(repository=repo)

    created = invoke(
        handler,
        "POST",
        "/objects",
        {"name": "event.txt", "content": "event me"},
        headers={"x-floci-user": "lucas", "content-type": "application/json"},
    )
    assert created["statusCode"] == 201
    assert parse_body(created)["data"]["event"]["event_type"] == "ObjectCreated"

    listed = invoke(handler, "GET", "/events", headers={"x-floci-user": "lucas"})
    assert listed["statusCode"] == 200
    assert parse_body(listed)["data"]["events"][0]["status"] == "pending"

    processed = invoke(handler, "POST", "/events/process", headers={"x-floci-user": "lucas"})
    assert processed["statusCode"] == 200
    assert parse_body(processed)["data"]["processed_count"] == 1

    processed_again = invoke(handler, "POST", "/events/process", headers={"x-floci-user": "lucas"})
    assert parse_body(processed_again)["data"]["processed_count"] == 0
