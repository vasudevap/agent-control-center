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
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.idempotency import ApiIdempotencyRecord
from atlas_api.models.knowledge import KnowledgeFact, KnowledgeFactRevision

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


def create_fact(
    client: TestClient,
    payload: dict[str, Any] | None = None,
    *,
    nonce: str = "create-fact",
    idempotency_key: str = "knowledge-create-key-1",
) -> dict[str, Any]:
    body_payload = payload or {
        "fact_key": "contact.preference",
        "display_value": "Use concise replies for scheduling requests.",
        "classification": "internal",
        "source_type": "human",
        "source_reference": "manual-entry",
        "provenance_summary": "Owner provided this preference directly.",
        "is_volatile": False,
        "confirmed": True,
    }
    body = json_body(body_payload)
    response = client.post(
        "/api/v1/knowledge/facts",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
            **signed_headers(
                method="POST",
                path_query="/api/v1/knowledge/facts",
                nonce=nonce,
                body=body,
            ),
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_knowledge_fact_create_is_idempotent_revisioned_and_audited() -> None:
    factory = database_factory()
    client = TestClient(create_app(configured_settings(), factory))

    created = create_fact(client)
    replayed = create_fact(client, nonce="create-fact-replay")

    assert replayed["knowledge_fact_id"] == created["knowledge_fact_id"]
    assert created["current_revision"]["revision_number"] == 1
    assert created["last_confirmed_at"] is not None
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(KnowledgeFact)) == 1
        revision_count = session.scalar(
            select(func.count()).select_from(KnowledgeFactRevision)
        )
        assert revision_count == 1
        assert session.scalar(select(ApiIdempotencyRecord)).resource_id == (
            created["knowledge_fact_id"]
        )
        audit_actions = list(
            session.scalars(
                select(AuditEvent.action).where(
                    AuditEvent.resource_type == "knowledge_fact"
                )
            )
        )
    assert audit_actions == ["create", "create"]


def test_knowledge_fact_update_confirm_and_delete_preserve_revision_history() -> None:
    factory = database_factory()
    client = TestClient(create_app(configured_settings(), factory))
    created = create_fact(client)
    fact_id = created["knowledge_fact_id"]
    update_payload = {
        "display_value": "Use concise replies and include two time options.",
        "source_type": "human",
        "source_reference": "manual-update",
        "provenance_summary": "Owner refined the scheduling preference.",
        "is_volatile": True,
        "confirmed": False,
    }
    update_body = json_body(update_payload)

    updated = client.patch(
        f"/api/v1/knowledge/facts/{fact_id}",
        content=update_body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "knowledge-update-key-1",
            **signed_headers(
                method="PATCH",
                path_query=f"/api/v1/knowledge/facts/{fact_id}",
                nonce="update-fact",
                body=update_body,
            ),
        },
    )
    confirmed = client.post(
        f"/api/v1/knowledge/facts/{fact_id}/confirm",
        headers={
            "Idempotency-Key": "knowledge-confirm-key-1",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/knowledge/facts/{fact_id}/confirm",
                nonce="confirm-fact",
            ),
        },
    )
    deleted = client.delete(
        f"/api/v1/knowledge/facts/{fact_id}",
        headers={
            "Idempotency-Key": "knowledge-delete-key-1",
            **signed_headers(
                method="DELETE",
                path_query=f"/api/v1/knowledge/facts/{fact_id}",
                nonce="delete-fact",
            ),
        },
    )

    assert updated.status_code == 200
    assert updated.json()["data"]["current_revision"]["revision_number"] == 2
    assert confirmed.status_code == 200
    assert confirmed.json()["data"]["current_revision"]["revision_number"] == 3
    assert deleted.status_code == 200
    assert deleted.json()["data"]["status"] == "deleted"
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(KnowledgeFact)) == 1
        revision_count = session.scalar(
            select(func.count()).select_from(KnowledgeFactRevision)
        )
        assert revision_count == 3


def test_stale_volatile_fact_listing_and_prohibited_content_rejection() -> None:
    factory = database_factory()
    client = TestClient(create_app(configured_settings(), factory))
    created = create_fact(
        client,
        payload={
            "fact_key": "travel.window",
            "display_value": "Avoid morning flights.",
            "classification": "internal",
            "source_type": "human",
            "source_reference": "manual-entry",
            "provenance_summary": "Owner provided a travel preference.",
            "is_volatile": True,
            "confirmed": False,
        },
        idempotency_key="knowledge-create-stale-key-1",
    )
    path_query = "/api/v1/knowledge/facts?stale_volatile_only=true"
    stale = client.get(
        path_query,
        headers=signed_headers(
            method="GET",
            path_query=path_query,
            nonce="list-stale",
        ),
    )
    unsafe_payload = {
        "fact_key": "unsafe.fact",
        "display_value": "Clinical diagnosis says protected health detail.",
        "classification": "internal",
        "source_type": "human",
        "source_reference": "manual-entry",
        "provenance_summary": "Owner entered the synthetic clinical sample.",
        "is_volatile": False,
        "confirmed": False,
    }
    unsafe_body = json_body(unsafe_payload)
    unsafe = client.post(
        "/api/v1/knowledge/facts",
        content=unsafe_body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "knowledge-unsafe-key-1",
            **signed_headers(
                method="POST",
                path_query="/api/v1/knowledge/facts",
                nonce="unsafe-fact",
                body=unsafe_body,
            ),
        },
    )

    assert stale.status_code == 200
    assert stale.json()["data"][0]["knowledge_fact_id"] == created["knowledge_fact_id"]
    assert unsafe.status_code == 422
    assert unsafe.json()["error"]["code"] == "knowledge_fact_prohibited_content"
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(KnowledgeFact)) == 1


def test_knowledge_fact_contract_requires_auth_owner_and_idempotency() -> None:
    factory = database_factory()
    client = TestClient(create_app(configured_settings(), factory))
    body = json_body(
        {
            "fact_key": "contact.preference",
            "display_value": "Use short replies.",
            "classification": "internal",
            "source_type": "human",
            "source_reference": "manual-entry",
            "provenance_summary": "Owner provided this preference.",
            "is_volatile": False,
            "confirmed": False,
        }
    )

    missing_auth = client.get("/api/v1/knowledge/facts")
    missing_idempotency = client.post(
        "/api/v1/knowledge/facts",
        content=body,
        headers={
            "Content-Type": "application/json",
            **signed_headers(
                method="POST",
                path_query="/api/v1/knowledge/facts",
                nonce="missing-idempotency",
                body=body,
            ),
        },
    )
    with factory() as session:
        session.get(ExternalProductClient, CLIENT_ID).human_owner_user_id = None
        session.commit()
    unlinked = client.get(
        "/api/v1/knowledge/facts",
        headers=signed_headers(
            method="GET",
            path_query="/api/v1/knowledge/facts",
            nonce="unlinked-owner",
        ),
    )

    assert missing_auth.status_code == 401
    assert missing_idempotency.status_code == 422
    assert unlinked.status_code == 403
    assert unlinked.json()["error"]["code"] == "knowledge_owner_unavailable"


def test_knowledge_fact_openapi_declares_hmac_security() -> None:
    client = TestClient(create_app(configured_settings(), database_factory()))

    schema = client.get("/openapi.json").json()

    operation = schema["paths"]["/api/v1/knowledge/facts"]["post"]
    assert operation["security"] == [{"ExternalClientHmac": []}]
