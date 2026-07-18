from __future__ import annotations

import pytest
from sqlalchemy import create_engine

from atlas_api.db.base import Base
from atlas_api.models import (  # noqa: F401
    approval,
    audit,
    external_client,
    knowledge,
    webhook,
)
from atlas_api.services.webhook_delivery import (
    RecordingWebhookTransport,
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
    assert "last_confirmed_at" in facts.c
    assert "knowledge_fact_id" in revisions.c
    assert "knowledge_question_id" in answers.c
    assert "approval_id" not in answers.c
    assert "approval_requests" in table_names
    assert "manual_handling_records" in table_names


def test_foundation_schema_can_create_in_narrow_sqlite_unit_test() -> None:
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    assert "users" in Base.metadata.tables
    assert "webhook_delivery_attempts" in Base.metadata.tables


@pytest.mark.anyio
async def test_webhook_delivery_uses_fake_transport_without_network() -> None:
    transport = RecordingWebhookTransport()
    notification = WebhookNotification(
        event_id="whe_123",
        event_type="knowledge.question.pending",
        target_url="https://client.example.test/webhooks/atlas",
        body=b'{"version":1}',
        headers={"X-Atlas-Event-Id": "whe_123"},
    )

    result = await transport.send(notification, timeout_seconds=5)

    assert result.status == "delivered"
    assert transport.sent == [notification]
