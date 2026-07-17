from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from atlas_api.core.config import Settings
from atlas_api.core.contracts import (
    DEFAULT_PAGE_LIMIT,
    MAX_PAGE_LIMIT,
    PaginationParameters,
    decode_cursor,
    encode_cursor,
    rate_limit_error,
    request_fingerprint,
    validate_filter_fields,
    validate_idempotency_key,
)
from atlas_api.core.errors import ApiError, error_payload
from atlas_api.main import create_app


def test_pagination_uses_bounded_limit_and_opaque_cursor() -> None:
    assert PaginationParameters().limit == DEFAULT_PAGE_LIMIT
    assert PaginationParameters(limit=MAX_PAGE_LIMIT).limit == MAX_PAGE_LIMIT
    cursor = encode_cursor({"created_at": "2026-07-17T00:00:00Z", "id": "fac_1"})
    assert "fac_1" not in cursor
    assert decode_cursor(cursor) == {
        "created_at": "2026-07-17T00:00:00Z",
        "id": "fac_1",
    }

    with pytest.raises(ApiError) as invalid_cursor:
        decode_cursor("not-a-cursor")
    assert invalid_cursor.value.code == "pagination_cursor_invalid"


def test_filter_and_idempotency_validation_fail_closed() -> None:
    assert validate_filter_fields({"status": "active"}, allowed_fields={"status"}) == {
        "status": "active"
    }
    with pytest.raises(ApiError) as unsupported_filter:
        validate_filter_fields({"unknown": "value"}, allowed_fields={"status"})
    assert unsupported_filter.value.code == "filter_field_unsupported"

    assert validate_idempotency_key("abcdefgh12345678") == "abcdefgh12345678"
    with pytest.raises(ApiError) as short_key:
        validate_idempotency_key("short")
    assert short_key.value.code == "idempotency_key_invalid"
    with pytest.raises(ApiError) as invalid_character:
        validate_idempotency_key("a" * 15 + "\n")
    assert invalid_character.value.code == "idempotency_key_invalid"


def test_request_fingerprint_binds_method_path_and_body() -> None:
    original = request_fingerprint("post", "/api/v1/example", b'{"value":1}')
    changed = request_fingerprint("post", "/api/v1/example", b'{"value":2}')

    assert original.method == "POST"
    assert original.body_sha256 != changed.body_sha256


def test_rate_limit_error_includes_retry_after_and_typed_details() -> None:
    error = rate_limit_error(30)
    assert error.status_code == 429
    assert error.headers == {"Retry-After": "30"}

    payload = error_payload(
        "example_error", "Example error.", details={"field": "example"}
    )
    assert payload["error"]["details"] == {"field": "example"}


def test_openapi_declares_contract_tags_and_hmac_security() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    schema = client.get("/openapi.json").json()

    assert {tag["name"] for tag in schema["tags"]} >= {
        "health",
        "api-health",
        "external-client",
        "knowledge",
    }
    assert "ExternalClientHmac" in schema["components"]["securitySchemes"]
    probe = schema["paths"]["/api/v1/external-client/authentication/probe"]["get"]
    assert probe["security"] == [{"ExternalClientHmac": []}]
