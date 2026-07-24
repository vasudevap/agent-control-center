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
    AgentCredential,
    AgentExecution,
    AgentHeartbeat,
    AgentIngestionRateLimit,
    AgentRegistration,
)
from atlas_api.models.external_client import User
from atlas_api.services.agent_credentials import issue_agent_credential

OWNER_ID = "usr_telemetry_owner"
CONTRACT_VERSION = "2026-07-24"


@pytest.fixture
def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine)


@pytest.fixture
def client(database_factory: sessionmaker[Session]) -> TestClient:
    return TestClient(
        create_app(settings(), database_factory),
        base_url="https://api.atlas.grafley.com",
    )


def settings() -> Settings:
    return Settings(
        environment="test",
        owner_identity_subject="owner-one",
        agent_credential_pepper=SecretStr("agent-credential-pepper"),
        agent_credential_pepper_key_id="pepper-key-1",
    )


def seed_agent_with_token(
    database_factory: sessionmaker[Session],
    *,
    slug: str = "telemetry-agent",
    lifecycle_status: str = "pending",
) -> tuple[str, str]:
    with database_factory() as session:
        user = session.get(User, OWNER_ID)
        if user is None:
            user = User(
                user_id=OWNER_ID,
                email="telemetry-owner@example.test",
                display_name="Telemetry Owner",
                identity_provider="google",
                identity_subject="owner-one",
                status="active",
            )
            session.add(user)
        agent = AgentRegistration(
            slug=slug,
            display_name=f"{slug} display",
            description="Reports external telemetry to Atlas.",
            version="1.0.0",
            risk_level="low",
            capabilities=["telemetry.report"],
            allowed_tools=["atlas.telemetry.write"],
            required_connectors=[],
            configuration_schema={},
            owner_user_id=user.user_id,
            lifecycle_status=lifecycle_status,
        )
        session.add_all([user, agent])
        session.flush()
        issued = issue_agent_credential(session, agent=agent, settings=settings())
        agent_id = agent.agent_id
        token = issued.plaintext_token
        session.commit()
    return agent_id, token


def heartbeat_payload(
    event_id: str = "heartbeat-1",
    *,
    status: str = "healthy",
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "contract_version": CONTRACT_VERSION,
        "sent_at": "2026-07-24T14:00:00Z",
        "environment": "production",
        "status": status,
        "checks": [{"name": "database", "status": status}],
        "agent_version": "1.2.3",
        "build_sha": "abc123",
    }


def execution_payload(
    representation_hash: str = "hash-running",
    *,
    status: str = "running",
    started_at: str = "2026-07-24T14:00:00Z",
    finished_at: str | None = None,
) -> dict[str, object]:
    return {
        "contract_version": CONTRACT_VERSION,
        "representation_hash": representation_hash,
        "status": status,
        "trigger": "schedule",
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_ms": 10 if finished_at is not None else None,
        "summary": "Agent reported work executed outside Atlas.",
        "correlation_id": "corr-agent-run-1",
        "agent_version": "1.2.3",
        "build_sha": "abc123",
    }


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_valid_heartbeat_returns_accepted_and_connects_pending_agent(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    agent_id, token = seed_agent_with_token(database_factory)

    response = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=heartbeat_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code == 202
    data = response.json()["data"]
    assert data["agent_id"] == agent_id
    assert data["event_id"] == "heartbeat-1"
    assert data["replayed"] is False

    with database_factory() as session:
        agent = session.get(AgentRegistration, agent_id)
        heartbeat = session.scalar(select(AgentHeartbeat))
        credential = session.scalar(select(AgentCredential))
        assert agent is not None
        assert heartbeat is not None
        assert credential is not None
        assert heartbeat.credential_id == credential.credential_id
        assert agent.lifecycle_status == "connected"
        assert agent.first_connected_at is not None
        assert agent.last_heartbeat_received_at is not None
        assert agent.last_activity_at is not None
        assert agent.reported_health == "healthy"
        assert agent.last_agent_version == "1.2.3"
        assert agent.last_build_sha == "abc123"


def test_heartbeat_replay_is_idempotent_but_conflicting_replay_fails(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    agent_id, token = seed_agent_with_token(database_factory)
    payload = heartbeat_payload("heartbeat-replay")

    first = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=payload,
        headers=auth_headers(token),
    )
    replay = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=payload,
        headers=auth_headers(token),
    )
    conflict_payload = heartbeat_payload("heartbeat-replay", status="degraded")
    conflict = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=conflict_payload,
        headers=auth_headers(token),
    )

    assert first.status_code == 202
    assert replay.status_code == 202
    assert replay.json()["data"]["replayed"] is True
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "agent_heartbeat_replay_conflict"

    with database_factory() as session:
        heartbeats = list(session.scalars(select(AgentHeartbeat)))
        assert len(heartbeats) == 1


