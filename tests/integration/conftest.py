import os

import pytest


ENDPOINT = os.getenv("AWS_ENDPOINT_URL", os.getenv("FLOCI_ENDPOINT", "http://localhost:4566"))
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "test")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
LOCAL_ENDPOINTS = {"http://localhost:4566", "http://127.0.0.1:4566"}
BUCKET = os.getenv("FLOCI_OBJECT_BUCKET", "floci-cloud-lab-local-objects")
TABLE = os.getenv("FLOCI_METADATA_TABLE", "floci-cloud-lab-local-metadata")


def _local_app_resources_exist() -> bool:
    if ENDPOINT not in LOCAL_ENDPOINTS:
        return False

    try:
        import boto3
        from botocore.config import Config

        config = Config(retries={"total_max_attempts": 2, "mode": "standard"}, connect_timeout=2, read_timeout=3)
        s3 = boto3.client(
            "s3",
            endpoint_url=ENDPOINT,
            region_name=REGION,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            config=config.merge(Config(s3={"addressing_style": "path"})),
        )
        dynamodb = boto3.client(
            "dynamodb",
            endpoint_url=ENDPOINT,
            region_name=REGION,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            config=config,
        )
        s3.head_bucket(Bucket=BUCKET)
        dynamodb.describe_table(TableName=TABLE)
        return True
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    if _local_app_resources_exist():
        return

    reason = (
        "Floci app bucket/table are not present; run an approved local Terraform apply "
        "before resource-backed integration tests"
    )
    skip_marker = pytest.mark.skip(reason=reason)
    for item in items:
        if "tests/integration" in str(item.path):
            item.add_marker(skip_marker)
