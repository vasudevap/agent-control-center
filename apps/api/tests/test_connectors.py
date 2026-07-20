from __future__ import annotations

import json
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.external_request_signing import SignedExternalRequest, sign_request
from atlas_api.db.base import Base
from atlas_api.main import create_app
from atlas_api.models.audit import AuditEvent
from atlas_api.models.connector import (
    ConnectorConnection,
    ConnectorCredentialReference,
    ConnectorOAuthState,
)
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.services import connectors as connector_service
from atlas_api.services.connectors import (
    DRIVE_SCOPE_FILE,
    GMAIL_SCOPE_MODIFY,
    REJECTED_GMAIL_SCOPE_FULL_MAILBOX,
    GoogleOAuthExchangeResult,
    authorize_connector_operation,
)

CLIENT_ID = "external-client-1"
KEY_ID = "current-key"
SECRET = "expected-signing-secret"
OWNER_ID = "usr_owner"


@pytest.fixture
def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine)


def configured_settings() -> Settings:
    return Settings(
        environment="test",
        external_client_id=CLIENT_ID,
        external_client_key_id=KEY_ID,
        external_client_secret=SecretStr(SECRET),
    )


def google_configured_settings() -> Settings:
    return Settings(
        environment="test",
        external_client_id=CLIENT_ID,
        external_client_key_id=KEY_ID,
        external_client_secret=SecretStr(SECRET),
        google_oauth_client_id="google-client-id",
        google_oauth_client_secret=SecretStr("google-client-secret"),
        google_oauth_redirect_uri="https://atlas.grafley.com/oauth/google/callback",
    )


def seed_owner(session: Session) -> None:
    session.add(
        User(
            user_id=OWNER_ID,
            email="owner@example.test",
            display_name="Owner",
            identity_provider="test",
            identity_subject="owner-subject",
            status="active",
        )
    )
    session.add(
        ExternalProductClient(
            external_client_id=CLIENT_ID,
            display_name="External Client",
            status="active",
            authentication_key_reference="keyref-1",
            human_owner_user_id=OWNER_ID,
        )
    )
    session.commit()


def signed_headers(
    method: str,
    path: str,
    *,
    nonce: str,
    body: bytes = b"",
) -> dict[str, str]:
    timestamp = int(datetime.now(UTC).timestamp())
    signed_request = SignedExternalRequest(
        client_id=CLIENT_ID,
        key_id=KEY_ID,
        timestamp=timestamp,
        nonce=nonce,
        signature="",
        method=method,
        path_query=path,
        body=body,
    )
    return {
        "X-Atlas-Client-Id": CLIENT_ID,
        "X-Atlas-Key-Id": KEY_ID,
        "X-Atlas-Timestamp": str(timestamp),
        "X-Atlas-Nonce": nonce,
        "X-Atlas-Signature": sign_request(signed_request, SECRET),
        "Content-Type": "application/json",
    }


