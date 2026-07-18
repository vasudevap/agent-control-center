from __future__ import annotations

import io
import json
import logging
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.external_request_signing import SignedExternalRequest, sign_request
from atlas_api.core.observability import JsonLogFormatter, log_event
from atlas_api.core.owner_sessions import (
    VerifiedIdentity,
    issue_owner_session,
    validate_owner_session,
    verify_owner_identity,
)
from atlas_api.db.base import Base
from atlas_api.main import create_app
from atlas_api.models import (  # noqa: F401
    external_client,
    external_request_nonce,
    job,
    knowledge,
    owner_session,
    schedule,
    webhook,
)
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.webhook import WebhookSubscription
from atlas_api.services.audit import (
    record_queue_audit_event,
    record_schedule_audit_event,
    record_webhook_audit_event,
)
from atlas_api.services.queue import QueueAuditEvent, claim, enqueue, succeed
from atlas_api.services.scheduler import (
    ScheduleAuditEvent,
    create_schedule,
    sweep_due_schedules,
)
from atlas_api.services.webhook_delivery import (
    RecordingWebhookTransport,
    WebhookAuditEvent,
    WebhookDeliveryResult,
    WebhookDeliveryService,
    enqueue_notification,
)

CLIENT_ID = "phase3-client"
KEY_ID = "phase3-key"
SECRET = "phase3-secret"
WEBHOOK_KEY_ID = "phase3-webhook-key"
WEBHOOK_SECRET = "phase3-webhook-secret"
OWNER_SUBJECT = "owner-subject"


@pytest.mark.anyio
async def test_phase3_foundation_smoke_path_is_coherent_and_audited() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    settings = Settings(
        environment="test",
        owner_identity_subject=OWNER_SUBJECT,
        external_client_id=CLIENT_ID,
        external_client_key_id=KEY_ID,
        external_client_secret=SecretStr(SECRET),
        webhook_signing_key_id=WEBHOOK_KEY_ID,
        webhook_signing_secret=SecretStr(WEBHOOK_SECRET),
    )
    _seed_foundation_records(factory)
    client = TestClient(create_app(settings, factory))
    correlation_id = "corr-phase3-closeout"
    now = datetime(2026, 7, 18, tzinfo=UTC)

    live = client.get("/health/live", headers={"X-Correlation-Id": correlation_id})
    ready = client.get("/health/ready")
    assert live.status_code == 200
    assert live.headers["X-Correlation-Id"] == correlation_id
    assert ready.json()["problems"] == []

    verify_owner_identity(
        VerifiedIdentity(provider="test", subject=OWNER_SUBJECT),
        settings,
    )
    with factory() as session:
        owner = session.scalar(select(User))
        assert owner is not None
        issued = issue_owner_session(
            session,
            user_id=owner.user_id,
            settings=settings,
            now=now,
        )
        session.commit()
        principal = validate_owner_session(
            session,
            session_token=issued.session_token,
            csrf_token=issued.csrf_token,
            require_csrf=True,
            now=now + timedelta(seconds=1),
        )
        assert principal.user_id == owner.user_id

    signed = client.get(
        "/api/v1/external-client/authentication/probe",
        headers={"X-Correlation-Id": correlation_id, **_signed_headers()},
    )
    rejected = client.get(
        "/api/v1/external-client/authentication/probe",
        headers={"X-Correlation-Id": correlation_id, **_signed_headers(secret="wrong")},
    )
    assert signed.status_code == 200
    assert rejected.status_code == 401

    with factory() as session:

        def queue_audit(event: QueueAuditEvent) -> None:
            record_queue_audit_event(session, event, correlation_id=correlation_id)

        job_record = enqueue(
            session,
            job_type="platform.closeout",
            payload_metadata={"resource": "phase3"},
            resource_reference="phase3-closeout",
            idempotency_key="phase3-closeout-job",
            now=now,
            audit_hook=queue_audit,
        )
        lease = claim(
            session,
            owner_id="phase3-worker",
            now=now,
            audit_hook=queue_audit,
        )
        assert lease is not None
        succeed(
            session,
            job_id=job_record.queue_job_id,
            lease_token=lease.lease_token,
            now=now,
            audit_hook=queue_audit,
        )

        schedule_record = create_schedule(
            session,
            job_type="platform.closeout.scheduled",
            payload_metadata={"resource": "phase3"},
            interval_seconds=60,
            next_due_at=now,
        )

        def schedule_audit(event: ScheduleAuditEvent) -> None:
            record_schedule_audit_event(session, event, correlation_id=correlation_id)

        assert (
            sweep_due_schedules(session, now=now, audit_hook=schedule_audit) == 1
        )
        assert schedule_record.next_due_at == now + timedelta(seconds=60)

        def webhook_audit(event: WebhookAuditEvent) -> None:
            record_webhook_audit_event(session, event, correlation_id=correlation_id)

        subscription = session.scalar(select(WebhookSubscription))
        assert subscription is not None
        attempt = enqueue_notification(
            session,
            subscription_id=subscription.webhook_subscription_id,
            event_type="approval.pending",
            payload={
                "resource_id": "approval-phase3",
                "status": "pending",
                "reconciliation_url": "/api/v1/approvals/approval-phase3",
            },
            correlation_id=correlation_id,
            now=now,
            settings=settings,
            audit_hook=webhook_audit,
        )
        transport = RecordingWebhookTransport(WebhookDeliveryResult("delivered"))
        delivered = await WebhookDeliveryService(transport, settings).deliver_due(
            session,
            now=now + timedelta(seconds=1),
            audit_hook=webhook_audit,
        )
        session.commit()

        assert delivered == 1
        assert attempt.status == "delivered"
        assert transport.sent[0].headers["X-Atlas-Key-Id"] == WEBHOOK_KEY_ID
        assert "X-Atlas-Signature" in transport.sent[0].headers

        audit_events = session.scalars(select(AuditEvent)).all()
        event_types = {event.event_type for event in audit_events}
        assert {
            "external_client_authorization",
            "queue.job_enqueued",
            "queue.job_claimed",
            "queue.job_succeeded",
            "scheduler.schedule_triggered",
            "webhook.delivery_queued",
            "webhook.delivery_delivered",
        }.issubset(event_types)
        assert all(event.correlation_id == correlation_id for event in audit_events)
        assert all(event.redaction_state == "metadata_only" for event in audit_events)

    log_payload = _structured_log_payload(correlation_id)
    assert log_payload["correlation_id"] == correlation_id
    assert log_payload["event_type"] == "phase3.closeout_smoke_completed"
    assert "signature" not in log_payload
    assert SECRET not in json.dumps(log_payload)
    assert WEBHOOK_SECRET not in json.dumps(log_payload)


