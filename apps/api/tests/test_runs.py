from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.external_request_signing import SignedExternalRequest, sign_request
from atlas_api.db.base import Base
from atlas_api.main import create_app
from atlas_api.models.agent import AgentRegistration
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.job import QueueJob
from atlas_api.models.run import AgentRun
from atlas_api.services.agent_registry import create_agent_registration

CLIENT_ID = "external-client-1"
KEY_ID = "current-key"
SECRET = "expected-signing-secret"


def database_factory(*, supports_manual_run: bool = True) -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    with factory() as session:
        owner = User(
            user_id="usr_owner",
            email="owner@example.test",
            display_name="Owner",
            identity_provider="test",
            identity_subject="owner-subject",
            status="active",
        )
        client = ExternalProductClient(
            external_client_id=CLIENT_ID,
            display_name="External Client",
            status="active",
            authentication_key_reference="keyref",
            human_owner_user_id=owner.user_id,
        )
        session.add_all([owner, client])
        create_agent_registration(
            session,
            slug="gmail-agent",
            display_name="Gmail Agent",
            description="Synthetic agent descriptor.",
            version="0.1.0",
            risk_level="medium",
            capabilities=["mail.classify"],
            allowed_tools=["connector.gmail.readonly"],
            required_connectors=["gmail"],
            supports_manual_run=supports_manual_run,
            health_status="healthy",
        )
        session.commit()
    return factory


def configured_settings() -> Settings:
    return Settings(
        environment="test",
        external_client_id=CLIENT_ID,
        external_client_key_id=KEY_ID,
        external_client_secret=SecretStr(SECRET),
    )


def signed_headers(
    *,
    method: str,
    path_query: str,
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
        path_query=path_query,
        body=body,
    )
    return {
        "X-Atlas-Client-Id": CLIENT_ID,
        "X-Atlas-Key-Id": KEY_ID,
        "X-Atlas-Timestamp": str(timestamp),
        "X-Atlas-Nonce": nonce,
        "X-Atlas-Signature": sign_request(signed_request, SECRET),
    }


def json_body(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode()


def agent_id(factory: sessionmaker[Session]) -> str:
    with factory() as session:
        return session.scalar(select(AgentRegistration)).agent_id


def create_run(
    client: TestClient,
    *,
    agent: str,
    nonce: str = "run-create",
    idempotency_key: str = "run-idempotency-key-1",
) -> dict[str, Any]:
    body = json_body({"agent_id": agent, "timeout_seconds": 300})
    response = client.post(
        "/api/v1/runs",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
            **signed_headers(
                method="POST",
                path_query="/api/v1/runs",
                nonce=nonce,
                body=body,
            ),
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_manual_run_creation_is_idempotent_and_enqueues_reference_only_job() -> None:
    factory = database_factory()
    client = TestClient(create_app(configured_settings(), factory))
    agent = agent_id(factory)

    created = create_run(client, agent=agent)
    replayed = create_run(client, agent=agent, nonce="run-create-replay")

    assert replayed["run_id"] == created["run_id"]
    assert created["status"] == "queued"
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(AgentRun)) == 1
        job = session.scalar(select(QueueJob))
        assert job is not None
        assert job.job_type == "agent.run"
        assert job.payload_metadata == {
            "run_id": created["run_id"],
            "agent_id": agent,
            "trigger_source": "manual",
        }
        assert "body" not in json.dumps(job.payload_metadata)
        audit_actions = list(
            session.scalars(
                select(AuditEvent.action).where(AuditEvent.resource_type == "agent_run")
            )
        )
    assert audit_actions == ["create", "create"]


def test_run_list_read_and_cancel_update_lifecycle_without_execution() -> None:
    factory = database_factory()
    client = TestClient(create_app(configured_settings(), factory))
    created = create_run(client, agent=agent_id(factory))
    run_id = created["run_id"]

    listed = client.get(
        "/api/v1/runs?status=queued",
        headers=signed_headers(
            method="GET",
            path_query="/api/v1/runs?status=queued",
            nonce="run-list",
        ),
    )
    read = client.get(
        f"/api/v1/runs/{run_id}",
        headers=signed_headers(
            method="GET",
            path_query=f"/api/v1/runs/{run_id}",
            nonce="run-read",
        ),
    )
    cancelled = client.post(
        f"/api/v1/runs/{run_id}/cancel",
        headers={
            "Idempotency-Key": "run-cancel-key-1",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/runs/{run_id}/cancel",
                nonce="run-cancel",
            ),
        },
    )

    assert listed.status_code == 200
    assert listed.json()["data"][0]["run_id"] == run_id
    assert read.status_code == 200
    assert read.json()["data"]["started_at"] is None
    assert cancelled.status_code == 200
    assert cancelled.json()["data"]["status"] == "cancelled"
    with factory() as session:
        job = session.scalar(select(QueueJob))
        assert job.state == "cancelled"


def test_run_creation_rejects_unsupported_agent_and_requires_idempotency() -> None:
    unsupported_factory = database_factory(supports_manual_run=False)
    client = TestClient(create_app(configured_settings(), unsupported_factory))
    agent = agent_id(unsupported_factory)
    body = json_body({"agent_id": agent, "timeout_seconds": 300})

    missing_idempotency = client.post(
        "/api/v1/runs",
        content=body,
        headers={
            "Content-Type": "application/json",
            **signed_headers(
                method="POST",
                path_query="/api/v1/runs",
                nonce="run-missing-idempotency",
                body=body,
            ),
        },
    )
    unsupported = client.post(
        "/api/v1/runs",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "run-unsupported-key-1",
            **signed_headers(
                method="POST",
                path_query="/api/v1/runs",
                nonce="run-unsupported",
                body=body,
            ),
        },
    )

    assert missing_idempotency.status_code == 422
    assert unsupported.status_code == 409
    assert unsupported.json()["error"]["code"] == "agent_manual_run_unsupported"


def test_run_openapi_declares_hmac_security() -> None:
    client = TestClient(create_app(configured_settings(), database_factory()))

    schema = client.get("/openapi.json").json()

    operation = schema["paths"]["/api/v1/runs"]["post"]
    assert operation["security"] == [{"ExternalClientHmac": []}]
