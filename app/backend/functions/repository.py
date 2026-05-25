from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Protocol
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Key
from botocore.config import Config


DEFAULT_ENDPOINT = "http://localhost:4566"
DEFAULT_REGION = "us-east-1"
DEFAULT_BUCKET = "floci-cloud-lab-local-objects"
DEFAULT_TABLE = "floci-cloud-lab-local-metadata"

BASE_CONFIG = Config(
    retries={"total_max_attempts": 2, "mode": "standard"},
    connect_timeout=3,
    read_timeout=10,
)


class ObjectRepository(Protocol):
    def create_object(
        self,
        *,
        owner_id: str,
        name: str,
        content: str,
        content_type: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]: ...

    def list_objects(self, *, owner_id: str) -> list[dict[str, Any]]: ...

    def get_object(self, *, owner_id: str, object_id: str) -> dict[str, Any] | None: ...


@dataclass(frozen=True)
class AwsClients:
    s3: Any
    dynamodb: Any


def aws_clients_from_env() -> AwsClients:
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", DEFAULT_ENDPOINT)
    region_name = os.getenv("AWS_DEFAULT_REGION", DEFAULT_REGION)
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "test")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "test")

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=BASE_CONFIG.merge(Config(s3={"addressing_style": "path"})),
    )
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=BASE_CONFIG,
    )
    return AwsClients(s3=s3, dynamodb=dynamodb)


def repository_from_env() -> "AwsObjectRepository":
    clients = aws_clients_from_env()
    return AwsObjectRepository(
        s3_client=clients.s3,
        dynamodb_resource=clients.dynamodb,
        bucket_name=os.getenv("FLOCI_OBJECT_BUCKET", DEFAULT_BUCKET),
        table_name=os.getenv("FLOCI_METADATA_TABLE", DEFAULT_TABLE),
    )


class AwsObjectRepository:
    def __init__(self, *, s3_client: Any, dynamodb_resource: Any, bucket_name: str, table_name: str):
        self._s3 = s3_client
        self._table = dynamodb_resource.Table(table_name)
        self._bucket_name = bucket_name

    def create_object(
        self,
        *,
        owner_id: str,
        name: str,
        content: str,
        content_type: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        object_id = f"obj_{uuid4().hex}"
        created_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        content_bytes = content.encode("utf-8")
        s3_key = f"objects/{owner_id}/{object_id}/{name}"

        self._s3.put_object(
            Bucket=self._bucket_name,
            Key=s3_key,
            Body=content_bytes,
            ContentType=content_type,
            Metadata={"owner_id": owner_id, "object_id": object_id},
        )

        record = {
            "pk": f"OWNER#{owner_id}",
            "sk": f"OBJECT#{object_id}",
            "object_id": object_id,
            "owner_id": owner_id,
            "name": name,
            "content_type": content_type,
            "size_bytes": len(content_bytes),
            "metadata": metadata,
            "s3_bucket": self._bucket_name,
            "s3_key": s3_key,
            "created_at": created_at,
        }
        self._table.put_item(Item=record)
        return _public_record(record)

    def list_objects(self, *, owner_id: str) -> list[dict[str, Any]]:
        response = self._table.query(
            KeyConditionExpression=Key("pk").eq(f"OWNER#{owner_id}") & Key("sk").begins_with("OBJECT#"),
            ScanIndexForward=False,
        )
        return [_public_record(item) for item in response.get("Items", [])]

    def get_object(self, *, owner_id: str, object_id: str) -> dict[str, Any] | None:
        response = self._table.get_item(
            Key={"pk": f"OWNER#{owner_id}", "sk": f"OBJECT#{object_id}"},
        )
        record = response.get("Item")
        if not record:
            return None

        obj = self._s3.get_object(Bucket=record["s3_bucket"], Key=record["s3_key"])
        try:
            content = obj["Body"].read().decode("utf-8")
        finally:
            obj["Body"].close()

        public = _public_record(record)
        public["content"] = content
        return public


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    hidden = {"pk", "sk"}
    return {key: _to_json_safe(value) for key, value in record.items() if key not in hidden}


def _to_json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)
    if isinstance(value, dict):
        return {str(key): _to_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_json_safe(item) for item in value]
    return value
