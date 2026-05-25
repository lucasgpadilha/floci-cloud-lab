import json

from app.backend.local_server import build_lambda_event


def test_build_lambda_event_maps_http_request_shape():
    event = build_lambda_event(
        method="POST",
        path="/objects",
        headers={"X-Floci-User": "lucas", "Content-Type": "application/json"},
        body=b'{"name":"demo.txt","content":"hello"}',
    )

    assert event["requestContext"]["http"]["method"] == "POST"
    assert event["requestContext"]["http"]["path"] == "/objects"
    assert event["headers"]["x-floci-user"] == "lucas"
    assert json.loads(event["body"]) == {"name": "demo.txt", "content": "hello"}
