from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
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
from atlas_api.models.approval import (
    ApprovalDecision,
    ApprovalRequest,
)
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.services.approval_contracts import (
    create_approval_request,
    create_manual_handling_record,
)

CLIENT_ID = "external-client-1"
KEY_ID = "current-key"
SECRET = "expected-signing-secret"


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


def seed_approval(
    factory: sessionmaker[Session],
    *,
    expires_at: datetime | None = None,
) -> str:
    with factory() as session:
        approval = create_approval_request(
            session,
            owner_user_id="usr_owner",
            agent_id="agt_gmail",
            run_id="run_synthetic",
            action_type="draft.send",
            action_reference="draft:synthetic-1",
            action_payload={"draft_id": "synthetic-1", "body_hash": "hash"},
            evidence_summary={"subject": "Synthetic approval", "body": "omitted"},
            decision_context_manifest={
                "action_identity": "draft:synthetic-1",
                "evidence_version": "v1",
            },
            expires_at=expires_at,
        )
        approval_id = approval.approval_id
        session.commit()
        return approval_id


def test_pending_queue_evidence_and_approve_are_audited_and_idempotent() -> None:
    factory = database_factory()
    approval_id = seed_approval(factory)
    client = TestClient(create_app(configured_settings(), factory))

    queue = client.get(
        "/api/v1/approvals",
        headers=signed_headers(
            method="GET",
            path_query="/api/v1/approvals",
            nonce="approval-list",
        ),
    )
    evidence = client.get(
        f"/api/v1/approvals/{approval_id}/evidence",
        headers=signed_headers(
            method="GET",
            path_query=f"/api/v1/approvals/{approval_id}/evidence",
            nonce="approval-evidence",
        ),
    )
    decision_payload = {
        "decision": "approve",
        "approval_revision": 1,
        "reason": "Looks good.",
    }
    body = json_body(decision_payload)
    decided = client.post(
        f"/api/v1/approvals/{approval_id}/decisions",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "approval-decision-key-1",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/approvals/{approval_id}/decisions",
                nonce="approval-decide",
                body=body,
            ),
        },
    )
    replayed = client.post(
        f"/api/v1/approvals/{approval_id}/decisions",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "approval-decision-key-1",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/approvals/{approval_id}/decisions",
                nonce="approval-decide-replay",
                body=body,
            ),
        },
    )

    assert queue.status_code == 200
    assert queue.json()["data"][0]["approval_id"] == approval_id
    assert evidence.status_code == 200
    assert "action_payload_hash" in evidence.json()["data"]
    assert decided.status_code == 200
    assert decided.json()["data"]["status"] == "approved"
    assert decided.json()["data"]["continuation_status"] == "pending"
    assert replayed.status_code == 200
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(ApprovalDecision)) == 1
        audit_actions = list(
            session.scalars(
                select(AuditEvent.action).where(AuditEvent.resource_type == "approval")
            )
        )
    assert audit_actions == ["list", "read_evidence", "decide", "decide"]


def test_decision_fails_closed_for_revision_conflict_and_expiry() -> None:
    factory = database_factory()
    approval_id = seed_approval(factory)
    expired_id = seed_approval(
        factory,
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )
    client = TestClient(create_app(configured_settings(), factory))

    conflict_body = json_body({"decision": "reject", "approval_revision": 2})
    conflict = client.post(
        f"/api/v1/approvals/{approval_id}/decisions",
        content=conflict_body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "approval-conflict-key",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/approvals/{approval_id}/decisions",
                nonce="approval-conflict",
                body=conflict_body,
            ),
        },
    )
    expired_body = json_body({"decision": "approve", "approval_revision": 1})
    expired = client.post(
        f"/api/v1/approvals/{expired_id}/decisions",
        content=expired_body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "approval-expired-key",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/approvals/{expired_id}/decisions",
                nonce="approval-expired",
                body=expired_body,
            ),
        },
    )

    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "approval_revision_conflict"
    assert expired.status_code == 409
    assert expired.json()["error"]["code"] == "approval_expired"


def test_edit_then_approve_supersedes_original_and_approves_replacement() -> None:
    factory = database_factory()
    approval_id = seed_approval(factory)
    client = TestClient(create_app(configured_settings(), factory))
    body = json_body(
        {
            "decision": "edit_approve",
            "approval_revision": 1,
            "reason": "Approved with edited content.",
            "edited_action_payload": {
                "draft_id": "synthetic-1",
                "body_hash": "edited-hash",
            },
        }
    )
    response = client.post(
        f"/api/v1/approvals/{approval_id}/decisions",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "approval-edit-key-1",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/approvals/{approval_id}/decisions",
                nonce="approval-edit",
                body=body,
            ),
        },
    )

    assert response.status_code == 200
    replacement_id = response.json()["data"]["approval_id"]
    assert replacement_id != approval_id
    assert response.json()["data"]["status"] == "approved"
    with factory() as session:
        original = session.get(ApprovalRequest, approval_id)
        replacement = session.get(ApprovalRequest, replacement_id)
        assert original.status == "superseded"
        assert original.superseded_by_approval_id == replacement_id
        assert replacement.status == "approved"


def test_manual_handling_records_are_readable_but_not_approvals() -> None:
    factory = database_factory()
    with factory() as session:
        record = create_manual_handling_record(
            session,
            owner_user_id="usr_owner",
            agent_id="agt_gmail",
            run_id="run_synthetic",
            source_reference="gmail:message:held",
            reason_category="Clinical",
            sensitivity_classification="restricted",
            metadata_json={"message_content": None},
        )
        manual_id = record.manual_handling_id
        session.commit()
    client = TestClient(create_app(configured_settings(), factory))

    listed = client.get(
        "/api/v1/manual-handling",
        headers=signed_headers(
            method="GET",
            path_query="/api/v1/manual-handling",
            nonce="manual-list",
        ),
    )
    read = client.get(
        f"/api/v1/manual-handling/{manual_id}",
        headers=signed_headers(
            method="GET",
            path_query=f"/api/v1/manual-handling/{manual_id}",
            nonce="manual-read",
        ),
    )
    not_approval = client.get(
        f"/api/v1/approvals/{manual_id}/evidence",
        headers=signed_headers(
            method="GET",
            path_query=f"/api/v1/approvals/{manual_id}/evidence",
            nonce="manual-not-approval",
        ),
    )

    assert listed.status_code == 200
    assert listed.json()["data"][0]["manual_handling_id"] == manual_id
    assert read.status_code == 200
    assert read.json()["data"]["reason_category"] == "Clinical"
    assert "message_content" not in read.text
    assert not_approval.status_code == 404


def test_approval_openapi_declares_hmac_security() -> None:
    client = TestClient(create_app(configured_settings(), database_factory()))

    schema = client.get("/openapi.json").json()

    operation = schema["paths"]["/api/v1/approvals/{approval_id}/decisions"]["post"]
    assert operation["security"] == [{"ExternalClientHmac": []}]
