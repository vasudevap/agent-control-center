from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.owner_sessions import SESSION_COOKIE_NAME, issue_owner_session
from atlas_api.db.base import Base
from atlas_api.main import create_app
from atlas_api.models.agent import (
    AgentActivityEvent,
    AgentCredential,
    AgentRegistration,
)
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import User
from atlas_api.services.agent_credentials import parse_agent_token, verify_agent_token

OWNER_ID = "usr_owner_one"
OTHER_OWNER_ID = "usr_owner_two"


@pytest.fixture
def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine)


def settings() -> Settings:
    return Settings(
        environment="test",
        owner_identity_subject="owner-one",
        agent_credential_pepper=SecretStr("agent-credential-pepper"),
        agent_credential_pepper_key_id="pepper-key-1",
    )


def seed_owner(session: Session, *, user_id: str, subject: str) -> User:
    user = User(
        user_id=user_id,
        email=f"{user_id}@example.test",
        display_name=user_id,
        identity_provider="google",
        identity_subject=subject,
        status="active",
    )
    session.add(user)
    return user


def authenticated_client(
    database_factory: sessionmaker[Session],
    *,
    user_id: str = OWNER_ID,
    subject: str = "owner-one",
) -> tuple[TestClient, str]:
    app_settings = settings()
    client = TestClient(
        create_app(app_settings, database_factory),
        base_url="https://api.atlas.grafley.com",
    )
    with database_factory() as session:
        user = seed_owner(session, user_id=user_id, subject=subject)
        issued = issue_owner_session(
            session,
            user_id=user.user_id,
            settings=app_settings,
            now=datetime.now(UTC),
        )
        session.commit()
    client.cookies.set(
        SESSION_COOKIE_NAME,
        issued.session_token,
        domain="api.atlas.grafley.com",
        path="/",
    )
    return client, issued.csrf_token


def enrollment_payload(slug: str = "invoice-agent") -> dict[str, object]:
    return {
        "slug": slug,
        "display_name": "Invoice Agent",
        "description": "Reports externally executed invoice work.",
        "environment": "production",
        "monitoring_mode": "heartbeat",
        "heartbeat_interval_seconds": 60,
        "tags": ["finance", "mvp"],
        "repository_url": "https://github.com/example/invoice-agent",
        "deployment_url": "https://agents.example.test/invoice",
        "expected_version": "1.2.3",
    }


