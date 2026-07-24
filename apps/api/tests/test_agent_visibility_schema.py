from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.contracts import PaginationParameters
from atlas_api.db.base import Base
from atlas_api.models.agent import (
    AgentActivityEvent,
    AgentAlert,
    AgentCredential,
    AgentExecution,
    AgentHealthEvaluatorLease,
    AgentHeartbeat,
    AgentIngestionRateLimit,
    AgentRegistration,
)
from atlas_api.services.agent_registry import list_agent_registrations


@pytest.fixture
def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine)


def agent_registration(
    slug: str,
    *,
    active_surface_visible: bool = True,
    registration_source: str = "owner_enrolled",
) -> AgentRegistration:
    return AgentRegistration(
        slug=slug,
        display_name=f"{slug} display",
        description="Agent visibility schema test agent.",
        version="1.0.0",
        risk_level="low",
        capabilities=["telemetry.report"],
        allowed_tools=["atlas.telemetry.write"],
        required_connectors=[],
        configuration_schema={},
        active_surface_visible=active_surface_visible,
        registration_source=registration_source,
        lifecycle_status="pending",
        monitoring_mode="heartbeat",
        heartbeat_interval_seconds=60,
        observed_health="never_seen",
        reported_health="unknown",
    )


def test_agent_visibility_tables_are_registered_in_metadata() -> None:
    expected_tables = {
        "agent_registrations",
        "agent_credentials",
        "agent_heartbeats",
        "agent_executions",
        "agent_health_evaluator_leases",
        "agent_alerts",
        "agent_activity_events",
        "agent_ingestion_rate_limits",
    }

    assert expected_tables.issubset(Base.metadata.tables)

    registration_columns = Base.metadata.tables["agent_registrations"].c
    for column_name in (
        "owner_user_id",
        "registration_source",
        "active_surface_visible",
        "lifecycle_status",
        "environment",
        "monitoring_mode",
        "heartbeat_interval_seconds",
        "tags",
        "observed_health",
        "reported_health",
    ):
        assert column_name in registration_columns


def test_new_agent_registration_defaults_to_visible_owner_enrolled(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        agent = agent_registration("owner-agent")
        session.add(agent)
        session.flush()

        assert agent.registration_source == "owner_enrolled"
        assert agent.active_surface_visible is True
        assert agent.lifecycle_status == "pending"
        assert agent.environment == "production"
        assert agent.monitoring_mode == "heartbeat"
        assert agent.heartbeat_interval_seconds == 60
        assert agent.tags == []
        assert agent.observed_health == "never_seen"
        assert agent.reported_health == "unknown"


def test_active_surface_selector_excludes_hidden_legacy_and_synthetic_rows(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        visible = agent_registration("visible-agent")
        legacy = agent_registration(
            "legacy-agent",
            active_surface_visible=False,
            registration_source="legacy_descriptor",
        )
        synthetic = agent_registration(
            "hosted-runtime-smoke-agent",
            active_surface_visible=False,
            registration_source="synthetic_smoke",
        )
        session.add_all([visible, legacy, synthetic])
        session.flush()

        page = list_agent_registrations(
            session,
            pagination=PaginationParameters(cursor=None, limit=10),
            active_surface_only=True,
        )

        assert [agent.slug for agent in page.agents] == ["visible-agent"]


def test_registration_monitoring_constraints_reject_invalid_interval(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        agent = agent_registration("bad-interval")
        agent.heartbeat_interval_seconds = 10
        session.add(agent)

        with pytest.raises(IntegrityError):
            session.flush()


def test_alert_active_condition_is_unique_until_resolved(
    database_factory: sessionmaker[Session],
) -> None:
    now = datetime.now(UTC)
    with database_factory() as session:
        agent = agent_registration("alert-agent")
        session.add(agent)
        session.flush()
        first = AgentAlert(
            agent_id=agent.agent_id,
            condition_key=f"agent:{agent.agent_id}:missed-heartbeat",
            status="open",
            severity="warning",
            first_seen_at=now,
            last_seen_at=now,
            evidence_json={"observed_health": "late"},
        )
        session.add(first)
        session.flush()

        duplicate = AgentAlert(
            agent_id=agent.agent_id,
            condition_key=first.condition_key,
            status="acknowledged",
            severity="warning",
            first_seen_at=now,
            last_seen_at=now,
            evidence_json={"observed_health": "offline"},
        )
        session.add(duplicate)
        with pytest.raises(IntegrityError):
            session.flush()

        session.rollback()
        agent = agent_registration("resolved-alert-agent")
        session.add(agent)
        session.flush()
        condition_key = f"agent:{agent.agent_id}:missed-heartbeat"
        session.add_all(
            [
                AgentAlert(
                    agent_id=agent.agent_id,
                    condition_key=condition_key,
                    status="resolved",
                    severity="warning",
                    first_seen_at=now,
                    last_seen_at=now,
                    evidence_json={},
                ),
                AgentAlert(
                    agent_id=agent.agent_id,
                    condition_key=condition_key,
                    status="open",
                    severity="warning",
                    first_seen_at=now,
                    last_seen_at=now,
                    evidence_json={},
                ),
            ]
        )
        session.flush()

        alerts = list(session.scalars(select(AgentAlert)))
        assert {alert.status for alert in alerts} == {"resolved", "open"}


def test_agent_visibility_model_defaults_are_plaintext_credential_free(
    database_factory: sessionmaker[Session],
) -> None:
    now = datetime.now(UTC)
    with database_factory() as session:
        agent = agent_registration("schema-agent")
        session.add(agent)
        session.flush()
        credential = AgentCredential(
            agent_id=agent.agent_id,
            credential_lookup_id="cred_schema_agent",
            verifier_hmac_sha256="a" * 64,
            verifier_key_id="test-key",
            issued_at=now,
        )
        session.add(credential)
        session.flush()

        session.add_all(
            [
                AgentHeartbeat(
                    agent_id=agent.agent_id,
                    credential_id=credential.credential_id,
                    event_id="heartbeat-1",
                    event_fingerprint="fingerprint-1",
                    contract_version="2026-07-24",
                    sent_at=now,
                    received_at=now,
                    environment="production",
                    reported_status="healthy",
                    checks_json=[],
                ),
                AgentExecution(
                    agent_id=agent.agent_id,
                    external_execution_id="external-run-1",
                    representation_hash="hash-1",
                    status="succeeded",
                    trigger="schedule",
                    summary="Completed outside Atlas.",
                    first_reported_at=now,
                    last_reported_at=now,
                    terminal_at=now,
                ),
                AgentHealthEvaluatorLease(
                    lease_name="agent-health-evaluator",
                    holder_id="worker-1",
                    last_processed_count=0,
                ),
                AgentActivityEvent(
                    agent_id=agent.agent_id,
                    source_type="agent",
                    source_id=agent.agent_id,
                    event_type="agent.enrolled",
                    severity="info",
                    summary="Agent enrolled.",
                    actor_type="owner",
                    metadata_json={},
                    occurred_at=now,
                ),
                AgentIngestionRateLimit(
                    credential_id=credential.credential_id,
                    route_key="heartbeat",
                    window_start=now,
                    request_count=1,
                ),
            ]
        )
        session.flush()

        credential_columns = Base.metadata.tables["agent_credentials"].c
        assert "plaintext" not in credential_columns
        assert "secret" not in credential_columns
        assert "verifier_hmac_sha256" in credential_columns
