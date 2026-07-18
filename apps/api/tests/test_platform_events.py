from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.events import (
    PHASE5_WEBHOOK_EVENT_TYPES,
    WEBHOOK_EVENT_APPROVAL_DECIDED,
    WEBHOOK_EVENT_APPROVAL_PENDING,
    WEBHOOK_EVENT_KNOWLEDGE_FACT_RECONFIRMATION_REQUIRED,
    WEBHOOK_EVENT_KNOWLEDGE_QUESTION_ANSWERED,
    WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING,
    WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING,
    WEBHOOK_EVENT_RUN_STATE_CHANGED,
)
from atlas_api.db.base import Base
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
from atlas_api.models.external_client import ExternalProductClient
from atlas_api.models.webhook import WebhookSubscription
from atlas_api.services.audit import record_webhook_audit_event
from atlas_api.services.platform_events import (
    approval_decided_event,
    approval_pending_event,
    build_platform_webhook_event,
    enqueue_platform_webhook_event,
    knowledge_fact_reconfirmation_required_event,
    knowledge_question_answered_event,
    knowledge_question_pending_event,
    message_held_for_manual_handling_event,
    run_state_changed_event,
)
from atlas_api.services.webhook_delivery import (
    RecordingWebhookTransport,
    WebhookAuditEvent,
    WebhookDeliveryResult,
    WebhookDeliveryService,
    WebhookError,
)


def session_factory() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def webhook_settings() -> Settings:
    return Settings(
        environment="test",
        webhook_signing_key_id="current",
        webhook_signing_secret=SecretStr("webhook-secret"),
    )


def test_phase5_webhook_event_registry_covers_required_contracts() -> None:
    assert PHASE5_WEBHOOK_EVENT_TYPES == {
        WEBHOOK_EVENT_APPROVAL_PENDING,
        WEBHOOK_EVENT_APPROVAL_DECIDED,
        WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING,
        WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING,
        WEBHOOK_EVENT_KNOWLEDGE_QUESTION_ANSWERED,
        WEBHOOK_EVENT_KNOWLEDGE_FACT_RECONFIRMATION_REQUIRED,
        WEBHOOK_EVENT_RUN_STATE_CHANGED,
    }


def test_phase5_event_builders_emit_minimum_necessary_payloads() -> None:
    events = [
        approval_pending_event(approval_id="apr_1"),
        approval_decided_event(
            approval_id="apr_1",
            status="approved",
            decision_channel="external",
        ),
        message_held_for_manual_handling_event(
            manual_handling_id="mhr_1",
            status="pending",
            reason_category="clinical_source",
            sensitivity_classification="restricted",
        ),
        knowledge_question_pending_event(
            question_id="kq_1",
            fact_key="reply.preference",
        ),
        knowledge_question_answered_event(
            question_id="kq_1",
            fact_key="reply.preference",
            revision_id="kfr_1",
        ),
        knowledge_fact_reconfirmation_required_event(
            knowledge_fact_id="kf_1",
            fact_key="reply.preference",
            reason_category="volatile_stale",
        ),
        run_state_changed_event(
            run_id="run_1",
            status="queued",
            trigger_source="manual",
        ),
    ]

    blocked_fragments = ("body", "content", "message", "secret", "text", "token")
    for event in events:
        assert event.event_type in PHASE5_WEBHOOK_EVENT_TYPES
        assert event.payload["reconciliation_path"].startswith("/api/v1/")
        assert not any(
            fragment in key
            for key in event.payload
            for fragment in blocked_fragments
        )


def test_phase5_event_builder_rejects_sensitive_payload_keys() -> None:
    with pytest.raises(WebhookError, match="platform_event_payload_invalid"):
        build_platform_webhook_event(
            WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING,
            resource_id="kq_1",
            resource_type="knowledge_question",
            status="pending",
            reconciliation_path="/api/v1/knowledge/questions/kq_1",
            fact_key="reply.preference",
            message_body="The customer wrote a sensitive email.",
        )


