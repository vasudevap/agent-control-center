from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from atlas_api.core.errors import ApiError

DEFAULT_PAGE_LIMIT = 50
MAX_PAGE_LIMIT = 100
_IDEMPOTENCY_KEY_PATTERN = re.compile(r"[!-~]{16,128}")


class PaginationParameters(BaseModel):
    cursor: str | None = Field(default=None, min_length=1, max_length=512)
    limit: int = Field(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT)


@dataclass(frozen=True)
class RequestFingerprint:
    method: str
    path_query: str
    body_sha256: str


def success_payload(data: Any, *, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"data": data}
    if meta:
        payload["meta"] = meta
    return payload


def encode_cursor(values: dict[str, str]) -> str:
    serialized = json.dumps(values, separators=(",", ":"), sort_keys=True).encode()
    return base64.urlsafe_b64encode(serialized).decode().rstrip("=")


def decode_cursor(cursor: str) -> dict[str, str]:
    padding = "=" * (-len(cursor) % 4)
    try:
        decoded = base64.urlsafe_b64decode(cursor + padding)
        values = json.loads(decoded)
    except (ValueError, json.JSONDecodeError) as exc:
        raise ApiError(
            status_code=422,
            code="pagination_cursor_invalid",
            message="Pagination cursor is invalid.",
        ) from exc
    if not isinstance(values, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in values.items()
    ):
        raise ApiError(
            status_code=422,
            code="pagination_cursor_invalid",
            message="Pagination cursor is invalid.",
        )
    return values


def validate_filter_fields(
    filters: dict[str, str],
    *,
    allowed_fields: set[str],
) -> dict[str, str]:
    unknown_fields = sorted(set(filters) - allowed_fields)
    if unknown_fields:
        raise ApiError(
            status_code=422,
            code="filter_field_unsupported",
            message="One or more filter fields are not supported.",
            details={"fields": unknown_fields},
        )
    return filters


def validate_idempotency_key(key: str | None) -> str:
    if key is None or _IDEMPOTENCY_KEY_PATTERN.fullmatch(key) is None:
        raise ApiError(
            status_code=422,
            code="idempotency_key_invalid",
            message="Idempotency-Key must contain 16 to 128 visible ASCII characters.",
        )
    return key


def request_fingerprint(
    method: str, path_query: str, body: bytes
) -> RequestFingerprint:
    return RequestFingerprint(
        method=method.upper(),
        path_query=path_query,
        body_sha256=hashlib.sha256(body).hexdigest(),
    )


def rate_limit_error(retry_after_seconds: int) -> ApiError:
    return ApiError(
        status_code=429,
        code="rate_limit_exceeded",
        message="Request rate limit exceeded.",
        headers={"Retry-After": str(retry_after_seconds)},
    )
