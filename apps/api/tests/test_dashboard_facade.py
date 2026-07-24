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
from atlas_api.models.approval import ApprovalRequest
from atlas_api.models.audit import AuditEvent
from atlas_api.models.connector import ConnectorConnection
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.run import AgentRun, AgentRunStep
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


def dashboard_settings(*, enable_synthetic_smoke_seed: bool = False) -> Settings:
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
        enable_synthetic_smoke_seed=enable_synthetic_smoke_seed,
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
        owner_user_id=OWNER_ID,
    )
    session.commit()
    return user


def authenticated_client(
    database_factory: sessionmaker[Session],
) -> tuple[TestClient, str]:
    settings = dashboard_settings()
    return authenticated_client_with_settings(database_factory, settings)


def authenticated_client_with_settings(
    database_factory: sessionmaker[Session],
    settings: Settings,
) -> tuple[TestClient, str]:
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


def test_dashboard_manual_run_creation_is_not_an_active_facade_route(
    database_factory: sessionmaker[Session],
) -> None:
    client, _ = authenticated_client(database_factory)

    response = client.post(
        "/api/v1/dashboard/runs",
        json={"agent_id": "agent_123"},
        headers={
            "X-Atlas-CSRF-Token": "csrf-token",
            "Idempotency-Key": "dashboard-run-0001",
        },
    )

    assert response.status_code == 405


def test_dashboard_smoke_seed_creates_synthetic_runtime_evidence(
    database_factory: sessionmaker[Session],
) -> None:
    client, _ = authenticated_client_with_settings(
        database_factory,
        dashboard_settings(enable_synthetic_smoke_seed=True),
    )
    session_response = client.get("/api/v1/dashboard/session")
    csrf_token = session_response.json()["data"]["csrf_token"]

    response = client.post(
        "/api/v1/dashboard/smoke-seed",
        json={"scope": "hosted_mvp_smoke"},
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "dashboard-smoke-seed-0001",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["scope"] == "hosted_mvp_smoke"
    assert payload["synthetic"] is True
    assert payload["agent"]["slug"] == "hosted-runtime-smoke-agent"
    assert payload["run"]["status"] == "succeeded"
    assert payload["run"]["trigger_source"] == "manual"
    assert payload["approval"]["status"] == "pending"
    assert {item["connector_type"] for item in payload["connections"]} == {
        "gmail",
        "google_drive",
    }
    assert all(
        item["status"] == "connected" and item["health_status"] == "healthy"
        for item in payload["connections"]
    )
    assert "grafley.invalid" in response.text
    assert "dashboard-secret" not in response.text
    assert "google-secret" not in response.text
    assert "access_token" not in response.text
    assert "refresh_token" not in response.text

    connectors = client.get("/api/v1/dashboard/connectors")
    runs = client.get("/api/v1/dashboard/runs")
    approvals = client.get("/api/v1/dashboard/approvals")
    audit = client.get("/api/v1/dashboard/audit")

    assert connectors.status_code == 200
    assert len(connectors.json()["data"]["connections"]) == 2
    assert runs.status_code == 200
    assert runs.json()["data"][0]["run_id"] == payload["run"]["run_id"]
    assert approvals.status_code == 200
    assert approvals.json()["data"][0]["approval_id"] == payload["approval"][
        "approval_id"
    ]
    assert audit.status_code == 200
    assert "smoke_seed.hosted_runtime_seeded" in {
        item["event_type"] for item in audit.json()["data"]
    }
    with database_factory() as session:
        assert session.scalar(select(ConnectorConnection)) is not None
        assert session.scalar(select(AgentRun)) is not None
        assert session.scalar(select(AgentRunStep)) is not None
        assert session.scalar(select(ApprovalRequest)) is not None


def test_dashboard_smoke_seed_requires_csrf_and_idempotency(
    database_factory: sessionmaker[Session],
) -> None:
    client, _ = authenticated_client_with_settings(
        database_factory,
        dashboard_settings(enable_synthetic_smoke_seed=True),
    )
    session_response = client.get("/api/v1/dashboard/session")
    csrf_token = session_response.json()["data"]["csrf_token"]

    missing_csrf = client.post(
        "/api/v1/dashboard/smoke-seed",
        json={"scope": "hosted_mvp_smoke"},
        headers={"Idempotency-Key": "dashboard-smoke-seed-0002"},
    )
    missing_idempotency = client.post(
        "/api/v1/dashboard/smoke-seed",
        json={"scope": "hosted_mvp_smoke"},
        headers={"X-Atlas-CSRF-Token": csrf_token},
    )

    assert missing_csrf.status_code == 401
    assert missing_csrf.json()["error"]["code"] == "owner_session_csrf_invalid"
    assert missing_idempotency.status_code == 422
    assert missing_idempotency.json()["error"]["code"] == "idempotency_key_invalid"


def test_dashboard_smoke_seed_is_idempotent(
    database_factory: sessionmaker[Session],
) -> None:
    client, _ = authenticated_client_with_settings(
        database_factory,
        dashboard_settings(enable_synthetic_smoke_seed=True),
    )
    session_response = client.get("/api/v1/dashboard/session")
    csrf_token = session_response.json()["data"]["csrf_token"]
    headers = {
        "X-Atlas-CSRF-Token": csrf_token,
        "Idempotency-Key": "dashboard-smoke-seed-0003",
    }

    first = client.post(
        "/api/v1/dashboard/smoke-seed",
        json={"scope": "hosted_mvp_smoke"},
        headers=headers,
    )
    second = client.post(
        "/api/v1/dashboard/smoke-seed",
        json={"scope": "hosted_mvp_smoke"},
        headers=headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["run"]["run_id"] == second.json()["data"]["run"][
        "run_id"
    ]
    assert first.json()["data"]["approval"]["approval_id"] == second.json()["data"][
        "approval"
    ]["approval_id"]
    with database_factory() as session:
        assert len(list(session.scalars(select(ConnectorConnection)))) == 2
        assert len(list(session.scalars(select(AgentRun)))) == 1
        assert len(list(session.scalars(select(ApprovalRequest)))) == 1


def test_dashboard_smoke_seed_is_disabled_by_default(
    database_factory: sessionmaker[Session],
) -> None:
    client, _ = authenticated_client(database_factory)
    session_response = client.get("/api/v1/dashboard/session")
    csrf_token = session_response.json()["data"]["csrf_token"]

    response = client.post(
        "/api/v1/dashboard/smoke-seed",
        json={"scope": "hosted_mvp_smoke"},
        headers={
            "X-Atlas-CSRF-Token": csrf_token,
            "Idempotency-Key": "dashboard-smoke-seed-disabled",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "dashboard_smoke_seed_disabled"


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
