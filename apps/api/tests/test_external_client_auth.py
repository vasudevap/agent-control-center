from __future__ import annotations

from datetime import UTC, datetime

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
from atlas_api.models.external_request_nonce import ExternalRequestNonce

CLIENT_ID = "external-client-1"
KEY_ID = "current-key"
SECRET = "expected-signing-secret"


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


def signed_headers(*, nonce: str = "nonce-1", secret: str = SECRET) -> dict[str, str]:
    timestamp = int(datetime.now(UTC).timestamp())
    signed_request = SignedExternalRequest(
        client_id=CLIENT_ID,
        key_id=KEY_ID,
        timestamp=timestamp,
        nonce=nonce,
        signature="",
        method="GET",
        path_query="/api/v1/external-client/authentication/probe",
        body=b"",
    )
    return {
        "X-Atlas-Client-Id": CLIENT_ID,
        "X-Atlas-Key-Id": KEY_ID,
        "X-Atlas-Timestamp": str(timestamp),
        "X-Atlas-Nonce": nonce,
        "X-Atlas-Signature": sign_request(signed_request, secret),
    }


def test_external_client_auth_fails_closed_when_unconfigured() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/api/v1/external-client/authentication/probe")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == (
        "external_client_authentication_not_configured"
    )


def test_external_client_auth_rejects_missing_signature_headers(
    database_factory: sessionmaker[Session],
) -> None:
    client = TestClient(create_app(configured_settings(), database_factory))

    response = client.get("/api/v1/external-client/authentication/probe")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == (
        "external_client_signature_headers_required"
    )


def test_external_client_auth_requires_a_persistent_nonce_store() -> None:
    client = TestClient(create_app(configured_settings()))

    response = client.get(
        "/api/v1/external-client/authentication/probe",
        headers=signed_headers(),
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == (
        "external_client_nonce_store_not_configured"
    )


def test_external_client_auth_accepts_signed_request_and_records_provenance(
    database_factory: sessionmaker[Session],
) -> None:
    client = TestClient(create_app(configured_settings(), database_factory))

    response = client.get(
        "/api/v1/external-client/authentication/probe",
        headers=signed_headers(),
    )

    assert response.status_code == 200
    assert response.json()["data"]["external_client_id"] == CLIENT_ID
    assert "human" not in response.text.lower()
    with database_factory() as session:
        assert session.scalar(select(ExternalRequestNonce)) is not None
        audit_event = session.scalar(select(AuditEvent))
        assert audit_event is not None
        assert audit_event.metadata_json["outcome"] == "authorized"


def test_external_client_auth_rejects_signature_and_replayed_nonce(
    database_factory: sessionmaker[Session],
) -> None:
    client = TestClient(create_app(configured_settings(), database_factory))

    invalid = client.get(
        "/api/v1/external-client/authentication/probe",
        headers=signed_headers(secret="wrong-secret"),
    )
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "external_client_signature_invalid"

    headers = signed_headers(nonce="replayed-nonce")
    accepted = client.get(
        "/api/v1/external-client/authentication/probe", headers=headers
    )
    replayed = client.get(
        "/api/v1/external-client/authentication/probe", headers=headers
    )
    assert accepted.status_code == 200
    assert replayed.status_code == 401
    assert replayed.json()["error"]["code"] == "external_client_nonce_replayed"