def heartbeat_payload(event_id: str = "heartbeat-1") -> dict[str, object]:
    return {
        "event_id": event_id,
        "contract_version": "2026-07-24",
        "sent_at": "2026-07-24T14:00:00Z",
        "environment": "production",
        "status": "healthy",
        "checks": [{"name": "runtime", "status": "healthy"}],
        "agent_version": "1.2.3",
        "build_sha": "abc123",
    }


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_owner_enrollment_issues_one_plaintext_credential_without_persisting_it(
    database_factory: sessionmaker[Session],
) -> None:
    client, csrf_token = authenticated_client(database_factory)

    response = client.post(
        "/api/v1/dashboard/agents",
        json=enrollment_payload(),
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-enroll-key-0001",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    agent = data["agent"]
    credential = data["credential"]
    plaintext_token = credential["plaintext_token"]
    parsed = parse_agent_token(plaintext_token)
    assert parsed is not None
    assert plaintext_token.startswith("atl_agent_cred_")
    assert agent["owner_user_id"] == OWNER_ID
    assert agent["registration_source"] == "owner_enrolled"
    assert agent["active_surface_visible"] is True
    assert agent["lifecycle_status"] == "pending"
    assert agent["observed_health"] == "never_seen"

    with database_factory() as session:
        stored_agent = session.scalar(select(AgentRegistration))
        stored_credential = session.scalar(select(AgentCredential))
        assert stored_agent is not None
        assert stored_credential is not None
        assert stored_agent.owner_user_id == OWNER_ID
        assert stored_credential.agent_id == stored_agent.agent_id
        assert stored_credential.scope == "telemetry_write"
        assert stored_credential.verifier_key_id == "pepper-key-1"
        assert plaintext_token not in stored_credential.verifier_hmac_sha256
        assert parsed[1] not in stored_credential.verifier_hmac_sha256
        assert verify_agent_token(
            session,
            token=plaintext_token,
            settings=settings(),
        ) == stored_credential

        audit = session.scalar(
            select(AuditEvent).where(AuditEvent.event_type == "dashboard.enroll_agent")
        )
        assert audit is not None
        assert plaintext_token not in str(audit.metadata)
        assert parsed[1] not in str(audit.metadata)

    read_response = client.get(f"/api/v1/dashboard/agents/{agent['agent_id']}")
    assert read_response.status_code == 200
    assert "plaintext_token" not in read_response.text
    assert "verifier_hmac_sha256" not in read_response.text


def test_activity_only_enrollment_persists_null_heartbeat_interval(
    database_factory: sessionmaker[Session],
) -> None:
    client, csrf_token = authenticated_client(database_factory)
    payload = enrollment_payload("activity-only-agent")
    payload["monitoring_mode"] = "activity_only"
    payload["heartbeat_interval_seconds"] = None

    response = client.post(
        "/api/v1/dashboard/agents",
        json=payload,
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-enroll-key-activity-only",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["agent"]["monitoring_mode"] == "activity_only"
    assert response.json()["data"]["agent"]["heartbeat_interval_seconds"] is None
    with database_factory() as session:
        stored_agent = session.scalar(
            select(AgentRegistration).where(
                AgentRegistration.slug == "activity-only-agent",
            )
        )
        assert stored_agent is not None
        assert stored_agent.heartbeat_interval_seconds is None


def test_credential_rotation_accepts_old_and_new_until_exact_overlap_expiry(
    database_factory: sessionmaker[Session],
) -> None:
    client, csrf_token = authenticated_client(database_factory)
    enrolled = client.post(
        "/api/v1/dashboard/agents",
        json=enrollment_payload("rotation-agent"),
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-rotate-enroll-key",
        },
    )
    old_token = enrolled.json()["data"]["credential"]["plaintext_token"]
    agent_id = enrolled.json()["data"]["agent"]["agent_id"]

    rotated = client.post(
        f"/api/v1/dashboard/agents/{agent_id}/credentials/rotate",
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-rotate-key-0001",
        },
    )

    assert rotated.status_code == 200
    data = rotated.json()["data"]
    new_token = data["credential"]["plaintext_token"]
    assert new_token != old_token
    assert "verifier_hmac_sha256" not in rotated.text

    with database_factory() as session:
        credentials = list(
            session.scalars(
                select(AgentCredential).order_by(AgentCredential.issued_at)
            )
        )
        old, new = credentials
        assert old.status == "overlap"
        assert new.status == "active"
        assert old.overlap_expires_at is not None
        assert old.overlap_expires_at - new.issued_at == timedelta(hours=24)
        assert verify_agent_token(session, token=old_token, settings=settings()) == old
        assert verify_agent_token(session, token=new_token, settings=settings()) == new

        old.overlap_expires_at = datetime.now(UTC) - timedelta(seconds=1)
        session.flush()
        assert verify_agent_token(session, token=old_token, settings=settings()) is None
        assert old.status == "expired"


