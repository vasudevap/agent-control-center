from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.owner_sessions import SESSION_COOKIE_NAME, issue_owner_session
from atlas_api.db.base import Base
from atlas_api.main import create_app
from atlas_api.models.agent import (
    AgentActivityEvent,
    AgentAlert,
    AgentExecution,
    AgentRegistration,
)
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import User

OWNER_ID = "usr_visibility_owner"
OTHER_OWNER_ID = "usr_visibility_other"


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
    existing = session.get(User, user_id)
    if existing is not None:
        return existing
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


def seed_agent(session: Session, *, owner_user_id: str, slug: str) -> AgentRegistration:
    agent = AgentRegistration(
        slug=slug,
        display_name=f"{slug} display",
        description="Owner visibility test agent.",
        version="1.0.0",
        risk_level="low",
        capabilities=["telemetry.report"],
        allowed_tools=["atlas.telemetry.write"],
        required_connectors=[],
        configuration_schema={},
        owner_user_id=owner_user_id,
        lifecycle_status="connected",
        monitoring_mode="heartbeat",
        heartbeat_interval_seconds=60,
        observed_health="online",
        reported_health="healthy",
    )
    session.add(agent)
    session.flush()
    return agent


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
        seed_owner(session, user_id=user_id, subject=subject)
        issued = issue_owner_session(
            session,
            user_id=user_id,
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


def seed_visibility_records(database_factory: sessionmaker[Session]) -> tuple[str, str]:
    with database_factory() as session:
        seed_owner(session, user_id=OWNER_ID, subject="owner-one")
        seed_owner(session, user_id=OTHER_OWNER_ID, subject="owner-two")
        owner_agent = seed_agent(session, owner_user_id=OWNER_ID, slug="owner-agent")
        other_agent = seed_agent(
            session,
            owner_user_id=OTHER_OWNER_ID,
            slug="other-agent",
        )
        execution = AgentExecution(
            agent_id=owner_agent.agent_id,
            external_execution_id="external-owner-run",
            representation_hash="hash-owner-run",
            status="succeeded",
            trigger="schedule",
            summary="Owner execution completed.",
            first_reported_at=datetime.now(UTC),
            last_reported_at=datetime.now(UTC),
            terminal_at=datetime.now(UTC),
        )
        hidden_execution = AgentExecution(
            agent_id=other_agent.agent_id,
            external_execution_id="external-other-run",
            representation_hash="hash-other-run",
            status="failed",
            trigger="manual",
            first_reported_at=datetime.now(UTC),
            last_reported_at=datetime.now(UTC),
            terminal_at=datetime.now(UTC),
        )
        alert = AgentAlert(
            agent_id=owner_agent.agent_id,
            condition_key=f"agent:{owner_agent.agent_id}:missed-heartbeat",
            status="open",
            severity="warning",
            evidence_json={"observed_health": "late"},
        )
        hidden_alert = AgentAlert(
            agent_id=other_agent.agent_id,
            condition_key=f"agent:{other_agent.agent_id}:missed-heartbeat",
            status="open",
            severity="critical",
            evidence_json={"observed_health": "offline"},
        )
        activity = AgentActivityEvent(
            agent_id=owner_agent.agent_id,
            source_type="agent_alert",
            source_id="owner-alert",
            event_type="agent.alert.opened",
            severity="warning",
            summary="Owner alert opened.",
            actor_type="system",
            metadata_json={},
        )
        hidden_activity = AgentActivityEvent(
            agent_id=other_agent.agent_id,
            source_type="agent_alert",
            source_id="other-alert",
            event_type="agent.alert.opened",
            severity="critical",
            summary="Other alert opened.",
            actor_type="system",
            metadata_json={},
        )
        session.add_all(
            [
                execution,
                hidden_execution,
                alert,
                hidden_alert,
                activity,
                hidden_activity,
            ]
        )
        session.flush()
        execution_id = execution.agent_execution_id
        alert_id = alert.alert_id
        session.commit()
    return execution_id, alert_id


def test_owner_visibility_reads_are_owner_scoped(
    database_factory: sessionmaker[Session],
) -> None:
    execution_id, alert_id = seed_visibility_records(database_factory)
    client, _ = authenticated_client(database_factory)

    executions = client.get("/api/v1/executions")
    execution_detail = client.get(f"/api/v1/executions/{execution_id}")
    alerts = client.get("/api/v1/alerts")
    alert_detail = client.get(f"/api/v1/alerts/{alert_id}")
    activity = client.get("/api/v1/activity")

    assert executions.status_code == 200
    assert [item["external_execution_id"] for item in executions.json()["data"]] == [
        "external-owner-run",
    ]
    assert execution_detail.status_code == 200
    assert execution_detail.json()["data"]["agent_execution_id"] == execution_id
    assert alerts.status_code == 200
    assert [item["alert_id"] for item in alerts.json()["data"]] == [alert_id]
    assert alert_detail.status_code == 200
    assert activity.status_code == 200
    assert [item["summary"] for item in activity.json()["data"]] == [
        "Owner alert opened.",
    ]


def test_alert_acknowledgement_requires_csrf_and_does_not_resolve(
    database_factory: sessionmaker[Session],
) -> None:
    _, alert_id = seed_visibility_records(database_factory)
    client, csrf_token = authenticated_client(database_factory)

    missing_csrf = client.post(f"/api/v1/alerts/{alert_id}/acknowledge")
    acknowledged = client.post(
        f"/api/v1/alerts/{alert_id}/acknowledge",
        headers={"X-Atlas-CSRF-Token": csrf_token},
    )

    assert missing_csrf.status_code == 401
    assert acknowledged.status_code == 200
    assert acknowledged.json()["data"]["status"] == "acknowledged"
    assert acknowledged.json()["data"]["resolved_at"] is None
    with database_factory() as session:
        alert = session.get(AgentAlert, alert_id)
        assert alert is not None
        assert alert.status == "acknowledged"
        audit = session.query(AuditEvent).filter_by(
            event_type="agent_visibility.acknowledge_alert",
        ).one_or_none()
        assert audit is not None
