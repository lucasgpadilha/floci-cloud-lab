from __future__ import annotations

from app.backend.functions.repository import ObjectRecordInput, build_object_record, decode_pagination_cursor, encode_pagination_cursor, page_items


def test_build_object_record_adds_version_category_gsi_and_ttl_fields():
    record_input = ObjectRecordInput(
        owner_id="lucas",
        object_id="obj_123",
        name="demo.txt",
        content_type="text/plain",
        size_bytes=12,
        metadata={"category": "notes", "source": "unit"},
        bucket_name="bucket",
        s3_key="objects/lucas/obj_123/demo.txt",
        created_at="2026-05-25T10:00:00Z",
        sha256="abc123",
        s3_version_id="version-1",
        expires_at=1790000000,
    )

    record = build_object_record(record_input)

    assert record["pk"] == "OWNER#lucas"
    assert record["sk"] == "OBJECT#obj_123"
    assert record["object_id"] == "obj_123"
    assert record["version"] == 1
    assert record["category"] == "notes"
    assert record["gsi1pk"] == "OWNER#lucas#CATEGORY#notes"
    assert record["gsi1sk"] == "CREATED#2026-05-25T10:00:00Z#OBJECT#obj_123"
    assert record["expires_at"] == 1790000000
    assert record["sha256"] == "abc123"
    assert record["s3_version_id"] == "version-1"


def test_build_object_record_defaults_category_and_ttl_when_absent():
    record = build_object_record(
        ObjectRecordInput(
            owner_id="lucas",
            object_id="obj_456",
            name="demo.txt",
            content_type="text/plain",
            size_bytes=1,
            metadata={},
            bucket_name="bucket",
            s3_key="objects/lucas/obj_456/demo.txt",
            created_at="2026-05-25T10:00:00Z",
            sha256="def456",
        )
    )

    assert record["category"] == "uncategorized"
    assert record["ttl_status"] == "none"
    assert "expires_at" not in record


def test_page_items_returns_limit_plus_next_cursor():
    items = [
        {"object_id": "a", "created_at": "2026-05-25T10:02:00Z"},
        {"object_id": "b", "created_at": "2026-05-25T10:01:00Z"},
        {"object_id": "c", "created_at": "2026-05-25T10:00:00Z"},
    ]

    first_page = page_items(items, limit=2, cursor=None)
    second_page = page_items(items, limit=2, cursor=first_page["next_cursor"])

    assert [item["object_id"] for item in first_page["objects"]] == ["a", "b"]
    assert first_page["count"] == 2
    assert first_page["next_cursor"] == encode_pagination_cursor(2)
    assert [item["object_id"] for item in second_page["objects"]] == ["c"]
    assert second_page["next_cursor"] is None


def test_decode_pagination_cursor_rejects_invalid_values():
    assert decode_pagination_cursor(None) == 0
    assert decode_pagination_cursor("not-base64") == 0
    assert decode_pagination_cursor(encode_pagination_cursor(5)) == 5
