from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

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
from atlas_api.models import (  # noqa: F401
    agent,
    approval,
    audit,
    external_client,
    external_request_nonce,
    idempotency,
    job,
    knowledge,
    owner_session,
    run,
    schedule,
    webhook,
)
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.webhook import WebhookSubscription
from atlas_api.services.agent_registry import create_agent_registration
from atlas_api.services.approval_contracts import create_approval_request
from atlas_api.services.approval_facts import attach_facts_used_evidence
from atlas_api.services.audit import record_webhook_audit_event
from atlas_api.services.knowledge_facts import update_fact
from atlas_api.services.platform_events import (
    enqueue_platform_webhook_event,
    run_state_changed_event,
)
from atlas_api.services.webhook_delivery import (
    RecordingWebhookTransport,
    WebhookAuditEvent,
    WebhookDeliveryResult,
    WebhookDeliveryService,
)

CLIENT_ID = "phase5-client"
KEY_ID = "phase5-key"
SECRET = "phase5-secret"
WEBHOOK_KEY_ID = "phase5-webhook-key"
WEBHOOK_SECRET = "phase5-webhook-secret"
OWNER_ID = "usr_phase5_owner"


@pytest.mark.anyio
async def test_phase5_contract_smoke_path_is_coherent_and_fail_closed() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    settings = Settings(
        environment="test",
        external_client_id=CLIENT_ID,
        external_client_key_id=KEY_ID,
        external_client_secret=SecretStr(SECRET),
        webhook_signing_key_id=WEBHOOK_KEY_ID,
        webhook_signing_secret=SecretStr(WEBHOOK_SECRET),
    )
    agent_id = _seed_phase5_records(factory)
    client = TestClient(create_app(settings, factory))
    correlation_id = "corr-phase5-closeout"

    agents = client.get(
        "/api/v1/agents?limit=10",
        headers={
            "X-Correlation-Id": correlation_id,
            **_signed_headers(method="GET", path_query="/api/v1/agents?limit=10"),
        },
    )
    assert agents.status_code == 200
    assert agents.json()["data"][0]["agent_id"] == agent_id

    run_body = _json_body({"agent_id": agent_id, "timeout_seconds": 300})
    created_run = client.post(
        "/api/v1/runs",
        content=run_body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "phase5-run-create",
            "X-Correlation-Id": correlation_id,
            **_signed_headers(
                method="POST",
                path_query="/api/v1/runs",
                nonce="phase5-run-create",
                body=run_body,
            ),
        },
    )
    assert created_run.status_code == 201
    run_payload = created_run.json()["data"]
    assert run_payload["status"] == "queued"
    assert "body" not in json.dumps(run_payload)

    fact_payload = {
        "fact_key": "reply.preference",
        "display_value": "Use concise replies for scheduling requests.",
        "classification": "internal",
        "source_type": "human",
        "source_reference": "manual-entry",
        "provenance_summary": "Owner provided this preference directly.",
        "is_volatile": False,
        "confirmed": True,
    }
    fact_body = _json_body(fact_payload)
    fact_response = client.post(
        "/api/v1/knowledge/facts",
        content=fact_body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "phase5-fact-create",
            "X-Correlation-Id": correlation_id,
            **_signed_headers(
                method="POST",
                path_query="/api/v1/knowledge/facts",
                nonce="phase5-fact-create",
                body=fact_body,
            ),
        },
    )
    assert fact_response.status_code == 201
    fact_id = fact_response.json()["data"]["knowledge_fact_id"]

    approval_id = _seed_approval_with_fact(factory, fact_id, run_payload["run_id"])
    evidence = client.get(
        f"/api/v1/approvals/{approval_id}/evidence",
        headers={
            "X-Correlation-Id": correlation_id,
            **_signed_headers(
                method="GET",
                path_query=f"/api/v1/approvals/{approval_id}/evidence",
                nonce="phase5-approval-evidence",
            ),
        },
    )
    assert evidence.status_code == 200
    facts_used = evidence.json()["data"]["evidence_summary"]["facts_used"]
    assert facts_used[0]["knowledge_fact_id"] == fact_id
    assert "display_value" not in facts_used[0]

    decision_body = _json_body(
        {
            "decision": "approve",
            "approval_revision": 2,
            "reason": "Synthetic closeout approval.",
        }
    )
    decision = client.post(
        f"/api/v1/approvals/{approval_id}/decisions",
        content=decision_body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "phase5-approval-decision",
            "X-Correlation-Id": correlation_id,
            **_signed_headers(
                method="POST",
                path_query=f"/api/v1/approvals/{approval_id}/decisions",
                nonce="phase5-approval-decision",
                body=decision_body,
            ),
        },
    )
    assert decision.status_code == 200
    assert decision.json()["data"]["continuation_status"] == "pending"

    passed = client.post(
        f"/api/v1/approvals/{approval_id}/facts-used/revalidate",
        headers={
            "X-Correlation-Id": correlation_id,
            **_signed_headers(
                method="POST",
                path_query=f"/api/v1/approvals/{approval_id}/facts-used/revalidate",
                nonce="phase5-revalidate-pass",
            ),
        },
    )
    assert passed.status_code == 200
    assert passed.json()["data"]["status"] == "passed"
    assert passed.json()["data"]["continuation_status"] == "ready"

    with factory() as session:
        update_fact(
            session,
            owner_user_id=OWNER_ID,
            knowledge_fact_id=fact_id,
            display_value="Use detailed replies with three scheduling options.",
            source_type="human",
            source_reference="manual-update",
            provenance_summary="Owner changed the preference.",
            is_volatile=False,
            confirmed=True,
        )
        session.commit()

    failed = client.post(
        f"/api/v1/approvals/{approval_id}/facts-used/revalidate",
        headers={
            "X-Correlation-Id": correlation_id,
            **_signed_headers(
                method="POST",
                path_query=f"/api/v1/approvals/{approval_id}/facts-used/revalidate",
                nonce="phase5-revalidate-fail",
            ),
        },
    )
    assert failed.status_code == 200
    assert failed.json()["data"]["status"] == "failed"
    assert failed.json()["data"]["continuation_status"] == "blocked"
    assert failed.json()["data"]["failure_reason_code"] == "fact_revision_changed"

    unsafe_body = _json_body(
        {
            **fact_payload,
            "fact_key": "unsafe.fact",
            "display_value": "Clinical diagnosis says protected health detail.",
        }
    )
    unsafe_fact = client.post(
        "/api/v1/knowledge/facts",
        content=unsafe_body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "phase5-unsafe-fact",
            **_signed_headers(
                method="POST",
                path_query="/api/v1/knowledge/facts",
                nonce="phase5-unsafe-fact",
                body=unsafe_body,
            ),
        },
    )
    assert unsafe_fact.status_code == 422
    assert unsafe_fact.json()["error"]["code"] == "knowledge_fact_prohibited_content"

    rejected = client.get(
        "/api/v1/agents?limit=10",
        headers=_signed_headers(
            method="GET",
            path_query="/api/v1/agents?limit=10",
            nonce="phase5-bad-signature",
            secret="wrong-secret",
        ),
    )
    assert rejected.status_code == 401

    with factory() as session:

        def webhook_audit(event: WebhookAuditEvent) -> None:
            record_webhook_audit_event(session, event, correlation_id=correlation_id)

        attempts = enqueue_platform_webhook_event(
            session,
            run_state_changed_event(
                run_id=run_payload["run_id"],
                status="queued",
                trigger_source="manual",
            ),
            correlation_id=correlation_id,
            now=datetime(2026, 7, 18, tzinfo=UTC),
            settings=settings,
            audit_hook=webhook_audit,
        )
        transport = RecordingWebhookTransport(WebhookDeliveryResult("delivered"))
        delivered = await WebhookDeliveryService(transport, settings).deliver_due(
            session,
            now=datetime(2026, 7, 18, 0, 1, tzinfo=UTC),
            audit_hook=webhook_audit,
        )
        session.commit()

        assert len(attempts) == 1
        assert delivered == 1
        body = transport.sent[0].body.decode()
        assert "Clinical diagnosis" not in body
        assert "protected health" not in body
        assert transport.sent[0].headers["X-Atlas-Key-Id"] == WEBHOOK_KEY_ID

        audit_events = session.scalars(select(AuditEvent)).all()
        assert {
            "agent_registry.list",
            "agent_run.create",
            "knowledge_fact.create",
            "approval.read_evidence",
            "approval.decide",
            "approval.revalidate_facts",
            "webhook.delivery_queued",
            "webhook.delivery_delivered",
        }.issubset({event.event_type for event in audit_events})
        assert all(event.redaction_state == "metadata_only" for event in audit_events)
        assert SECRET not in json.dumps([event.metadata_json for event in audit_events])
        assert WEBHOOK_SECRET not in json.dumps(
            [event.metadata_json for event in audit_events]
        )


