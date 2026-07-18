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
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.knowledge import (
    KnowledgeAnswer,
    KnowledgeFact,
    KnowledgeFactRevision,
    KnowledgeQuestion,
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


def create_question(
    client: TestClient,
    *,
    nonce: str = "question-create",
    idempotency_key: str = "question-create-key-1",
    fact_key: str = "contact.preference",
) -> dict[str, Any]:
    body = json_body(
        {
            "required_fact_key": fact_key,
            "question_text": "What reply style should be used?",
            "source_reference": "synthetic-question",
        }
    )
    response = client.post(
        "/api/v1/knowledge/questions",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
            **signed_headers(
                method="POST",
                path_query="/api/v1/knowledge/questions",
                nonce=nonce,
                body=body,
            ),
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_question_create_list_read_and_cancel_are_governed() -> None:
    factory = database_factory()
    client = TestClient(create_app(configured_settings(), factory))
    created = create_question(client)
    replayed = create_question(client, nonce="question-create-replay")
    question_id = created["knowledge_question_id"]

    listed = client.get(
        "/api/v1/knowledge/questions",
        headers=signed_headers(
            method="GET",
            path_query="/api/v1/knowledge/questions",
            nonce="question-list",
        ),
    )
    read = client.get(
        f"/api/v1/knowledge/questions/{question_id}",
        headers=signed_headers(
            method="GET",
            path_query=f"/api/v1/knowledge/questions/{question_id}",
            nonce="question-read",
        ),
    )
    cancelled = client.post(
        f"/api/v1/knowledge/questions/{question_id}/cancel",
        headers={
            "Idempotency-Key": "question-cancel-key-1",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/knowledge/questions/{question_id}/cancel",
                nonce="question-cancel",
            ),
        },
    )

    assert replayed["knowledge_question_id"] == question_id
    assert listed.status_code == 200
    assert listed.json()["data"][0]["knowledge_question_id"] == question_id
    assert read.status_code == 200
    assert cancelled.status_code == 200
    assert cancelled.json()["data"]["status"] == "cancelled"
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(KnowledgeQuestion)) == 1


def test_answer_creates_governed_fact_and_duplicate_answer_is_idempotent() -> None:
    factory = database_factory()
    client = TestClient(create_app(configured_settings(), factory))
    question = create_question(client, fact_key="reply.style")
    question_id = question["knowledge_question_id"]
    body = json_body(
        {
            "answer_text": "Use concise replies with two concrete options.",
            "source_reference": "synthetic-answer",
        }
    )

    answered = client.post(
        f"/api/v1/knowledge/questions/{question_id}/answers",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "question-answer-key-1",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/knowledge/questions/{question_id}/answers",
                nonce="question-answer",
                body=body,
            ),
        },
    )
    replayed = client.post(
        f"/api/v1/knowledge/questions/{question_id}/answers",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "question-answer-key-1",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/knowledge/questions/{question_id}/answers",
                nonce="question-answer-replay",
                body=body,
            ),
        },
    )

    assert answered.status_code == 201
    assert replayed.status_code == 201
    assert replayed.json()["data"]["knowledge_answer_id"] == (
        answered.json()["data"]["knowledge_answer_id"]
    )
    with factory() as session:
        question_record = session.get(KnowledgeQuestion, question_id)
        assert question_record.status == "answered"
        assert session.scalar(select(func.count()).select_from(KnowledgeAnswer)) == 1
        assert session.scalar(select(func.count()).select_from(KnowledgeFact)) == 1
        revision_count = session.scalar(
            select(func.count()).select_from(KnowledgeFactRevision)
        )
        assert revision_count == 1


def test_prohibited_answer_values_are_rejected_before_persistence() -> None:
    factory = database_factory()
    client = TestClient(create_app(configured_settings(), factory))
    question = create_question(client, fact_key="unsafe.fact")
    question_id = question["knowledge_question_id"]
    body = json_body(
        {
            "answer_text": "Clinical diagnosis includes protected health detail.",
            "source_reference": "synthetic-answer",
        }
    )
    response = client.post(
        f"/api/v1/knowledge/questions/{question_id}/answers",
        content=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": "question-unsafe-answer-key-1",
            **signed_headers(
                method="POST",
                path_query=f"/api/v1/knowledge/questions/{question_id}/answers",
                nonce="question-unsafe-answer",
                body=body,
            ),
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "knowledge_fact_prohibited_content"
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(KnowledgeAnswer)) == 0
        assert session.scalar(select(func.count()).select_from(KnowledgeFact)) == 0


def test_question_openapi_declares_hmac_security() -> None:
    client = TestClient(create_app(configured_settings(), database_factory()))

    schema = client.get("/openapi.json").json()

    operation = schema["paths"]["/api/v1/knowledge/questions"]["post"]
    assert operation["security"] == [{"ExternalClientHmac": []}]
