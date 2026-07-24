from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.db.base import Base
from atlas_api.main import create_app
from atlas_api.models.agent import (
    AgentActivityEvent,
    AgentAlert,
    AgentCredential,
    AgentExecution,
    AgentHealthEvaluatorLease,
    AgentHeartbeat,
    AgentRegistration,
)
from atlas_api.models.external_client import User
from atlas_api.services.agent_alerts import (
    acknowledge_alert,
    record_security_ingestion_alert,
)
from atlas_api.services.agent_health_evaluator import (
    EVALUATOR_LEASE_NAME,
    evaluate_agent_health_once,
)

OWNER_ID = "usr_health_owner"
CREDENTIAL_ID = "agc_health_credential"
NOW = datetime(2026, 7, 24, 14, 0, tzinfo=UTC)


@pytest.fixture
def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine)


def settings(*, evaluator_enabled: bool = False) -> Settings:
    return Settings(
        environment="test",
        owner_identity_subject="owner-one",
        agent_credential_pepper=SecretStr("agent-credential-pepper"),
        agent_credential_pepper_key_id="pepper-key-1",
        agent_health_evaluator_enabled=evaluator_enabled,
    )


def seed_owner(session: Session) -> None:
    session.add(
        User(
            user_id=OWNER_ID,
            email="health-owner@example.test",
            display_name="Health Owner",
            identity_provider="google",
            identity_subject="owner-one",
            status="active",
        )
    )


def seed_agent(
    session: Session,
    *,
    slug: str = "health-agent",
    lifecycle_status: str = "connected",
    monitoring_mode: str = "heartbeat",
    heartbeat_interval_seconds: int | None = 60,
    last_heartbeat_received_at: datetime | None = None,
    observed_health: str = "never_seen",
    expected_version: str | None = None,
    last_agent_version: str | None = None,
    environment: str = "production",
) -> AgentRegistration:
    agent = AgentRegistration(
        slug=slug,
        display_name=f"{slug} display",
        description="Reports external health to Atlas.",
        version="1.0.0",
        risk_level="low",
        capabilities=["telemetry.report"],
        allowed_tools=["atlas.telemetry.write"],
        required_connectors=[],
        configuration_schema={},
        owner_user_id=OWNER_ID,
        lifecycle_status=lifecycle_status,
        monitoring_mode=monitoring_mode,
        heartbeat_interval_seconds=heartbeat_interval_seconds,
        last_heartbeat_received_at=last_heartbeat_received_at,
        observed_health=observed_health,
        health_status=observed_health,
        expected_version=expected_version,
        last_agent_version=last_agent_version,
        environment=environment,
    )
    session.add(agent)
    session.flush()
    session.add(
        AgentCredential(
            credential_id=f"{CREDENTIAL_ID}_{slug}",
            agent_id=agent.agent_id,
            credential_lookup_id=f"lookup-{slug}",
            verifier_hmac_sha256="0" * 64,
            verifier_key_id="pepper-key-1",
        )
    )
    session.flush()
    return agent


def seed_heartbeat(
    session: Session,
    agent: AgentRegistration,
    *,
    event_id: str,
    received_at: datetime,
    environment: str = "production",
    reported_status: str = "healthy",
    checks: list[dict[str, object]] | None = None,
) -> AgentHeartbeat:
    heartbeat = AgentHeartbeat(
        agent_id=agent.agent_id,
        credential_id=f"{CREDENTIAL_ID}_{agent.slug}",
        event_id=event_id,
        event_fingerprint=f"fingerprint-{event_id}",
        contract_version="2026-07-24",
        sent_at=received_at,
        received_at=received_at,
        agent_version=agent.last_agent_version,
        build_sha=None,
        environment=environment,
        reported_status=reported_status,
        checks_json=checks or [],
    )
    session.add(heartbeat)
    agent.last_heartbeat_received_at = received_at
    session.flush()
    return heartbeat


def seed_failed_execution(
    session: Session,
    agent: AgentRegistration,
    *,
    external_id: str,
    terminal_at: datetime,
) -> None:
    session.add(
        AgentExecution(
            agent_id=agent.agent_id,
            external_execution_id=external_id,
            representation_hash=f"hash-{external_id}",
            status="failed",
            trigger="schedule",
            first_reported_at=terminal_at,
            last_reported_at=terminal_at,
            terminal_at=terminal_at,
        )
    )


def active_alerts(session: Session, agent: AgentRegistration) -> list[AgentAlert]:
    return list(
        session.scalars(
            select(AgentAlert)
            .where(
                AgentAlert.agent_id == agent.agent_id,
                AgentAlert.status.in_(("open", "acknowledged")),
            )
            .order_by(AgentAlert.condition_key)
        )
    )


