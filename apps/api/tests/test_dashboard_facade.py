from __future__ import annotations

from datetime import UTC, datetime

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
from atlas_api.models.agent import AgentRegistration
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.services.agent_registry import create_agent_registration

OWNER_ID = "usr_dashboard_owner"


@pytest.fixture
def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine)


def dashboard_settings() -> Settings:
    return Settings(
        environment="test",
        external_client_id="dashboard-client",
        external_client_key_id="dashboard-key",
        external_client_secret=SecretStr("dashboard-secret"),
        google_oauth_client_id="google-client",
        google_oauth_client_secret=SecretStr("google-secret"),
        google_oauth_redirect_uri="https://atlas.grafley.com/oauth/google/callback",
        owner_identity_subject="google-owner-subject",
        frontend_origin="https://atlas.grafley.com",
    )


def seed_owner(session: Session) -> User:
    user = User(
        user_id=OWNER_ID,
        email="grafleyinc@gmail.com",
        display_name="Grafley Owner",
        identity_provider="google",
        identity_subject="google-owner-subject",
        status="active",
    )
    session.add(user)
    session.add(
        ExternalProductClient(
            external_client_id="dashboard-client",
            display_name="Atlas Dashboard",
            status="active",
            authentication_key_reference="provider-native",
            human_owner_user_id=OWNER_ID,
        )
    )
    create_agent_registration(
        session,
        slug="gmail-agent",
        display_name="Gmail Agent",
        description="Synthetic Gmail agent for dashboard facade tests.",
        version="0.1.0",
        risk_level="medium",
        capabilities=["gmail.triage"],
        allowed_tools=["gmail.modify"],
        required_connectors=["gmail"],
        supports_manual_run=True,
    )
    session.commit()
    return user


def authenticated_client(
    database_factory: sessionmaker[Session],
) -> tuple[TestClient, str]:
    settings = dashboard_settings()
    client = TestClient(
        create_app(settings, database_factory),
        base_url="https://api.atlas.grafley.com",
    )
    with database_factory() as session:
        user = seed_owner(session)
        issued = issue_owner_session(
            session,
            user_id=user.user_id,
            settings=settings,
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


def test_dashboard_facade_requires_owner_session(
    database_factory: sessionmaker[Session],
) -> None:
    client = TestClient(
        create_app(dashboard_settings(), database_factory),
        base_url="https://api.atlas.grafley.com",
    )

    response = client.get("/api/v1/dashboard/connectors")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "owner_session_missing"


def test_dashboard_session_returns_csrf_without_secret_values(
    database_factory: sessionmaker[Session],
) -> None:
    client, _ = authenticated_client(database_factory)

    response = client.get("/api/v1/dashboard/session")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["authenticated"] is True
    assert payload["data"]["user"]["email"] == "grafleyinc@gmail.com"
    assert payload["data"]["csrf_token"]
    assert "dashboard-secret" not in response.text
    assert "google-secret" not in response.text


def test_dashboard_connector_and_run_facade_use_owner_scope(
    database_factory: sessionmaker[Session],
) -> None:
    client, _ = authenticated_client(database_factory)

    connectors = client.get("/api/v1/dashboard/connectors")
    agents = client.get("/api/v1/dashboard/agents")
    runs = client.get("/api/v1/dashboard/runs")

    assert connectors.status_code == 200
    assert "gmail" in {
        item["connector_type"] for item in connectors.json()["data"]["descriptors"]
    }
    assert agents.status_code == 200
    assert agents.json()["data"][0]["slug"] == "gmail-agent"
    assert runs.status_code == 200
    assert runs.json()["data"] == []


def test_dashboard_state_change_requires_rotated_csrf(
    database_factory: sessionmaker[Session],
) -> None:
    client, stale_csrf = authenticated_client(database_factory)
    with database_factory() as session:
        agent_id = session.scalar(
            select(AgentRegistration.agent_id).where(
                AgentRegistration.slug == "gmail-agent"
            )
        )
    assert agent_id is not None
    session_response = client.get("/api/v1/dashboard/session")
    csrf_token = session_response.json()["data"]["csrf_token"]

    denied = client.post(
        "/api/v1/dashboard/runs",
        json={"agent_id": "missing-agent"},
        headers={
            "X-Atlas-CSRF-Token": stale_csrf,
            "Idempotency-Key": "dashboard-run-0001",
        },
    )
    created = client.post(
        "/api/v1/dashboard/runs",
        json={"agent_id": agent_id},
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "dashboard-run-0002",
        },
    )

    assert denied.status_code == 401
    assert denied.json()["error"]["code"] == "owner_session_csrf_invalid"
    assert created.status_code == 200
    assert created.json()["data"]["agent_id"] == agent_id
    detail = client.get(f"/api/v1/dashboard/runs/{created.json()['data']['run_id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["run_id"] == created.json()["data"]["run_id"]


def test_dashboard_audit_and_monitoring_are_metadata_only(
    database_factory: sessionmaker[Session],
) -> None:
    client, _ = authenticated_client(database_factory)

    audit = client.get("/api/v1/dashboard/audit")
    monitoring = client.get("/api/v1/dashboard/monitoring")

    assert audit.status_code == 200
    assert monitoring.status_code == 200
    assert monitoring.json()["data"]["runtime_origin"] == "atlas-api"
    assert all(
        item["redaction_state"] == "metadata_only" for item in audit.json()["data"]
    )
    with database_factory() as session:
        assert session.scalar(select(AuditEvent)) is not None
