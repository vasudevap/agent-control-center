from __future__ import annotations

import pytest
from sqlalchemy import create_engine

from atlas_api.db.base import Base
from atlas_api.models import audit, external_client, knowledge, webhook  # noqa: F401
from atlas_api.services.webhook_delivery import (
    RecordingWebhookTransport,
    WebhookDeliveryService,
    WebhookNotification,
)


def test_foundation_metadata_keeps_knowledge_records_distinct() -> None:
    table_names = set(Base.metadata.tables)

    assert {
        "knowledge_facts",
        "knowledge_fact_revisions",
        "knowledge_questions",
        "knowledge_answers",
    }.issubset(table_names)

    facts = Base.metadata.tables["knowledge_facts"]
    revisions = Base.metadata.tables["knowledge_fact_revisions"]
    answers = Base.metadata.tables["knowledge_answers"]

    assert "current_revision_id" in facts.c
    assert "knowledge_fact_id" in revisions.c
    assert "knowledge_question_id" in answers.c
    assert "approval_id" not in answers.c


def test_foundation_schema_can_create_on_local_sqlite_substitute() -> None:
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    assert "users" in Base.metadata.tables
    assert "webhook_delivery_attempts" in Base.metadata.tables


@pytest.mark.anyio
async def test_webhook_delivery_uses_fake_transport_without_network() -> None:
    transport = RecordingWebhookTransport()
    service = WebhookDeliveryService(transport)
    notification = WebhookNotification(
        event_type="knowledge.question.pending",
        target_url="https://client.example.test/webhooks/atlas",
        payload_summary={"knowledge_question_id": "kq_123"},
        correlation_id="corr-webhook",
    )

    result = await service.deliver(notification)

    assert result.status == "delivered"
    assert result.attempt_count == 1
    assert transport.sent == [notification]
