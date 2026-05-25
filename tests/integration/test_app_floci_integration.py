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


def invoke(handler, method, path, body=None, headers=None):
    event = {
        "requestContext": {"http": {"method": method, "path": path}},
        "headers": headers or {},
        "body": json.dumps(body) if isinstance(body, dict) else body,
    }
    return handler(event, None)


def parse_body(response):
    return json.loads(response["body"])


def test_api_persists_object_metadata_and_content_in_floci():
    clients = aws_clients_from_env()
    repo = AwsObjectRepository(
        s3_client=clients.s3,
        dynamodb_resource=clients.dynamodb,
        bucket_name=BUCKET,
        table_name=TABLE,
    )
    handler = create_handler(repository=repo)

    created = invoke(
        handler,
        "POST",
        "/objects",
        {
            "name": "portfolio-proof.txt",
            "content": "stored through the app API on local Floci",
            "content_type": "text/plain",
            "metadata": {"test": "integration"},
        },
        headers={"x-floci-user": "integration-user"},
    )

    assert created["statusCode"] == 201
    created_body = parse_body(created)
    object_id = created_body["data"]["object_id"]
    assert created_body["data"]["s3_key"].startswith("objects/integration-user/")

    listed = invoke(handler, "GET", "/objects", headers={"x-floci-user": "integration-user"})
    listed_body = parse_body(listed)
    assert listed["statusCode"] == 200
    assert any(item["object_id"] == object_id for item in listed_body["data"]["objects"])

    fetched = invoke(
        handler,
        "GET",
        f"/objects/{object_id}",
        headers={"x-floci-user": "integration-user"},
    )
    fetched_body = parse_body(fetched)
    assert fetched["statusCode"] == 200
    assert fetched_body["data"]["content"] == "stored through the app API on local Floci"
    assert fetched_body["data"]["metadata"] == {"test": "integration"}