def _seed_phase5_records(factory: sessionmaker[Session]) -> str:
    with factory.begin() as session:
        owner = User(
            user_id=OWNER_ID,
            email="owner@example.test",
            display_name="Owner",
            identity_provider="test",
            identity_subject="owner-subject",
            status="active",
        )
        client = ExternalProductClient(
            external_client_id=CLIENT_ID,
            display_name="Phase 5 Client",
            status="active",
            authentication_key_reference="phase5-key-reference",
            human_owner_user_id=owner.user_id,
        )
        session.add_all([owner, client])
        agent_registration = create_agent_registration(
            session,
            slug="gmail-agent",
            display_name="Gmail Agent Contract Fixture",
            description="Synthetic generic agent descriptor.",
            version="0.1.0",
            risk_level="medium",
            capabilities=["mail.classify", "approval.prepare"],
            allowed_tools=["connector.gmail.readonly"],
            required_connectors=["gmail"],
            supports_manual_run=True,
            supports_scheduled_run=True,
            health_status="healthy",
        )
        session.add(
            WebhookSubscription(
                external_client_id=CLIENT_ID,
                event_type="run.state_changed",
                target_url="https://client.example.test/webhooks/atlas",
                secret_reference="phase5-webhook-secret-reference",
                status="active",
            )
        )
        return agent_registration.agent_id


