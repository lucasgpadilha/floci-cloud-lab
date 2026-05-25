from __future__ import annotations

import hashlib
import re
from typing import Any

_SAFE_SEGMENT_RE = re.compile(r"[^a-z0-9._-]+")
_REPEAT_DASH_RE = re.compile(r"-+")


def content_sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def build_object_key(*, owner_id: str, object_id: str, name: str) -> str:
    return f"objects/{safe_key_segment(owner_id)}/{safe_object_id(object_id)}/{safe_filename(name)}"


def safe_object_id(value: str) -> str:
    normalized = _SAFE_SEGMENT_RE.sub("-", value.strip().lower())
    normalized = _REPEAT_DASH_RE.sub("-", normalized).strip("-.")
    return normalized or "unknown"


def safe_key_segment(value: str) -> str:
    normalized = value.strip().lower().replace("_", "-")
    normalized = _SAFE_SEGMENT_RE.sub("-", normalized)
    normalized = _REPEAT_DASH_RE.sub("-", normalized).replace("-.", ".").strip("-._")
    return normalized or "unknown"


def safe_filename(name: str) -> str:
    filename = name.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    return safe_key_segment(filename)


def build_s3_metadata(*, owner_id: str, object_id: str, content: bytes, user_metadata: dict[str, Any]) -> dict[str, str]:
    metadata = {
        "owner-id": owner_id,
        "object-id": object_id,
        "sha256": content_sha256_hex(content),
    }
    for key, value in sorted(user_metadata.items()):
        metadata[f"user-{safe_key_segment(str(key))}"] = str(value)
    return metadata


def validate_retrieved_object_integrity(*, content: bytes, metadata: dict[str, str]) -> bool:
    expected = metadata.get("sha256")
    if not expected:
        return False
    return content_sha256_hex(content) == expected