@pytest.mark.anyio
async def test_phase5_event_enqueue_delivery_and_audit_are_minimized() -> None:
    settings = webhook_settings()
    with session_factory() as session:
        session.add(
            ExternalProductClient(
                external_client_id="client-1",
                display_name="Client",
                status="active",
                authentication_key_reference="key-ref",
            )
        )
        subscription = WebhookSubscription(
            external_client_id="client-1",
            event_type=WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING,
            target_url="https://client.example.test/webhooks/atlas",
            secret_reference="secret-ref",
            status="active",
        )
        session.add(subscription)
        session.flush()

        def audit_hook(event: WebhookAuditEvent) -> None:
            record_webhook_audit_event(session, event, correlation_id="corr-event")

        attempts = enqueue_platform_webhook_event(
            session,
            knowledge_question_pending_event(
                question_id="kq_1",
                fact_key="reply.preference",
            ),
            correlation_id="corr-event",
            now=datetime(2026, 7, 18, tzinfo=UTC),
            settings=settings,
            audit_hook=audit_hook,
        )
        transport = RecordingWebhookTransport(WebhookDeliveryResult("delivered"))
        delivered = await WebhookDeliveryService(transport, settings).deliver_due(
            session,
            now=datetime(2026, 7, 18, 0, 1, tzinfo=UTC),
            audit_hook=audit_hook,
        )
        session.commit()

        assert len(attempts) == 1
        assert delivered == 1
        assert attempts[0].event_id == transport.sent[0].event_id
        assert transport.sent[0].headers["X-Atlas-Event-Type"] == (
            WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING
        )
        body = json.loads(transport.sent[0].body)
        assert body["event_type"] == WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING
        assert body["payload"] == {
            "fact_key": "reply.preference",
            "resource_id": "kq_1",
            "resource_type": "knowledge_question",
            "status": "pending",
            "reconciliation_path": "/api/v1/knowledge/questions/kq_1",
        }
        encoded = transport.sent[0].body.decode()
        assert "customer" not in encoded
        assert "email" not in encoded
        assert "X-Atlas-Signature" in transport.sent[0].headers

        audit_events = session.scalars(select(AuditEvent)).all()
        assert [event.event_type for event in audit_events] == [
            "webhook.delivery_queued",
            "webhook.delivery_delivered",
        ]
        assert audit_events[0].metadata_json == {
            "attempt_count": 0,
            "event_id": attempts[0].event_id,
            "event_type": WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING,
            "status": "pending",
            "webhook_delivery_attempt_id": attempts[
                0
            ].webhook_delivery_attempt_id,
            "webhook_subscription_id": subscription.webhook_subscription_id,
        }


def test_phase5_event_enqueue_uses_exact_event_subscription_match() -> None:
    settings = webhook_settings()
    with session_factory() as session:
        session.add(
            ExternalProductClient(
                external_client_id="client-1",
                display_name="Client",
                status="active",
                authentication_key_reference="key-ref",
            )
        )
        session.add_all(
            [
                WebhookSubscription(
                    external_client_id="client-1",
                    event_type=WEBHOOK_EVENT_RUN_STATE_CHANGED,
                    target_url="https://client.example.test/webhooks/run",
                    secret_reference="secret-ref",
                    status="active",
                ),
                WebhookSubscription(
                    external_client_id="client-1",
                    event_type=WEBHOOK_EVENT_APPROVAL_PENDING,
                    target_url="https://client.example.test/webhooks/approval",
                    secret_reference="secret-ref",
                    status="active",
                ),
            ]
        )
        session.flush()

        attempts = enqueue_platform_webhook_event(
            session,
            run_state_changed_event(
                run_id="run_1",
                status="queued",
                trigger_source="manual",
            ),
            correlation_id="corr-run",
            now=datetime(2026, 7, 18, tzinfo=UTC),
            settings=settings,
        )
        session.commit()

        assert len(attempts) == 1
        assert attempts[0].event_type == WEBHOOK_EVENT_RUN_STATE_CHANGED
