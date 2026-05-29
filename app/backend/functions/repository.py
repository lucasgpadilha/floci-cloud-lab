from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Protocol
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Key
from botocore.config import Config
from botocore.exceptions import ClientError

from app.backend.functions.events import build_object_created_event, mark_event_failed, mark_event_processed, public_event
from app.backend.functions.storage import (
    build_object_key,
    build_s3_metadata,
    content_sha256_hex,
    validate_retrieved_object_integrity,
)


DEFAULT_ENDPOINT = "http://localhost:4566"
DEFAULT_REGION = "us-east-1"
DEFAULT_BUCKET = "floci-cloud-lab-local-objects"
DEFAULT_TABLE = "floci-cloud-lab-local-metadata"
DEFAULT_PAGE_LIMIT = 25
MAX_PAGE_LIMIT = 100

BASE_CONFIG = Config(
    retries={"total_max_attempts": 2, "mode": "standard"},
    connect_timeout=3,
    read_timeout=10,
)


class ConditionalWriteFailed(RuntimeError):
    """Raised when DynamoDB rejects a conditional write."""


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

    def list_objects(
        self,
        *,
        owner_id: str,
        limit: int = DEFAULT_PAGE_LIMIT,
        cursor: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]: ...

    def get_object(self, *, owner_id: str, object_id: str) -> dict[str, Any] | None: ...

    def list_events(self, *, owner_id: str, status: str | None = None, limit: int = DEFAULT_PAGE_LIMIT) -> dict[str, Any]: ...

    def process_pending_events(self, *, owner_id: str, limit: int = DEFAULT_PAGE_LIMIT) -> dict[str, Any]: ...

    def mark_event_failed(self, *, owner_id: str, event_id: str, reason: str, code: str) -> dict[str, Any]: ...


@dataclass(frozen=True)
class AwsClients:
    s3: Any
    dynamodb: Any


