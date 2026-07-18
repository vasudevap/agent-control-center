from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.external_request_signing import SignedExternalRequest, sign_request
from atlas_api.db.base import Base
from atlas_api.main import create_app
from atlas_api.models.approval import ApprovalRequest
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.knowledge import KnowledgeFactRevision
from atlas_api.services.approval_contracts import create_approval_request
from atlas_api.services.approval_facts import attach_facts_used_evidence
from atlas_api.services.knowledge_facts import (
    create_fact,
    soft_delete_fact,
    update_fact,
)

CLIENT_ID = "external-client-1"
KEY_ID = "current-key"
SECRET = "expected-signing-secret"
OWNER_ID = "usr_owner"


def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    with factory() as session:
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
            display_name="External Client",
            status="active",
            authentication_key_reference="keyref",
            human_owner_user_id=owner.user_id,
        )
        session.add_all([owner, client])
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


def seed_approval_with_fact(
    factory: sessionmaker[Session],
    *,
    volatile: bool = False,
) -> tuple[str, str, str]:
    with factory() as session:
        fact, revision = create_fact(
            session,
            owner_user_id=OWNER_ID,
            fact_key="reply.preference",
            display_value="Use concise replies for scheduling requests.",
            classification="internal",
            source_type="human",
            source_reference="manual-entry",
            provenance_summary="Owner provided this preference directly.",
            is_volatile=volatile,
            confirmed=True,
        )
        approval = create_approval_request(
            session,
            owner_user_id=OWNER_ID,
            agent_id="agt_gmail",
            run_id="run_synthetic",
            action_type="draft.send",
            action_reference="draft:synthetic-1",
            action_payload={"draft_id": "synthetic-1", "body_hash": "hash"},
            evidence_summary={"subject": "Synthetic approval"},
            decision_context_manifest={
                "action_identity": "draft:synthetic-1",
                "evidence_version": "v1",
            },
        )
        attach_facts_used_evidence(
            session,
            approval,
            owner_user_id=OWNER_ID,
            knowledge_fact_ids=[fact.knowledge_fact_id],
            bound_at=datetime(2026, 7, 18, tzinfo=UTC),
        )
        approval_id = approval.approval_id
        fact_id = fact.knowledge_fact_id
        revision_id = revision.knowledge_fact_revision_id
        session.commit()
        return approval_id, fact_id, revision_id


def approve_bound_approval(client: TestClient, approval_id: str) -> None:
    body = json_body(
        {
            "decision": "approve",
            "approval_revision": 2,
            "reason": "Validated bound evidence.",
        }
    )
    response = client.post(
        f"/api/v1/approvals/{approval_id}/decisions",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": f"{approval_id}-decision",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/approvals/{approval_id}/decisions",
                nonce=f"{approval_id}-decision",
                body=body,
            ),
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["continuation_status"] == "pending"


