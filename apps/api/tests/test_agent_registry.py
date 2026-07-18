from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.core.external_request_signing import SignedExternalRequest, sign_request
from atlas_api.db.base import Base
from atlas_api.main import create_app
from atlas_api.models.agent import AgentRegistration
from atlas_api.models.audit import AuditEvent
from atlas_api.services.agent_registry import create_agent_registration
from atlas_api.services.agent_runtime import (
    AgentHealth,
    AgentRuntimeDescriptor,
)

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


def signed_headers(path: str, *, nonce: str = "nonce-1") -> dict[str, str]:
    timestamp = int(datetime.now(UTC).timestamp())
    signed_request = SignedExternalRequest(
        client_id=CLIENT_ID,
        key_id=KEY_ID,
        timestamp=timestamp,
        nonce=nonce,
        signature="",
        method="GET",
        path_query=path,
        body=b"",
    )
    return {
        "X-Atlas-Client-Id": CLIENT_ID,
        "X-Atlas-Key-Id": KEY_ID,
        "X-Atlas-Timestamp": str(timestamp),
        "X-Atlas-Nonce": nonce,
        "X-Atlas-Signature": sign_request(signed_request, SECRET),
    }


def seed_agent(session: Session) -> AgentRegistration:
    return create_agent_registration(
        session,
        slug="gmail-agent",
        display_name="Gmail Agent",
        description="Synthetic MVP candidate descriptor.",
        version="0.1.0",
        risk_level="medium",
        capabilities=["mail.classify", "mail.draft"],
        allowed_tools=["connector.gmail.readonly"],
        required_connectors=["gmail"],
        configuration_schema_ref="schemas/agents/gmail-agent-v1.json",
        configuration_schema={
            "type": "object",
            "properties": {
                "max_messages": {"type": "integer", "minimum": 1, "maximum": 50}
            },
        },
        supports_manual_run=True,
        supports_scheduled_run=True,
        health_status="healthy",
    )


def test_agent_registry_metadata_is_distinct_and_secret_free() -> None:
    table = Base.metadata.tables["agent_registrations"]

    assert "agent_id" in table.c
    assert "required_connectors" in table.c
    assert "configuration_schema" in table.c
    assert "credential" not in table.c
    assert "oauth_token" not in table.c


def test_agent_descriptor_validation_rejects_secret_bearing_schema(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        with pytest.raises(ApiError) as error:
            create_agent_registration(
                session,
                slug="unsafe-agent",
                display_name="Unsafe Agent",
                description="Rejected descriptor.",
                version="0.1.0",
                risk_level="low",
                capabilities=["mail.classify"],
                allowed_tools=["connector.gmail.readonly"],
                required_connectors=["gmail"],
                configuration_schema={
                    "properties": {"oauth_token": {"type": "string"}}
                },
            )

    assert error.value.code == "agent_configuration_schema_prohibited"
    assert error.value.details == {"fields": ["properties.oauth_token"]}


def test_agent_registry_list_and_read_contracts_require_signed_client_and_audit(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        agent = seed_agent(session)
        agent_id = agent.agent_id
        session.commit()

    client = TestClient(create_app(configured_settings(), database_factory))

    unauthenticated = client.get("/api/v1/agents")
    assert unauthenticated.status_code == 401

    listed = client.get(
        "/api/v1/agents?limit=10",
        headers=signed_headers("/api/v1/agents?limit=10", nonce="agents-list"),
    )
    assert listed.status_code == 200
    payload = listed.json()
    assert payload["data"][0]["agent_id"] == agent_id
    assert payload["data"][0]["required_connectors"] == ["gmail"]
    assert "secret" not in listed.text.lower()

    read = client.get(
        f"/api/v1/agents/{agent_id}",
        headers=signed_headers(f"/api/v1/agents/{agent_id}", nonce="agent-read"),
    )
    assert read.status_code == 200
    assert read.json()["data"]["slug"] == "gmail-agent"

    with database_factory() as session:
        audit_actions = list(
            session.scalars(
                select(AuditEvent.action).where(
                    AuditEvent.resource_type == "agent_registration"
                )
            )
        )
    assert audit_actions == ["list", "read"]


def test_agent_status_and_health_contracts_are_separate(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        agent = seed_agent(session)
        agent_id = agent.agent_id
        session.commit()

    client = TestClient(create_app(configured_settings(), database_factory))

    status = client.get(
        f"/api/v1/agents/{agent_id}/status",
        headers=signed_headers(
            f"/api/v1/agents/{agent_id}/status",
            nonce="agent-status",
        ),
    )
    health = client.get(
        f"/api/v1/agents/{agent_id}/health",
        headers=signed_headers(
            f"/api/v1/agents/{agent_id}/health",
            nonce="agent-health",
        ),
    )

    assert status.status_code == 200
    assert status.json()["data"] == {
        "agent_id": agent_id,
        "status": "active",
        "health_status": "healthy",
        "updated_at": status.json()["data"]["updated_at"],
    }
    assert health.status_code == 200
    assert health.json()["data"]["last_error_code"] is None


def test_agent_runtime_contract_is_non_executing_descriptor_shape() -> None:
    descriptor = AgentRuntimeDescriptor(
        agent_id="agt_test",
        version="0.1.0",
        capabilities=("mail.classify",),
        required_connectors=("gmail",),
        allowed_tools=("connector.gmail.readonly",),
        risk_level="medium",
        supports_manual_run=True,
        supports_scheduled_run=False,
    )
    health = AgentHealth(status="healthy", checked_at_iso="2026-07-18T00:00:00Z")

    assert descriptor.required_connectors == ("gmail",)
    assert health.status == "healthy"


def test_agent_registry_openapi_declares_hmac_security() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    schema: dict[str, Any] = client.get("/openapi.json").json()

    assert "agents" in {tag["name"] for tag in schema["tags"]}
    operation = schema["paths"]["/api/v1/agents"]["get"]
    assert operation["security"] == [{"ExternalClientHmac": []}]