def _seed_approval_with_fact(
    factory: sessionmaker[Session],
    fact_id: str,
    run_id: str,
) -> str:
    with factory.begin() as session:
        approval = create_approval_request(
            session,
            owner_user_id=OWNER_ID,
            agent_id="agt_gmail_contract_fixture",
            run_id=run_id,
            action_type="draft.send",
            action_reference="draft:synthetic-closeout",
            action_payload={"draft_id": "synthetic-closeout", "body_hash": "hash"},
            evidence_summary={"subject": "Synthetic closeout approval"},
            decision_context_manifest={
                "action_identity": "draft:synthetic-closeout",
                "evidence_version": "v1",
            },
        )
        attach_facts_used_evidence(
            session,
            approval,
            owner_user_id=OWNER_ID,
            knowledge_fact_ids=[fact_id],
            bound_at=datetime(2026, 7, 18, tzinfo=UTC),
        )
        return approval.approval_id


def _signed_headers(
    *,
    method: str,
    path_query: str,
    nonce: str = "phase5-nonce",
    body: bytes = b"",
    secret: str = SECRET,
) -> dict[str, str]:
    timestamp = int(datetime.now(UTC).timestamp())
    request = SignedExternalRequest(
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
        "X-Atlas-Signature": sign_request(request, secret),
    }


def _json_body(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode()