def json_body(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def post_signed(
    client: TestClient,
    path: str,
    *,
    nonce: str,
    payload: dict[str, object],
) -> object:
    body = json_body(payload)
    return client.post(
        path,
        content=body,
        headers=signed_headers("POST", path, nonce=nonce, body=body),
    )


def get_signed(client: TestClient, path: str, *, nonce: str) -> object:
    return client.get(
        path,
        headers=signed_headers("GET", path, nonce=nonce),
    )


def oauth_state_from_url(authorization_url: str) -> str:
    parsed = urlparse(authorization_url)
    values = parse_qs(parsed.query)
    return values["state"][0]


def test_connector_metadata_is_registered_and_secret_free(
    database_factory: sessionmaker[Session],
) -> None:
    client = TestClient(create_app(configured_settings(), database_factory))

    response = get_signed(client, "/api/v1/connectors", nonce="connector-list")

    assert response.status_code == 200
    connectors = {item["connector_type"]: item for item in response.json()["data"]}
    assert connectors["gmail"]["required_scopes"]["gmail.create_draft"] == [
        GMAIL_SCOPE_MODIFY
    ]
    assert connectors["google_drive"]["required_scopes"]["drive.save_attachment"] == [
        DRIVE_SCOPE_FILE
    ]
    response_text = response.text.lower()
    assert "oauth_token" not in response_text
    assert "refresh_token" not in response_text
    assert "access_token" not in response_text
    assert "secret" not in response_text

    table_names = Base.metadata.tables
    assert "connector_connections" in table_names
    assert "connector_credential_references" in table_names
    assert "connector_oauth_states" in table_names


def test_oauth_start_rejects_broad_gmail_scope_and_audits_denial(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
    client = TestClient(create_app(configured_settings(), database_factory))

    response = post_signed(
        client,
        "/api/v1/connectors/gmail/oauth/start",
        nonce="gmail-broad-scope",
        payload={
            "requested_scopes": [GMAIL_SCOPE_MODIFY, REJECTED_GMAIL_SCOPE_FULL_MAILBOX],
            "redirect_uri": "https://client.example.test/oauth/callback",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "connector_scope_rejected"
    assert REJECTED_GMAIL_SCOPE_FULL_MAILBOX not in response.text
    with database_factory() as session:
        audit_event = session.scalar(
            select(AuditEvent).where(AuditEvent.action == "start_oauth")
        )
        assert audit_event is not None
        assert audit_event.result == "denied"
        assert audit_event.reason_code == "connector_scope_rejected"
        assert "token" not in json.dumps(audit_event.metadata_json).lower()


def test_fake_oauth_callback_creates_connection_without_exposing_credential_reference(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
    client = TestClient(create_app(configured_settings(), database_factory))

    start = post_signed(
        client,
        "/api/v1/connectors/gmail/oauth/start",
        nonce="gmail-oauth-start",
        payload={
            "requested_scopes": [GMAIL_SCOPE_MODIFY],
            "redirect_uri": "https://client.example.test/oauth/callback",
        },
    )
    assert start.status_code == 200
    state = oauth_state_from_url(start.json()["data"]["authorization_url"])

    callback = post_signed(
        client,
        "/api/v1/connectors/gmail/oauth/callback",
        nonce="gmail-oauth-callback",
        payload={
            "state": state,
            "authorization_code": "fake-provider-code",
            "account_identifier": "owner@example.test",
            "granted_scopes": [GMAIL_SCOPE_MODIFY],
            "display_name": "Owner Gmail",
        },
    )

    assert callback.status_code == 200
    data = callback.json()["data"]
    assert data["connector_type"] == "gmail"
    assert data["status"] == "connected"
    assert data["granted_scopes"] == [GMAIL_SCOPE_MODIFY]
    assert "credential_reference" not in callback.text
    assert "fake-provider-code" not in callback.text
    assert "token" not in callback.text.lower()

    with database_factory() as session:
        connection = session.scalar(select(ConnectorConnection))
        credential = session.scalar(select(ConnectorCredentialReference))
        state_record = session.scalar(select(ConnectorOAuthState))
        assert connection is not None
        assert credential is not None
        assert state_record is not None
        assert connection.credential_reference_id == credential.credential_reference_id
        assert credential.status == "active"
        assert state_record.status == "consumed"
        assert "fake-provider-code" not in json.dumps(credential.reference_label)


def test_google_oauth_callback_fails_closed_when_google_is_not_configured(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
    client = TestClient(create_app(configured_settings(), database_factory))

    start = post_signed(
        client,
        "/api/v1/connectors/gmail/oauth/start",
        nonce="google-unconfigured-start",
        payload={
            "requested_scopes": [GMAIL_SCOPE_MODIFY],
            "redirect_uri": "https://atlas.grafley.com/oauth/google/callback",
        },
    )
    state = oauth_state_from_url(start.json()["data"]["authorization_url"])
    callback = post_signed(
        client,
        "/api/v1/connectors/oauth/google/callback",
        nonce="google-unconfigured-callback",
        payload={
            "state": state,
            "authorization_code": "provider-code",
        },
    )

    assert callback.status_code == 503
    assert callback.json()["error"]["code"] == "google_oauth_not_configured"
    assert "provider-code" not in callback.text


def test_google_oauth_callback_uses_provider_scopes_and_account_identity(
    database_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with database_factory() as session:
        seed_owner(session)
    client = TestClient(create_app(google_configured_settings(), database_factory))

    start = post_signed(
        client,
        "/api/v1/connectors/gmail/oauth/start",
        nonce="google-oauth-start",
        payload={
            "requested_scopes": [GMAIL_SCOPE_MODIFY],
            "redirect_uri": "https://atlas.grafley.com/oauth/google/callback",
        },
    )
    assert start.status_code == 200
    authorization_url = start.json()["data"]["authorization_url"]
    assert "client_id=google-client-id" in authorization_url
    assert "code_challenge_method=S256" in authorization_url
    state = oauth_state_from_url(authorization_url)

    def fake_exchange(**_: object) -> GoogleOAuthExchangeResult:
        return GoogleOAuthExchangeResult(
            account_identifier="owner@example.test",
            granted_scopes=[GMAIL_SCOPE_MODIFY],
            display_name="Owner Gmail",
            credential_key_version="google-test-v1",
        )

    monkeypatch.setattr(
        connector_service,
        "exchange_google_oauth_code",
        fake_exchange,
    )
    callback = post_signed(
        client,
        "/api/v1/connectors/oauth/google/callback",
        nonce="google-oauth-callback",
        payload={
            "state": state,
            "authorization_code": "provider-code",
        },
    )

    assert callback.status_code == 200
    data = callback.json()["data"]
    assert data["connector_type"] == "gmail"
    assert data["status"] == "connected"
    assert data["account_identifier"] == "owner@example.test"
    assert data["granted_scopes"] == [GMAIL_SCOPE_MODIFY]
    assert "provider-code" not in callback.text
    with database_factory() as session:
        credential = session.scalar(select(ConnectorCredentialReference))
        assert credential is not None
        assert credential.key_version == "google-test-v1"
        assert "provider-code" not in json.dumps(credential.reference_label)


def test_google_oauth_callback_rejects_consumed_state_before_provider_exchange(
    database_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with database_factory() as session:
        seed_owner(session)
    client = TestClient(create_app(google_configured_settings(), database_factory))
    start = post_signed(
        client,
        "/api/v1/connectors/gmail/oauth/start",
        nonce="google-consumed-start",
        payload={
            "requested_scopes": [GMAIL_SCOPE_MODIFY],
            "redirect_uri": "https://atlas.grafley.com/oauth/google/callback",
        },
    )
    state = oauth_state_from_url(start.json()["data"]["authorization_url"])
    with database_factory() as session:
        state_record = session.scalar(select(ConnectorOAuthState))
        assert state_record is not None
        state_record.status = "consumed"
        state_record.consumed_at = datetime.now(UTC)
        session.commit()

    called = False

    def fake_exchange(**_: object) -> GoogleOAuthExchangeResult:
        nonlocal called
        called = True
        return GoogleOAuthExchangeResult(
            account_identifier="owner@example.test",
            granted_scopes=[GMAIL_SCOPE_MODIFY],
        )

    monkeypatch.setattr(
        connector_service,
        "exchange_google_oauth_code",
        fake_exchange,
    )
    callback = post_signed(
        client,
        "/api/v1/connectors/oauth/google/callback",
        nonce="google-consumed-callback",
        payload={
            "state": state,
            "authorization_code": "provider-code",
        },
    )

    assert callback.status_code == 422
    assert callback.json()["error"]["code"] == "oauth_state_expired"
    assert called is False


def test_connection_health_revoke_reconnect_and_operation_denial(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
    client = TestClient(create_app(configured_settings(), database_factory))
    start = post_signed(
        client,
        "/api/v1/connectors/gmail/oauth/start",
        nonce="gmail-health-start",
        payload={
            "requested_scopes": [GMAIL_SCOPE_MODIFY],
            "redirect_uri": "https://client.example.test/oauth/callback",
        },
    )
    state = oauth_state_from_url(start.json()["data"]["authorization_url"])
    callback = post_signed(
        client,
        "/api/v1/connectors/gmail/oauth/callback",
        nonce="gmail-health-callback",
        payload={
            "state": state,
            "authorization_code": "fake-health-code",
            "account_identifier": "owner@example.test",
            "granted_scopes": [GMAIL_SCOPE_MODIFY],
        },
    )
    connection_id = callback.json()["data"]["connection_id"]

    health = get_signed(
        client,
        f"/api/v1/connections/{connection_id}/health",
        nonce="gmail-health",
    )
    assert health.status_code == 200
    assert health.json()["data"]["health_status"] == "healthy"

    with database_factory() as session:
        allowed = authorize_connector_operation(
            session,
            owner_user_id=OWNER_ID,
            connection_id=connection_id,
            operation_id="gmail.archive_message",
            actor_id=CLIENT_ID,
        )
        assert allowed.allowed is True
        session.commit()

    revoked = post_signed(
        client,
        f"/api/v1/connections/{connection_id}/revoke",
        nonce="gmail-revoke",
        payload={},
    )
    assert revoked.status_code == 200
    assert revoked.json()["data"]["status"] == "revoked"
    assert "credential_reference" not in revoked.text

    with database_factory() as session:
        denied = authorize_connector_operation(
            session,
            owner_user_id=OWNER_ID,
            connection_id=connection_id,
            operation_id="gmail.archive_message",
            actor_id=CLIENT_ID,
        )
        assert denied.allowed is False
        assert denied.reason_code == "connector_not_connected"
        audit_payloads = [
            event.metadata_json
            for event in session.scalars(
                select(AuditEvent).where(
                    AuditEvent.action == "authorize_operation"
                )
            )
        ]
        assert audit_payloads[-1]["outcome"] == "connector_not_connected"
        session.commit()

    reconnect = post_signed(
        client,
        f"/api/v1/connections/{connection_id}/reconnect",
        nonce="gmail-reconnect",
        payload={
            "requested_scopes": [GMAIL_SCOPE_MODIFY],
            "redirect_uri": "https://client.example.test/oauth/callback",
        },
    )
    assert reconnect.status_code == 200
    assert reconnect.json()["data"]["connector_type"] == "gmail"