def test_disconnect_reconnect_and_archive_revoke_credentials_and_preserve_history(
    database_factory: sessionmaker[Session],
) -> None:
    client, csrf_token = authenticated_client(database_factory)
    enrolled = client.post(
        "/api/v1/dashboard/agents",
        json=enrollment_payload("lifecycle-agent"),
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-lifecycle-enroll-key",
        },
    )
    agent_id = enrolled.json()["data"]["agent"]["agent_id"]
    first_token = enrolled.json()["data"]["credential"]["plaintext_token"]

    connected = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=heartbeat_payload("connect-before-disconnect"),
        headers=bearer(first_token),
    )
    assert connected.status_code == 202

    disconnected = client.post(
        f"/api/v1/dashboard/agents/{agent_id}/disconnect",
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-disconnect-key-0001",
        },
    )
    assert disconnected.status_code == 200
    assert disconnected.json()["data"]["agent"]["lifecycle_status"] == "disconnected"
    assert "plaintext_token" not in disconnected.text

    rejected = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=heartbeat_payload("rejected-after-disconnect"),
        headers=bearer(first_token),
    )
    assert rejected.status_code == 401

    reconnected = client.post(
        f"/api/v1/dashboard/agents/{agent_id}/reconnect",
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-reconnect-key-0001",
        },
    )
    assert reconnected.status_code == 200
    assert reconnected.json()["data"]["agent"]["lifecycle_status"] == "pending"
    reconnect_token = reconnected.json()["data"]["credential"]["plaintext_token"]
    assert reconnect_token != first_token

    accepted = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=heartbeat_payload("connect-after-reconnect"),
        headers=bearer(reconnect_token),
    )
    assert accepted.status_code == 202

    archived = client.post(
        f"/api/v1/dashboard/agents/{agent_id}/archive",
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-archive-key-0001",
        },
    )
    assert archived.status_code == 200
    archived_agent = archived.json()["data"]["agent"]
    assert archived_agent["lifecycle_status"] == "archived"
    assert archived_agent["active_surface_visible"] is False
    assert "plaintext_token" not in archived.text

    hidden = client.get(f"/api/v1/dashboard/agents/{agent_id}")
    assert hidden.status_code == 404

    archived_rejected = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=heartbeat_payload("rejected-after-archive"),
        headers=bearer(reconnect_token),
    )
    assert archived_rejected.status_code == 401

    with database_factory() as session:
        agent = session.get(AgentRegistration, agent_id)
        assert agent is not None
        assert agent.lifecycle_status == "archived"
        assert agent.active_surface_visible is False
        assert session.query(AgentCredential).filter_by(status="active").count() == 0
        assert session.query(AgentCredential).filter_by(status="revoked").count() >= 2
        assert (
            session.query(AgentActivityEvent).filter_by(agent_id=agent_id).count() >= 4
        )
        assert agent.observed_health == "archived"


def test_enrollment_requires_csrf_and_idempotency(
    database_factory: sessionmaker[Session],
) -> None:
    client, csrf_token = authenticated_client(database_factory)

    missing_csrf = client.post(
        "/api/v1/dashboard/agents",
        json=enrollment_payload("missing-csrf-agent"),
        headers={"Idempotency-Key": "agent-enroll-key-0002"},
    )
    missing_idempotency = client.post(
        "/api/v1/dashboard/agents",
        json=enrollment_payload("missing-idempotency-agent"),
        headers={"X-Atlas-CSRF-Token": csrf_token},
    )

    assert missing_csrf.status_code == 401
    assert missing_csrf.json()["error"]["code"] == "owner_session_csrf_invalid"
    assert missing_idempotency.status_code == 422
    assert missing_idempotency.json()["error"]["code"] == "idempotency_key_invalid"


def test_enrollment_idempotency_does_not_replay_plaintext_credentials(
    database_factory: sessionmaker[Session],
) -> None:
    client, csrf_token = authenticated_client(database_factory)
    headers = {
        "X-Atlas-CSRF-Token": csrf_token,
        "Idempotency-Key": "agent-enroll-key-0003",
    }

    first = client.post(
        "/api/v1/dashboard/agents",
        json=enrollment_payload("replay-agent"),
        headers=headers,
    )
    replay = client.post(
        "/api/v1/dashboard/agents",
        json=enrollment_payload("replay-agent"),
        headers=headers,
    )

    assert first.status_code == 200
    assert replay.status_code == 409
    assert "plaintext_token" not in replay.text
    assert replay.json()["error"]["code"] == (
        "agent_enrollment_idempotency_replay_unavailable"
    )


