from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApiError(Exception):
    status_code: int
    code: str
    message: str


class BadRequest(ApiError):
    def __init__(self, code: str, message: str):
        super().__init__(400, code, message)


class UnsupportedMediaType(ApiError):
    def __init__(self, message: str):
        super().__init__(415, "unsupported_media_type", message)


class PayloadTooLarge(ApiError):
    def __init__(self, message: str):
        super().__init__(413, "payload_too_large", message)


class NotFound(ApiError):
    def __init__(self, message: str):
        super().__init__(404, "not_found", message)