def _seed_foundation_records(factory: sessionmaker[Session]) -> None:
    with factory.begin() as session:
        owner = User(
            email="owner@example.test",
            display_name="Owner",
            identity_provider="test",
            identity_subject=OWNER_SUBJECT,
            status="active",
        )
        session.add(owner)
        session.flush()
        session.add(
            ExternalProductClient(
                external_client_id=CLIENT_ID,
                display_name="Phase 3 Client",
                status="active",
                authentication_key_reference="phase3-key-reference",
                human_owner_user_id=owner.user_id,
            )
        )
        session.add(
            WebhookSubscription(
                external_client_id=CLIENT_ID,
                event_type="approval.pending",
                target_url="https://client.example.test/webhooks/atlas",
                secret_reference="phase3-webhook-secret-reference",
                status="active",
            )
        )


def _signed_headers(
    *, nonce: str = "phase3-nonce", secret: str = SECRET
) -> dict[str, str]:
    timestamp = int(datetime.now(UTC).timestamp())
    request = SignedExternalRequest(
        client_id=CLIENT_ID,
        key_id=KEY_ID,
        timestamp=timestamp,
        nonce=nonce,
        signature="",
        method="GET",
        path_query="/api/v1/external-client/authentication/probe",
        body=b"",
    )
    return {
        "X-Atlas-Client-Id": CLIENT_ID,
        "X-Atlas-Key-Id": KEY_ID,
        "X-Atlas-Timestamp": str(timestamp),
        "X-Atlas-Nonce": nonce,
        "X-Atlas-Signature": sign_request(request, secret),
    }


def _structured_log_payload(correlation_id: str) -> dict[str, object]:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonLogFormatter())
    logger = logging.getLogger("atlas_api.phase3_closeout")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)
    log_event(
        logger,
        component="phase3_closeout",
        event_type="phase3.closeout_smoke_completed",
        message="Phase 3 closeout smoke path completed.",
        correlation_id=correlation_id,
        metadata={
            "status": "succeeded",
            "signature": "must-not-appear",
            "key_id": WEBHOOK_KEY_ID,
        },
    )
    return json.loads(stream.getvalue())
