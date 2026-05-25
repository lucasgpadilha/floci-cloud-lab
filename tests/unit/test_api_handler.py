import json

from app.backend.functions.api import create_handler


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


def invoke(handler, method, path, body=None, headers=None):
    event = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "requestContext": {"requestId": "unit-request", "http": {"method": method, "path": path}},
        "headers": headers or {},
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