def test_owner_scoping_prevents_cross_owner_agent_reads(
    database_factory: sessionmaker[Session],
) -> None:
    first_client, csrf_token = authenticated_client(database_factory)
    create_response = first_client.post(
        "/api/v1/dashboard/agents",
        json=enrollment_payload("private-agent"),
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-enroll-key-0004",
        },
    )
    assert create_response.status_code == 200
    agent_id = create_response.json()["data"]["agent"]["agent_id"]

    second_client, _ = authenticated_client(
        database_factory,
        user_id=OTHER_OWNER_ID,
        subject="owner-two",
    )
    response = second_client.get(f"/api/v1/dashboard/agents/{agent_id}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "agent_not_found"


def test_owner_metadata_update_requires_csrf_and_does_not_return_credentials(
    database_factory: sessionmaker[Session],
) -> None:
    client, csrf_token = authenticated_client(database_factory)
    create_response = client.post(
        "/api/v1/dashboard/agents",
        json=enrollment_payload("metadata-agent"),
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-enroll-key-0005",
        },
    )
    agent_id = create_response.json()["data"]["agent"]["agent_id"]

    update = client.patch(
        f"/api/v1/dashboard/agents/{agent_id}",
        json={"display_name": "Updated Agent", "tags": ["updated"]},
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "agent-update-key-0005",
        },
    )

    assert update.status_code == 200
    assert update.json()["data"]["display_name"] == "Updated Agent"
    assert update.json()["data"]["tags"] == ["updated"]
    assert "plaintext_token" not in update.text
    assert "verifier_hmac_sha256" not in update.text


def test_production_like_readiness_requires_agent_credential_settings() -> None:
    problems = Settings(
        environment="production",
        database_url=SecretStr("configured-database-url"),
        external_client_id="client",
        external_client_key_id="key",
        external_client_secret=SecretStr("external-secret"),
        google_oauth_client_id="google",
        google_oauth_client_secret=SecretStr("google-secret"),
        google_oauth_redirect_uri="https://atlas.example.test/oauth",
        owner_oidc_bootstrap_email="owner@example.test",
        owner_oidc_client_id="owner-client",
        owner_oidc_client_secret=SecretStr("owner-secret"),
        owner_oidc_redirect_uri="https://atlas.example.test/owner",
        owner_oidc_transaction_secret=SecretStr("transaction-secret"),
        owner_identity_subject="owner-subject",
        webhook_signing_key_id="webhook-key",
        webhook_signing_secret=SecretStr("webhook-secret"),
    ).readiness_problems()

    assert "agent_credential_pepper_missing" in problems
    assert "agent_credential_pepper_key_id_missing" in problems

    ready_problems = Settings(
        environment="production",
        database_url=SecretStr("configured-database-url"),
        external_client_id="client",
        external_client_key_id="key",
        external_client_secret=SecretStr("external-secret"),
        google_oauth_client_id="google",
        google_oauth_client_secret=SecretStr("google-secret"),
        google_oauth_redirect_uri="https://atlas.example.test/oauth",
        owner_oidc_bootstrap_email="owner@example.test",
        owner_oidc_client_id="owner-client",
        owner_oidc_client_secret=SecretStr("owner-secret"),
        owner_oidc_redirect_uri="https://atlas.example.test/owner",
        owner_oidc_transaction_secret=SecretStr("transaction-secret"),
        owner_identity_subject="owner-subject",
        webhook_signing_key_id="webhook-key",
        webhook_signing_secret=SecretStr("webhook-secret"),
        agent_credential_pepper=SecretStr("agent-pepper"),
        agent_credential_pepper_key_id="agent-pepper-key",
    ).readiness_problems()

    assert "agent_credential_pepper_missing" not in ready_problems
    assert "agent_credential_pepper_key_id_missing" not in ready_problems
