from __future__ import annotations

from app.backend.functions.storage import (
    build_object_key,
    build_s3_metadata,
    content_sha256_hex,
    validate_retrieved_object_integrity,
)


def test_build_object_key_uses_owner_object_and_safe_filename():
    key = build_object_key(owner_id="Lucas Demo", object_id="obj_123", name="../Quarterly Report!.txt")

    assert key == "objects/lucas-demo/obj_123/quarterly-report.txt"


def test_build_s3_metadata_preserves_user_metadata_and_integrity_hash():
    metadata = build_s3_metadata(
        owner_id="lucas",
        object_id="obj_123",
        content=b"hello local S3",
        user_metadata={"category": "Notes", "unsafe key!": "kept readable", "ttl_days": 30},
    )

    assert metadata["owner-id"] == "lucas"
    assert metadata["object-id"] == "obj_123"
    assert metadata["sha256"] == content_sha256_hex(b"hello local S3")
    assert metadata["user-category"] == "Notes"
    assert metadata["user-unsafe-key"] == "kept readable"
    assert metadata["user-ttl-days"] == "30"


def test_validate_retrieved_object_integrity_compares_sha256_metadata():
    content = b"round trip"
    metadata = {"sha256": content_sha256_hex(content)}

    assert validate_retrieved_object_integrity(content=content, metadata=metadata) is True
    assert validate_retrieved_object_integrity(content=b"tampered", metadata=metadata) is False