def revalidate(client: TestClient, approval_id: str, nonce: str) -> dict[str, Any]:
    response = client.post(
        f"/api/v1/approvals/{approval_id}/facts-used/revalidate",
        headers=signed_headers(
            method="POST",
            path_query=f"/api/v1/approvals/{approval_id}/facts-used/revalidate",
            nonce=nonce,
        ),
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_approval_evidence_contains_typed_facts_used_without_fact_values() -> None:
    factory = database_factory()
    approval_id, _fact_id, revision_id = seed_approval_with_fact(factory)
    client = TestClient(create_app(configured_settings(), factory))

    response = client.get(
        f"/api/v1/approvals/{approval_id}/evidence",
        headers=signed_headers(
            method="GET",
            path_query=f"/api/v1/approvals/{approval_id}/evidence",
            nonce="approval-facts-evidence",
        ),
    )

    assert response.status_code == 200
    data = response.json()["data"]
    fact_used = data["evidence_summary"]["facts_used"][0]
    binding = data["decision_context_manifest"]["fact_revision_bindings"][0]
    assert fact_used["type"] == "knowledge_fact_revision"
    assert fact_used["knowledge_fact_revision_id"] == revision_id
    assert binding["knowledge_fact_revision_id"] == revision_id
    assert "display_value" not in fact_used
    assert "answer_text" not in response.text


def test_revalidation_passes_for_unchanged_bound_fact_and_is_audited() -> None:
    factory = database_factory()
    approval_id, _fact_id, _revision_id = seed_approval_with_fact(factory)
    client = TestClient(create_app(configured_settings(), factory))
    approve_bound_approval(client, approval_id)

    data = revalidate(client, approval_id, nonce="revalidate-pass")

    assert data["status"] == "passed"
    assert data["continuation_status"] == "ready"
    assert data["failure_reason_code"] is None
    assert data["facts_checked"] == 1
    with factory() as session:
        approval = session.get(ApprovalRequest, approval_id)
        assert approval.continuation_status == "ready"
        audit = session.scalar(
            select(AuditEvent).where(AuditEvent.action == "revalidate_facts")
        )
        assert audit is not None
        assert audit.result == "succeeded"
        assert audit.metadata_json["facts_checked"] == 1


def test_revalidation_fails_closed_when_fact_revision_changes() -> None:
    factory = database_factory()
    approval_id, fact_id, _revision_id = seed_approval_with_fact(factory)
    client = TestClient(create_app(configured_settings(), factory))
    approve_bound_approval(client, approval_id)
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

    data = revalidate(client, approval_id, nonce="revalidate-changed")

    assert data["status"] == "failed"
    assert data["continuation_status"] == "blocked"
    assert data["failure_reason_code"] == "fact_revision_changed"


def test_revalidation_fails_closed_when_fact_is_deleted() -> None:
    factory = database_factory()
    approval_id, fact_id, _revision_id = seed_approval_with_fact(factory)
    client = TestClient(create_app(configured_settings(), factory))
    approve_bound_approval(client, approval_id)
    with factory() as session:
        soft_delete_fact(session, owner_user_id=OWNER_ID, knowledge_fact_id=fact_id)
        session.commit()

    data = revalidate(client, approval_id, nonce="revalidate-deleted")

    assert data["status"] == "failed"
    assert data["failure_reason_code"] == "fact_deleted"


def test_revalidation_fails_closed_when_volatile_fact_is_stale() -> None:
    factory = database_factory()
    approval_id, _fact_id, revision_id = seed_approval_with_fact(
        factory,
        volatile=True,
    )
    client = TestClient(create_app(configured_settings(), factory))
    approve_bound_approval(client, approval_id)
    with factory() as session:
        revision = session.get(KnowledgeFactRevision, revision_id)
        assert revision is not None
        revision.confirmed_at = datetime(2026, 1, 1, tzinfo=UTC)
        session.commit()

    data = revalidate(client, approval_id, nonce="revalidate-stale")

    assert data["status"] == "failed"
    assert data["failure_reason_code"] == "fact_stale_volatile"


def test_revalidation_fails_closed_when_bound_revision_becomes_prohibited() -> None:
    factory = database_factory()
    approval_id, _fact_id, revision_id = seed_approval_with_fact(factory)
    client = TestClient(create_app(configured_settings(), factory))
    approve_bound_approval(client, approval_id)
    with factory() as session:
        revision = session.get(KnowledgeFactRevision, revision_id)
        assert revision is not None
        revision.prohibited_content_reason = "clinical_source"
        session.commit()

    data = revalidate(client, approval_id, nonce="revalidate-prohibited")

    assert data["status"] == "failed"
    assert data["failure_reason_code"] == "fact_prohibited_content"


def test_revalidation_openapi_declares_hmac_security() -> None:
    client = TestClient(create_app(configured_settings(), database_factory()))

    schema = client.get("/openapi.json").json()

    operation = schema["paths"][
        "/api/v1/approvals/{approval_id}/facts-used/revalidate"
    ]["post"]
    assert operation["security"] == [{"ExternalClientHmac": []}]
