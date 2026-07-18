from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.observability import JsonLogFormatter, log_event, sanitize_metadata
from atlas_api.db.base import Base
from atlas_api.models import (  # noqa: F401
    external_client,
    external_request_nonce,
    job,
    owner_session,
    schedule,
    webhook,
)
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import ExternalProductClient
from atlas_api.models.webhook import WebhookSubscription
from atlas_api.services.audit import (
    AuditEventInput,
    record_audit_event,
    record_queue_audit_event,
    record_schedule_audit_event,
    record_webhook_audit_event,
)
from atlas_api.services.queue import QueueAuditEvent, enqueue
from atlas_api.services.scheduler import ScheduleAuditEvent
from atlas_api.services.webhook_delivery import (
    RecordingWebhookTransport,
    WebhookAuditEvent,
    WebhookDeliveryResult,
    WebhookDeliveryService,
    enqueue_notification,
)


def session_factory() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_sanitizer_is_allowlist_first_and_redacts_sensitive_keys() -> None:
    sanitized = sanitize_metadata(
        {
            "job_id": "job_123",
            "key_id": "current-key",
            "signature": "should-not-appear",
            "body": "email body",
            "unknown": "discarded",
        }
    )

    assert sanitized == {"job_id": "job_123", "key_id": "current-key"}


def test_json_log_formatter_emits_required_fields_without_secret_metadata(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = logging.getLogger("atlas_api.test_observability")
    logger.propagate = True
    formatter = JsonLogFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)

    log_event(
        logger,
        component="queue",
        event_type="queue.job_enqueued",
        message="job enqueued",
        correlation_id="corr-log",
        metadata={"job_id": "job_123", "signature": "secret"},
    )

    payload = json.loads(formatter.format(caplog.records[0]))
    assert payload["timestamp"].endswith("Z")
    assert payload["severity"] == "INFO"
    assert payload["component"] == "queue"
    assert payload["event_type"] == "queue.job_enqueued"
    assert payload["correlation_id"] == "corr-log"
    assert payload["job_id"] == "job_123"
    assert "signature" not in payload


def test_record_audit_event_persists_canonical_shape_and_sanitized_metadata() -> None:
    with session_factory() as session:
        audit_event = record_audit_event(
            session,
            AuditEventInput(
                event_type="authorization.decision",
                actor_type="external_client",
                actor_id="client-1",
                channel="external_product_client",
                action="probe",
                resource_type="external_client_authentication",
                resource_id="client-1",
                result="denied",
                reason_code="authorization_denied",
                correlation_id="corr-audit",
                metadata={"outcome": "authorization_denied", "body": "discarded"},
            ),
        )
        session.commit()

        stored = session.get(AuditEvent, audit_event.audit_event_id)
        assert stored is not None
        assert stored.channel == "external_product_client"
        assert stored.action == "probe"
        assert stored.result == "denied"
        assert stored.reason_code == "authorization_denied"
        assert stored.metadata_json == {"outcome": "authorization_denied"}


def test_queue_audit_hook_rolls_back_with_material_change() -> None:
    with session_factory() as session:

        def failing_audit(_: QueueAuditEvent) -> None:
            raise RuntimeError("audit unavailable")

        with pytest.raises(RuntimeError, match="audit unavailable"):
            enqueue(
                session,
                job_type="platform.maintenance",
                payload_metadata={},
                now=datetime(2026, 7, 18, tzinfo=UTC),
                audit_hook=failing_audit,
            )
        session.rollback()

        assert session.scalar(select(AuditEvent)) is None


def test_queue_schedule_and_webhook_audit_adapters_write_durable_rows() -> None:
    with session_factory() as session:
        record_queue_audit_event(
            session,
            QueueAuditEvent(
                event_type="queue.job_enqueued",
                job_id="job_123",
                metadata={"job_type": "platform.maintenance", "state": "queued"},
            ),
            correlation_id="corr-queue",
        )
        record_schedule_audit_event(
            session,
            ScheduleAuditEvent(
                event_type="scheduler.schedule_triggered",
                schedule_id="sch_123",
                metadata={"queue_job_id": "job_123"},
            ),
            correlation_id="corr-schedule",
        )
        record_webhook_audit_event(
            session,
            event=WebhookAuditEvent(
                event_type="webhook.delivery_delivered",
                delivery_attempt_id="whdel_123",
                metadata={"event_id": "whe_123", "status": "delivered"},
            ),
            correlation_id="corr-webhook",
        )
        session.commit()

        events = session.scalars(
            select(AuditEvent).order_by(AuditEvent.event_type)
        ).all()
        assert [event.resource_type for event in events] == [
            "queue_job",
            "job_schedule",
            "webhook_delivery_attempt",
        ]


@pytest.mark.anyio
async def test_webhook_delivery_audit_hook_records_same_transaction_events() -> None:
    settings = Settings(
        environment="test",
        webhook_signing_key_id="current",
        webhook_signing_secret=SecretStr("webhook-secret"),
    )
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
            event_type="approval.pending",
            target_url="https://client.example.test/webhooks/atlas",
            secret_reference="secret-ref",
            status="active",
        )
        session.add(subscription)
        session.flush()

        def audit_hook(event: WebhookAuditEvent) -> None:
            record_webhook_audit_event(session, event, correlation_id="corr-webhook")

        attempt = enqueue_notification(
            session,
            subscription_id=subscription.webhook_subscription_id,
            event_type="approval.pending",
            payload={"resource_id": "approval-1"},
            correlation_id="corr-webhook",
            now=datetime(2026, 7, 18, tzinfo=UTC),
            settings=settings,
            audit_hook=audit_hook,
        )
        delivered = await WebhookDeliveryService(
            RecordingWebhookTransport(WebhookDeliveryResult("delivered")),
            settings,
        ).deliver_due(
            session,
            now=datetime(2026, 7, 18, 0, 1, tzinfo=UTC),
            audit_hook=audit_hook,
        )
        session.commit()

        assert delivered == 1
        assert attempt.status == "delivered"
        assert len(session.scalars(select(AuditEvent)).all()) == 2