def test_evaluator_derives_observed_health_and_records_transitions(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
        online = seed_agent(
            session,
            slug="online-agent",
            last_heartbeat_received_at=NOW - timedelta(seconds=120),
        )
        late = seed_agent(
            session,
            slug="late-agent",
            last_heartbeat_received_at=NOW - timedelta(seconds=121),
        )
        offline = seed_agent(
            session,
            slug="offline-agent",
            last_heartbeat_received_at=NOW - timedelta(seconds=301),
        )
        never_seen = seed_agent(session, slug="never-seen-agent")
        activity_only = seed_agent(
            session,
            slug="activity-agent",
            monitoring_mode="activity_only",
            heartbeat_interval_seconds=None,
        )
        disconnected = seed_agent(
            session,
            slug="disconnected-agent",
            lifecycle_status="disconnected",
        )
        archived = seed_agent(
            session,
            slug="archived-agent",
            lifecycle_status="archived",
        )

        result = evaluate_agent_health_once(session, holder_id="worker-one", now=NOW)
        session.commit()

        assert result.acquired is True
        assert result.processed_count == 7
        assert online.observed_health == "online"
        assert late.observed_health == "late"
        assert offline.observed_health == "offline"
        assert never_seen.observed_health == "never_seen"
        assert activity_only.observed_health == "not_monitored"
        assert disconnected.observed_health == "disconnected"
        assert archived.observed_health == "archived"
        event_types = {
            event.event_type
            for event in session.scalars(select(AgentActivityEvent))
        }
        assert event_types >= {
            "agent.observed_health.transition",
            "agent.alert.opened",
        }


def test_evaluator_dedupes_missed_heartbeat_alerts_across_repeat_runs(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
        agent = seed_agent(
            session,
            last_heartbeat_received_at=NOW - timedelta(minutes=6),
        )

        first = evaluate_agent_health_once(session, holder_id="worker-one", now=NOW)
        second = evaluate_agent_health_once(
            session,
            holder_id="worker-one",
            now=NOW + timedelta(seconds=1),
        )
        session.commit()

        alerts = active_alerts(session, agent)
        assert first.opened_alerts == 1
        assert second.opened_alerts == 0
        assert len(alerts) == 1
        assert alerts[0].condition_key == f"agent:{agent.agent_id}:missed-heartbeat"
        assert alerts[0].status == "open"


def test_evaluator_respects_database_lease_contention(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
        agent = seed_agent(
            session,
            last_heartbeat_received_at=NOW - timedelta(minutes=6),
        )
        session.add(
            AgentHealthEvaluatorLease(
                lease_name=EVALUATOR_LEASE_NAME,
                holder_id="other-worker",
                lease_expires_at=NOW + timedelta(seconds=60),
                last_processed_count=0,
            )
        )
        session.commit()

        blocked = evaluate_agent_health_once(session, holder_id="worker-one", now=NOW)
        acquired = evaluate_agent_health_once(
            session,
            holder_id="worker-one",
            now=NOW + timedelta(seconds=91),
        )
        session.commit()

        assert blocked.acquired is False
        assert acquired.acquired is True
        assert agent.observed_health == "offline"


def test_missed_heartbeat_alert_resolves_when_agent_returns_online(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
        agent = seed_agent(
            session,
            last_heartbeat_received_at=NOW - timedelta(minutes=6),
        )
        evaluate_agent_health_once(session, holder_id="worker-one", now=NOW)
        seed_heartbeat(
            session,
            agent,
            event_id="heartbeat-returned",
            received_at=NOW + timedelta(seconds=10),
        )

        result = evaluate_agent_health_once(
            session,
            holder_id="worker-one",
            now=NOW + timedelta(seconds=10),
        )
        session.commit()

        alerts = list(session.scalars(select(AgentAlert)))
        assert result.resolved_alerts == 1
        assert agent.observed_health == "online"
        assert alerts[0].status == "resolved"
        assert alerts[0].resolved_reason == "observed_health_online"


def test_failed_check_alert_opens_and_resolves_on_recovery(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
        agent = seed_agent(session, last_heartbeat_received_at=NOW)
        seed_heartbeat(
            session,
            agent,
            event_id="heartbeat-unhealthy",
            received_at=NOW,
            checks=[{"name": "database", "status": "unhealthy"}],
        )

        opened = evaluate_agent_health_once(session, holder_id="worker-one", now=NOW)
        seed_heartbeat(
            session,
            agent,
            event_id="heartbeat-healthy",
            received_at=NOW + timedelta(seconds=30),
            checks=[{"name": "database", "status": "healthy"}],
        )
        resolved = evaluate_agent_health_once(
            session,
            holder_id="worker-one",
            now=NOW + timedelta(seconds=30),
        )
        session.commit()

        alert = session.scalar(select(AgentAlert))
        assert opened.opened_alerts == 1
        assert resolved.resolved_alerts == 1
        assert alert is not None
        assert alert.status == "resolved"


def test_repeated_failed_execution_alert_opens_and_resolves_after_quiet_period(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
        agent = seed_agent(
            session,
            monitoring_mode="activity_only",
            heartbeat_interval_seconds=None,
        )
        for index in range(3):
            seed_failed_execution(
                session,
                agent,
                external_id=f"failed-{index}",
                terminal_at=NOW - timedelta(minutes=index + 1),
            )

        opened = evaluate_agent_health_once(session, holder_id="worker-one", now=NOW)
        for execution in session.scalars(select(AgentExecution)):
            execution.terminal_at = NOW - timedelta(minutes=61)
        resolved = evaluate_agent_health_once(
            session,
            holder_id="worker-one",
            now=NOW + timedelta(minutes=1),
        )
        session.commit()

        alert = session.scalar(select(AgentAlert))
        assert opened.opened_alerts == 1
        assert resolved.resolved_alerts == 1
        assert alert is not None
        assert alert.status == "resolved"


def test_version_and_environment_mismatch_alerts_open_and_resolve(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
        agent = seed_agent(
            session,
            expected_version="2.0.0",
            last_agent_version="1.0.0",
            last_heartbeat_received_at=NOW,
        )
        seed_heartbeat(
            session,
            agent,
            event_id="heartbeat-staging",
            received_at=NOW,
            environment="staging",
        )

        opened = evaluate_agent_health_once(session, holder_id="worker-one", now=NOW)
        agent.last_agent_version = "2.0.0"
        seed_heartbeat(
            session,
            agent,
            event_id="heartbeat-production",
            received_at=NOW + timedelta(seconds=30),
            environment="production",
        )
        resolved = evaluate_agent_health_once(
            session,
            holder_id="worker-one",
            now=NOW + timedelta(seconds=30),
        )
        session.commit()

        alerts = list(session.scalars(select(AgentAlert)))
        assert opened.opened_alerts == 2
        assert resolved.resolved_alerts == 2
        assert {alert.status for alert in alerts} == {"resolved"}


def test_acknowledged_alert_remains_active_until_source_condition_resolves(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
        agent = seed_agent(
            session,
            last_heartbeat_received_at=NOW - timedelta(minutes=6),
        )
        evaluate_agent_health_once(session, holder_id="worker-one", now=NOW)
        alert = session.scalar(select(AgentAlert))
        assert alert is not None
        acknowledge_alert(
            session,
            alert_id=alert.alert_id,
            acknowledged_by_user_id=OWNER_ID,
            now=NOW + timedelta(seconds=5),
        )

        evaluate_agent_health_once(
            session,
            holder_id="worker-one",
            now=NOW + timedelta(seconds=10),
        )
        session.commit()

        alerts = active_alerts(session, agent)
        assert len(alerts) == 1
        assert alerts[0].status == "acknowledged"


def test_security_ingestion_alert_resolves_after_acknowledged_quiet_period(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner(session)
        agent = seed_agent(session)
        alert = record_security_ingestion_alert(
            session,
            agent_id=agent.agent_id,
            category="secret_pattern",
            reason_code="agent_telemetry_secret_rejected",
            now=NOW,
        )
        acknowledge_alert(
            session,
            alert_id=alert.alert_id,
            acknowledged_by_user_id=OWNER_ID,
            now=NOW + timedelta(minutes=1),
        )
        alert.last_seen_at = NOW - timedelta(hours=25)

        result = evaluate_agent_health_once(
            session,
            holder_id="worker-one",
            now=NOW,
        )
        session.commit()

        assert result.resolved_alerts == 1
        assert alert.status == "resolved"
        assert alert.resolved_reason == "security_ingestion_quiet_period_elapsed"


def test_readiness_reports_evaluator_freshness_when_enabled(
    database_factory: sessionmaker[Session],
) -> None:
    fresh_at = datetime.now(UTC)
    client = TestClient(
        create_app(settings(evaluator_enabled=True), database_factory),
        base_url="https://api.atlas.grafley.com",
    )

    missing = client.get("/health/ready")
    with database_factory() as session:
        session.add(
            AgentHealthEvaluatorLease(
                lease_name=EVALUATOR_LEASE_NAME,
                holder_id="worker-one",
                lease_expires_at=fresh_at + timedelta(seconds=90),
                last_completed_at=fresh_at,
                last_processed_count=0,
            )
        )
        session.commit()
    fresh = client.get("/health/ready")

    assert missing.status_code == 200
    assert missing.json()["status"] == "not_ready"
    assert missing.json()["checks"]["agent_health_evaluator"]["status"] == (
        "never_completed"
    )
    assert "agent_health_evaluator_never_completed" in missing.json()["problems"]
    assert fresh.status_code == 200
    assert fresh.json()["status"] == "ready"
    assert fresh.json()["checks"]["agent_health_evaluator"]["status"] == "fresh"
