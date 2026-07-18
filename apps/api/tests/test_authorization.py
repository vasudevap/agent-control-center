from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr

from atlas_api.core.authorization import (
    ActorKind,
    AuthorizationContext,
    Channel,
    authorize,
)
from atlas_api.core.config import Settings
from atlas_api.core.external_request_signing import (
    ExternalRequestSignatureError,
    SignedExternalRequest,
    sign_request,
    verify_signature,
)


def signed_request(
    *, body: bytes = b"", key_id: str = "current"
) -> SignedExternalRequest:
    timestamp = int(datetime(2026, 7, 17, tzinfo=UTC).timestamp())
    unsigned = SignedExternalRequest(
        client_id="external-client-1",
        key_id=key_id,
        timestamp=timestamp,
        nonce="opaque-nonce",
        signature="",
        method="POST",
        path_query="/api/v1/example?filter=active",
        body=body,
    )
    secret = "next-secret" if key_id == "next" else "current-secret"
    return SignedExternalRequest(
        **{**unsigned.__dict__, "signature": sign_request(unsigned, secret)}
    )


def signing_settings() -> Settings:
    return Settings(
        external_client_id="external-client-1",
        external_client_key_id="current",
        external_client_secret=SecretStr("current-secret"),
        external_client_next_key_id="next",
        external_client_next_secret=SecretStr("next-secret"),
    )


def test_authorization_denies_by_default_and_preserves_actor_kind() -> None:
    denied = authorize(
        AuthorizationContext(
            actor_kind=ActorKind.HUMAN_OWNER,
            actor_id="owner-1",
            channel=Channel.DASHBOARD,
            resource="external_client_authentication",
            action="probe",
        )
    )
    assert not denied.allowed
    assert denied.reason_code == "authorization_denied"


def test_authorization_allows_only_explicit_external_probe() -> None:
    allowed = authorize(
        AuthorizationContext(
            actor_kind=ActorKind.EXTERNAL_CLIENT,
            actor_id="external-client-1",
            channel=Channel.EXTERNAL_PRODUCT_CLIENT,
            resource="external_client_authentication",
            action="probe",
            risk_level="low",
            environment="test",
        )
    )
    assert allowed.allowed


def test_authorization_allows_external_approval_fact_revalidation() -> None:
    allowed = authorize(
        AuthorizationContext(
            actor_kind=ActorKind.EXTERNAL_CLIENT,
            actor_id="external-client-1",
            channel=Channel.EXTERNAL_PRODUCT_CLIENT,
            resource="approval",
            action="revalidate_facts",
            risk_level="medium",
        )
    )

    assert allowed.allowed


def test_signatures_bind_body_and_enforce_timestamp_window() -> None:
    request = signed_request(body=b'{"state":"original"}')
    now = datetime(2026, 7, 17, tzinfo=UTC)
    verify_signature(request, signing_settings(), now=now)

    altered_request = SignedExternalRequest(
        **{**request.__dict__, "body": b'{"state":"altered"}'}
    )
    with pytest.raises(
        ExternalRequestSignatureError, match="external_client_signature_invalid"
    ):
        verify_signature(altered_request, signing_settings(), now=now)

    with pytest.raises(
        ExternalRequestSignatureError, match="external_client_timestamp_invalid"
    ):
        verify_signature(
            request,
            signing_settings(),
            now=now + timedelta(minutes=5, seconds=1),
        )


def test_rotation_accepts_current_and_next_but_rejects_unknown_key() -> None:
    now = datetime(2026, 7, 17, tzinfo=UTC)
    verify_signature(signed_request(key_id="current"), signing_settings(), now=now)
    verify_signature(signed_request(key_id="next"), signing_settings(), now=now)

    unknown = signed_request(key_id="retired")
    with pytest.raises(
        ExternalRequestSignatureError, match="external_client_key_unknown"
    ):
        verify_signature(unknown, signing_settings(), now=now)