def test_credential_failures_are_closed(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    first_agent_id, first_token = seed_agent_with_token(
        database_factory,
        slug="first-agent",
    )
    second_agent_id, _ = seed_agent_with_token(database_factory, slug="second-agent")

    missing = client.post(
        f"/api/v1/agents/{first_agent_id}/heartbeats",
        json=heartbeat_payload("missing-auth"),
    )
    invalid = client.post(
        f"/api/v1/agents/{first_agent_id}/heartbeats",
        json=heartbeat_payload("invalid-auth"),
        headers=auth_headers("atl_agent_cred_unknown.bad-secret"),
    )
    mismatch = client.post(
        f"/api/v1/agents/{second_agent_id}/heartbeats",
        json=heartbeat_payload("mismatch-auth"),
        headers=auth_headers(first_token),
    )
    with database_factory() as session:
        credential = session.scalar(select(AgentCredential))
        assert credential is not None
        credential.status = "revoked"
        session.commit()
    revoked = client.post(
        f"/api/v1/agents/{first_agent_id}/heartbeats",
        json=heartbeat_payload("revoked-auth"),
        headers=auth_headers(first_token),
    )

    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "agent_credential_missing"
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "agent_credential_invalid"
    assert mismatch.status_code == 403
    assert mismatch.json()["error"]["code"] == "agent_credential_agent_mismatch"
    assert revoked.status_code == 401
    assert revoked.json()["error"]["code"] == "agent_credential_invalid"


def test_disconnected_and_archived_agents_reject_telemetry(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    disconnected_agent_id, disconnected_token = seed_agent_with_token(
        database_factory,
        slug="disconnected-agent",
        lifecycle_status="disconnected",
    )
    archived_agent_id, archived_token = seed_agent_with_token(
        database_factory,
        slug="archived-agent",
        lifecycle_status="archived",
    )

    disconnected = client.post(
        f"/api/v1/agents/{disconnected_agent_id}/heartbeats",
        json=heartbeat_payload("disconnected"),
        headers=auth_headers(disconnected_token),
    )
    archived = client.put(
        f"/api/v1/agents/{archived_agent_id}/executions/external-1",
        json=execution_payload(),
        headers=auth_headers(archived_token),
    )

    assert disconnected.status_code == 401
    assert disconnected.json()["error"]["code"] == (
        "agent_lifecycle_rejects_telemetry"
    )
    assert archived.status_code == 401
    assert archived.json()["error"]["code"] == "agent_lifecycle_rejects_telemetry"


def test_secret_like_telemetry_content_is_rejected(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    agent_id, token = seed_agent_with_token(database_factory)
    secret_like_value = "sk-" + ("a" * 16)
    payload = execution_payload("hash-secret", status="failed")
    payload["summary"] = f"Agent accidentally included {secret_like_value}"

    response = client.put(
        f"/api/v1/agents/{agent_id}/executions/external-secret",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "agent_telemetry_secret_rejected"


def test_arbitrary_extra_telemetry_fields_are_rejected(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    agent_id, token = seed_agent_with_token(database_factory)
    payload = heartbeat_payload("extra-field")
    payload["raw_logs"] = "arbitrary provider payload is out of scope"

    response = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_contract_version_and_payload_bounds_are_enforced(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    agent_id, token = seed_agent_with_token(database_factory)
    bad_contract = heartbeat_payload("bad-contract")
    bad_contract["contract_version"] = "2026-01-01"
    too_many_checks = heartbeat_payload("too-many-checks")
    too_many_checks["checks"] = [
        {"name": f"check-{index}", "status": "healthy"} for index in range(21)
    ]

    contract_response = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=bad_contract,
        headers=auth_headers(token),
    )
    bounds_response = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=too_many_checks,
        headers=auth_headers(token),
    )

    assert contract_response.status_code == 422
    assert contract_response.json()["error"]["code"] == (
        "agent_contract_version_unsupported"
    )
    assert bounds_response.status_code == 422


def test_heartbeat_rate_limit_enforces_route_and_global_windows(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    agent_id, token = seed_agent_with_token(database_factory)

    for index in range(30):
        response = client.post(
            f"/api/v1/agents/{agent_id}/heartbeats",
            json=heartbeat_payload(f"heartbeat-{index}"),
            headers=auth_headers(token),
        )
        assert response.status_code == 202

    limited = client.post(
        f"/api/v1/agents/{agent_id}/heartbeats",
        json=heartbeat_payload("heartbeat-limited"),
        headers=auth_headers(token),
    )

    assert limited.status_code == 429
    assert limited.json()["error"]["code"] == "agent_ingestion_rate_limited"

    with database_factory() as session:
        limits = {
            limit.route_key: limit.request_count
            for limit in session.scalars(select(AgentIngestionRateLimit))
        }
        assert limits == {"heartbeats": 30, "telemetry": 30}


def test_execution_upsert_is_idempotent_and_rejects_regressions(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    agent_id, token = seed_agent_with_token(database_factory)
    endpoint = f"/api/v1/agents/{agent_id}/executions/external-run-1"
    running_payload = execution_payload("hash-running", status="running")

    created = client.put(endpoint, json=running_payload, headers=auth_headers(token))
    replay = client.put(endpoint, json=running_payload, headers=auth_headers(token))
    terminal_payload = execution_payload(
        "hash-succeeded",
        status="succeeded",
        finished_at="2026-07-24T14:00:05Z",
    )
    terminal = client.put(endpoint, json=terminal_payload, headers=auth_headers(token))
    regression_payload = execution_payload("hash-regression", status="running")
    regression = client.put(
        endpoint,
        json=regression_payload,
        headers=auth_headers(token),
    )

    assert created.status_code == 201
    assert created.json()["data"]["created"] is True
    assert replay.status_code == 200
    assert replay.json()["data"]["created"] is False
    assert terminal.status_code == 200
    assert terminal.json()["data"]["status"] == "succeeded"
    assert regression.status_code == 409
    assert regression.json()["error"]["code"] == (
        "agent_execution_terminal_regression"
    )

    with database_factory() as session:
        execution = session.scalar(select(AgentExecution))
        agent = session.get(AgentRegistration, agent_id)
        assert execution is not None
        assert agent is not None
        assert execution.status == "succeeded"
        assert execution.terminal_at is not None
        assert agent.last_activity_at is not None


def test_execution_rejects_immutable_started_at_conflict(
    database_factory: sessionmaker[Session],
    client: TestClient,
) -> None:
    agent_id, token = seed_agent_with_token(database_factory)
    endpoint = f"/api/v1/agents/{agent_id}/executions/external-run-immutable"

    created = client.put(
        endpoint,
        json=execution_payload("hash-first", status="running"),
        headers=auth_headers(token),
    )
    conflict = client.put(
        endpoint,
        json=execution_payload(
            "hash-second",
            status="running",
            started_at="2026-07-24T14:01:00Z",
        ),
        headers=auth_headers(token),
    )

    assert created.status_code == 201
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == (
        "agent_execution_immutable_timestamp_conflict"
    )


def test_global_rate_limit_caps_combined_telemetry_requests(
    database_factory: sessionmaker[Session],
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    agent_id, token = seed_agent_with_token(database_factory)
    now = datetime(2026, 7, 24, 14, 0, tzinfo=UTC)
    monkeypatch.setattr("atlas_api.services.agent_telemetry.utc_now", lambda: now)
    with database_factory() as session:
        credential = session.scalar(select(AgentCredential))
        assert credential is not None
        session.add(
            AgentIngestionRateLimit(
                credential_id=credential.credential_id,
                route_key="telemetry",
                window_start=now.replace(second=0, microsecond=0),
                request_count=60,
            )
        )
        session.commit()

    response = client.put(
        f"/api/v1/agents/{agent_id}/executions/external-rate-limited",
        json=execution_payload(
            "hash-rate-limited",
            status="running",
            started_at=(now + timedelta(seconds=10)).isoformat(),
        ),
        headers=auth_headers(token),
    )

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "agent_ingestion_rate_limited"
