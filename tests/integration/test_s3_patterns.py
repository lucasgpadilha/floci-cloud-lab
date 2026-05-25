import os

import pytest
import requests

from app.backend.functions.repository import AwsObjectRepository, aws_clients_from_env
from app.backend.functions.storage import content_sha256_hex


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


def test_s3_upload_preserves_content_type_metadata_integrity_and_presigned_url():
    clients = aws_clients_from_env()
    repo = AwsObjectRepository(
        s3_client=clients.s3,
        dynamodb_resource=clients.dynamodb,
        bucket_name=BUCKET,
        table_name=TABLE,
    )

    created = repo.create_object(
        owner_id="s3-pattern-user",
        name="S3 Pattern Proof.txt",
        content="S3 integrity round trip through Floci",
        content_type="text/plain; charset=utf-8",
        metadata={"category": "s3", "source": "integration", "ttl_days": 7},
    )

    assert created["s3_key"].startswith("objects/s3-pattern-user/")
    assert created["s3_key"].endswith("/s3-pattern-proof.txt")
    assert created["sha256"] == content_sha256_hex(b"S3 integrity round trip through Floci")

    s3_object = clients.s3.get_object(Bucket=BUCKET, Key=created["s3_key"])
    try:
        body = s3_object["Body"].read()
    finally:
        s3_object["Body"].close()

    assert body == b"S3 integrity round trip through Floci"
    assert s3_object["ContentType"] == "text/plain; charset=utf-8"
    assert s3_object["Metadata"]["sha256"] == created["sha256"]
    assert s3_object["Metadata"]["user-category"] == "s3"
    assert s3_object["Metadata"]["user-ttl-days"] == "7"

    fetched = repo.get_object(owner_id="s3-pattern-user", object_id=created["object_id"])
    assert fetched is not None
    assert fetched["integrity_verified"] is True
    assert fetched["s3_content_type"] == "text/plain; charset=utf-8"

    presigned_url = clients.s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": created["s3_key"]},
        ExpiresIn=300,
    )
    assert presigned_url.startswith(ENDPOINT)
    assert "Signature=" in presigned_url or "X-Amz-Signature=" in presigned_url