@dataclass(frozen=True)
class ObjectRecordInput:
    owner_id: str
    object_id: str
    name: str
    content_type: str
    size_bytes: int
    metadata: dict[str, Any]
    bucket_name: str
    s3_key: str
    created_at: str
    sha256: str
    s3_version_id: str | None = None
    expires_at: int | None = None


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
        s3_key = build_object_key(owner_id=owner_id, object_id=object_id, name=name)
        content_sha256 = content_sha256_hex(content_bytes)
        expires_at = _ttl_from_metadata(metadata)

        put_response = self._s3.put_object(
            Bucket=self._bucket_name,
            Key=s3_key,
            Body=content_bytes,
            ContentType=content_type,
            Metadata=build_s3_metadata(
                owner_id=owner_id,
                object_id=object_id,
                content=content_bytes,
                user_metadata=metadata,
            ),
        )

        record = build_object_record(
            ObjectRecordInput(
                owner_id=owner_id,
                object_id=object_id,
                name=name,
                content_type=content_type,
                size_bytes=len(content_bytes),
                metadata=metadata,
                bucket_name=self._bucket_name,
                s3_key=s3_key,
                created_at=created_at,
                sha256=content_sha256,
                s3_version_id=put_response.get("VersionId"),
                expires_at=expires_at,
            )
        )
        try:
            self._table.put_item(
                Item=record,
                ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
            )
            event = build_object_created_event(object_record=record, created_at=created_at)
            self._table.put_item(
                Item=event,
                ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise ConditionalWriteFailed(f"object {object_id} or its event already exists") from exc
            raise
        public = _public_record(record)
        public["event"] = public_event(event)
        return public

    def list_objects(
        self,
        *,
        owner_id: str,
        limit: int = DEFAULT_PAGE_LIMIT,
        cursor: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        if category:
            items = self._query_objects_by_category(owner_id=owner_id, category=category)
        else:
            response = self._table.query(
                KeyConditionExpression=Key("pk").eq(f"OWNER#{owner_id}") & Key("sk").begins_with("OBJECT#"),
            )
            items = response.get("Items", [])
        public_items = [_public_record(item) for item in _sort_recent_first(items)]
        return page_items(public_items, limit=limit, cursor=cursor)

    def get_object(self, *, owner_id: str, object_id: str) -> dict[str, Any] | None:
        response = self._table.get_item(
            Key={"pk": f"OWNER#{owner_id}", "sk": f"OBJECT#{object_id}"},
        )
        record = response.get("Item")
        if not record:
            return None

        obj = self._s3.get_object(Bucket=record["s3_bucket"], Key=record["s3_key"])
        try:
            content_bytes = obj["Body"].read()
            content = content_bytes.decode("utf-8")
        finally:
            obj["Body"].close()

        public = _public_record(record)
        public["content"] = content
        public["s3_content_type"] = obj.get("ContentType")
        public["s3_metadata"] = obj.get("Metadata", {})
        public["integrity_verified"] = validate_retrieved_object_integrity(
            content=content_bytes,
            metadata=obj.get("Metadata", {}),
        )
        return public

    def _query_objects_by_category(self, *, owner_id: str, category: str) -> list[dict[str, Any]]:
        category_key = normalized_category(category)
        try:
            response = self._table.query(
                IndexName="gsi1",
                KeyConditionExpression=Key("gsi1pk").eq(f"OWNER#{owner_id}#CATEGORY#{category_key}"),
                ScanIndexForward=False,
            )
            return response.get("Items", [])
        except ClientError as exc:
            # The current local table was created before the optional GSI migration. Keep the
            # lab usable by falling back to an owner query, and document the emulator/local
            # migration gap in docs/dynamodb-data-model.md.
            if exc.response.get("Error", {}).get("Code") not in {"ValidationException", "ResourceNotFoundException"}:
                raise
            response = self._table.query(
                KeyConditionExpression=Key("pk").eq(f"OWNER#{owner_id}") & Key("sk").begins_with("OBJECT#"),
            )
            return [item for item in response.get("Items", []) if item.get("category") == category_key]

    def list_events(self, *, owner_id: str, status: str | None = None, limit: int = DEFAULT_PAGE_LIMIT) -> dict[str, Any]:
        response = self._table.query(
            KeyConditionExpression=Key("pk").eq(f"OWNER#{owner_id}") & Key("sk").begins_with("EVENT#"),
        )
        events = [_to_json_safe(public_event(item)) for item in _sort_recent_first(response.get("Items", []))]
        if status:
            events = [event for event in events if event.get("status") == status]
        return {"count": len(events[:limit]), "events": events[:limit]}

    def process_pending_events(self, *, owner_id: str, limit: int = DEFAULT_PAGE_LIMIT) -> dict[str, Any]:
        response = self._table.query(
            KeyConditionExpression=Key("pk").eq(f"OWNER#{owner_id}") & Key("sk").begins_with("EVENT#"),
        )
        pending = [item for item in _sort_recent_first(response.get("Items", [])) if item.get("status") == "pending"][:limit]
        processed = []
        for event in pending:
            updated = mark_event_processed(event)
            self._table.put_item(Item=updated)
            processed.append(_to_json_safe(public_event(updated)))
        return {"processed_count": len(processed), "events": processed}

    def mark_event_failed(self, *, owner_id: str, event_id: str, reason: str, code: str) -> dict[str, Any]:
        response = self._table.query(
            KeyConditionExpression=Key("pk").eq(f"OWNER#{owner_id}") & Key("sk").begins_with("EVENT#"),
            ConsistentRead=True,
        )
        for event in response.get("Items", []):
            if event.get("event_id") == event_id:
                updated = mark_event_failed(event, reason=reason, code=code)
                self._table.put_item(Item=updated)
                return _to_json_safe(public_event(updated))
        raise KeyError(f"event {event_id} was not found")


def build_object_record(record_input: ObjectRecordInput) -> dict[str, Any]:
    category = normalized_category(record_input.metadata.get("category"))
    record = {
        "pk": f"OWNER#{record_input.owner_id}",
        "sk": f"OBJECT#{record_input.object_id}",
        "object_id": record_input.object_id,
        "owner_id": record_input.owner_id,
        "name": record_input.name,
        "content_type": record_input.content_type,
        "size_bytes": record_input.size_bytes,
        "metadata": record_input.metadata,
        "category": category,
        "version": 1,
        "s3_bucket": record_input.bucket_name,
        "s3_key": record_input.s3_key,
        "sha256": record_input.sha256,
        "s3_version_id": record_input.s3_version_id,
        "created_at": record_input.created_at,
        "gsi1pk": f"OWNER#{record_input.owner_id}#CATEGORY#{category}",
        "gsi1sk": f"CREATED#{record_input.created_at}#OBJECT#{record_input.object_id}",
        "ttl_status": "scheduled" if record_input.expires_at else "none",
    }
    if record_input.expires_at:
        record["expires_at"] = record_input.expires_at
    return record


def normalized_category(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return "uncategorized"
    return value.strip().lower().replace(" ", "-")[:64]


def page_items(items: list[dict[str, Any]], *, limit: int, cursor: str | None) -> dict[str, Any]:
    safe_limit = max(1, min(int(limit or DEFAULT_PAGE_LIMIT), MAX_PAGE_LIMIT))
    start = decode_pagination_cursor(cursor)
    end = start + safe_limit
    page = items[start:end]
    next_cursor = encode_pagination_cursor(end) if end < len(items) else None
    return {"count": len(page), "objects": page, "next_cursor": next_cursor}


def encode_pagination_cursor(offset: int) -> str:
    payload = json.dumps({"offset": offset}, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii")


def decode_pagination_cursor(cursor: str | None) -> int:
    if not cursor:
        return 0
    try:
        payload = json.loads(base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8"))
        return max(0, int(payload.get("offset", 0)))
    except (ValueError, TypeError, json.JSONDecodeError):
        return 0


def _ttl_from_metadata(metadata: dict[str, Any]) -> int | None:
    ttl_days = metadata.get("ttl_days")
    if not isinstance(ttl_days, int) or ttl_days <= 0:
        return None
    return int((datetime.now(UTC) + timedelta(days=ttl_days)).timestamp())


def _sort_recent_first(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: (str(item.get("created_at", "")), str(item.get("object_id", ""))), reverse=True)


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    hidden = {"pk", "sk", "gsi1pk", "gsi1sk"}
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
