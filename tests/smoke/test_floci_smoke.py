import os
import socket
import time
from uuid import uuid4

import boto3
import pytest
import requests
from botocore.config import Config


ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "test")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")


def _endpoint_is_reachable() -> bool:
    try:
        response = requests.get(f"{ENDPOINT.rstrip('/')}/_localstack/health", timeout=2)
        return response.status_code < 500
    except requests.RequestException:
        return False


pytestmark = pytest.mark.skipif(
    not _endpoint_is_reachable(),
    reason=f"Floci endpoint is not reachable at {ENDPOINT}",
)


BASE_CONFIG = Config(
    retries={"total_max_attempts": 2, "mode": "standard"},
    connect_timeout=3,
    read_timeout=10,
)


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=BASE_CONFIG.merge(Config(s3={"addressing_style": "path"})),
    )


def dynamodb_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=BASE_CONFIG,
    )


def test_floci_health_endpoint_returns_json_like_body():
    response = requests.get(f"{ENDPOINT.rstrip('/')}/_localstack/health", timeout=3)

    assert response.status_code == 200
    assert response.text.strip()


def test_s3_bucket_round_trip():
    s3 = s3_client()
    bucket = f"floci-cloud-lab-smoke-{uuid4().hex[:12]}"

    s3.create_bucket(Bucket=bucket)
    s3.put_object(Bucket=bucket, Key="smoke.txt", Body=b"hello from floci")
    response = s3.get_object(Bucket=bucket, Key="smoke.txt")
    try:
        body = response["Body"].read()
    finally:
        response["Body"].close()

    buckets = [entry["Name"] for entry in s3.list_buckets().get("Buckets", [])]
    assert bucket in buckets
    assert body == b"hello from floci"


def test_dynamodb_table_round_trip():
    dynamodb = dynamodb_resource()
    table_name = f"floci-cloud-lab-smoke-{uuid4().hex[:12]}"

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    # Floci returns quickly; avoid AWS waiter assumptions and poll using the resource API.
    for _ in range(10):
        if table.table_status in {"ACTIVE", "CREATING"}:
            break
        time.sleep(0.2)

    item = {"pk": "USER#local", "sk": "OBJECT#smoke", "message": "hello from floci"}
    table.put_item(Item=item)
    response = table.get_item(Key={"pk": item["pk"], "sk": item["sk"]})

    assert response.get("Item") == item
