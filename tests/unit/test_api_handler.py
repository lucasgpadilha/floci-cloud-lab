import json

from app.backend.functions.api import create_handler


class InMemoryRepository:
    def __init__(self):
        self.objects = {}

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
        self.objects[record["object_id"]] = {**record, "content": content}
        return record

    def list_objects(self, *, owner_id):
        return [
            {k: v for k, v in item.items() if k != "content"}
            for item in self.objects.values()
            if item["owner_id"] == owner_id
        ]

    def get_object(self, *, owner_id, object_id):
        item = self.objects.get(object_id)
        if not item or item["owner_id"] != owner_id:
            return None
        return dict(item)


def invoke(handler, method, path, body=None, headers=None):
    event = {
        "requestContext": {"http": {"method": method, "path": path}},
        "headers": headers or {},
        "body": json.dumps(body) if isinstance(body, dict) else body,
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


def test_create_object_validates_required_name():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "POST", "/objects", {"content": "hello"})

    assert response["statusCode"] == 400
    body = parse_body(response)
    assert body["error"]["code"] == "validation_error"
    assert "name" in body["error"]["message"]


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
        headers={"x-floci-user": "lucas"},
    )

    assert created["statusCode"] == 201
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


def test_unknown_route_returns_404():
    handler = create_handler(repository=InMemoryRepository())

    response = invoke(handler, "DELETE", "/objects/obj_test123")

    assert response["statusCode"] == 404
    assert parse_body(response)["error"]["code"] == "not_found"
