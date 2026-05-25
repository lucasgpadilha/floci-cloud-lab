import json
import os

import pytest
import requests

from app.backend.functions.api import create_handler
from app.backend.functions.repository import AwsObjectRepository, aws_clients_from_env

ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
BUCKET = os.getenv("FLOCI_OBJECT_BUCKET", "floci-cloud-lab-local-objects")
TABLE = os.getenv("FLOCI_METADATA_TABLE", "floci-cloud-lab-local-metadata")


def floci_is_reachable():
    try:
        response = requests.get(f"{ENDPOINT.rstrip('/')}/_localstack/health", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


pytestmark = pytest.mark.skipif(
    not floci_is_reachable(),
    reason=f"Floci endpoint is not reachable at {ENDPOINT}",
)


def invoke(handler, method, path, body=None, headers=None, query=None):
    event = {
        "requestContext": {"http": {"method": method, "path": path}},
        "headers": {"content-type": "application/json", **(headers or {})},
        "queryStringParameters": query or {},
        "body": json.dumps(body) if isinstance(body, dict) else body,
        "isBase64Encoded": False,
    }
    return handler(event, None)


def parse_body(response):
    return json.loads(response["body"])


def test_object_create_emits_and_processes_outbox_event_in_floci():
    clients = aws_clients_from_env()
    repo = AwsObjectRepository(
        s3_client=clients.s3,
        dynamodb_resource=clients.dynamodb,
        bucket_name=BUCKET,
        table_name=TABLE,
    )
    handler = create_handler(repository=repo)
    owner = "integration-events-user"

    created = invoke(
        handler,
        "POST",
        "/objects",
        {
            "name": "event-proof.txt",
            "content": "event-driven portfolio evidence",
            "content_type": "text/plain",
            "metadata": {"category": "events", "test": "eventing"},
        },
        headers={"x-floci-user": owner},
    )
    assert created["statusCode"] == 201
    created_event = parse_body(created)["data"]["event"]
    assert created_event["event_type"] == "ObjectCreated"
    assert created_event["status"] == "pending"

    pending = invoke(handler, "GET", "/events", headers={"x-floci-user": owner}, query={"status": "pending"})
    assert pending["statusCode"] == 200
    pending_events = parse_body(pending)["data"]["events"]
    assert any(event["event_id"] == created_event["event_id"] for event in pending_events)

    processed = invoke(handler, "POST", "/events/process", headers={"x-floci-user": owner})
    assert processed["statusCode"] == 200
    processed_body = parse_body(processed)["data"]
    assert processed_body["processed_count"] >= 1
    assert any(event["event_id"] == created_event["event_id"] and event["status"] == "processed" for event in processed_body["events"])

    processed_again = invoke(handler, "POST", "/events/process", headers={"x-floci-user": owner})
    assert processed_again["statusCode"] == 200
    assert parse_body(processed_again)["data"]["processed_count"] == 0
