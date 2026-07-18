from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.db.base import Base
from atlas_api.models.approval import ApprovalRequest
from atlas_api.models.audit import AuditEvent
from atlas_api.models.connector import (
    ConnectorConnection,
    ConnectorCredentialReference,
)
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.gmail_message import (
    GmailDraftRecord,
    GmailMessageRecord,
    GmailSendOutcomeRecord,
)
from atlas_api.models.job import QueueJob
from atlas_api.models.run import AgentRunStep
from atlas_api.models.webhook import WebhookDeliveryAttempt, WebhookSubscription
from atlas_api.services.connectors import (
    DRIVE_SCOPE_FILE,
    GMAIL_SCOPE_MODIFY,
    ensure_default_connector_types,
)
from atlas_api.services.gmail_messages import (
    FakeGmailMessage,
    FakeGmailProvider,
    GmailRetrievalPolicy,
)
from atlas_api.services.gmail_operational import (
    WEBHOOK_EVENT_SEND_OUTCOME,
    GmailOperationalWebhookContext,
    create_gmail_manual_run,
    create_gmail_scheduled_run,
    enqueue_gmail_approval_pending_event,
    enqueue_gmail_send_outcome_event,
    ensure_gmail_agent_registered,
    execute_gmail_reconciliation_run,
)
from atlas_api.services.runs import record_run_step

OWNER_ID = "usr_owner"
CLIENT_ID = "external-client-1"


def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


def webhook_settings() -> Settings:
    return Settings(
        environment="test",
        webhook_signing_key_id="current",
        webhook_signing_secret=SecretStr("webhook-secret"),
    )


def seed_owner_client_and_connections(session: Session) -> tuple[str, str]:
    session.add(
        User(
            user_id=OWNER_ID,
            email="owner@example.test",
            display_name="Owner",
            identity_provider="test",
            identity_subject="owner-subject",
            status="active",
        )
    )
    session.add(
        ExternalProductClient(
            external_client_id=CLIENT_ID,
            display_name="External Client",
            status="active",
            authentication_key_reference="key-ref",
            human_owner_user_id=OWNER_ID,
        )
    )
    ensure_default_connector_types(session)
    gmail_credential = ConnectorCredentialReference(
        owner_user_id=OWNER_ID,
        connector_type="gmail",
        reference_label="gmail:oauth:ref",
        key_version="local-fake-v1",
        status="active",
    )
    drive_credential = ConnectorCredentialReference(
        owner_user_id=OWNER_ID,
        connector_type="drive",
        reference_label="drive:oauth:ref",
        key_version="local-fake-v1",
        status="active",
    )
    session.add_all([gmail_credential, drive_credential])
    session.flush()
    gmail_connection = ConnectorConnection(
        owner_user_id=OWNER_ID,
        connector_type="gmail",
        display_name="Owner Gmail",
        account_identifier="owner@example.test",
        status="connected",
        granted_scopes=[GMAIL_SCOPE_MODIFY],
        credential_reference_id=gmail_credential.credential_reference_id,
        health_status="healthy",
    )
    drive_connection = ConnectorConnection(
        owner_user_id=OWNER_ID,
        connector_type="drive",
        display_name="Owner Drive",
        account_identifier="owner@example.test",
        status="connected",
        granted_scopes=[DRIVE_SCOPE_FILE],
        credential_reference_id=drive_credential.credential_reference_id,
        health_status="healthy",
    )
    session.add_all([gmail_connection, drive_connection])
    session.flush()
    return gmail_connection.connection_id, drive_connection.connection_id


def subscribe(session: Session, *event_types: str) -> None:
    for event_type in event_types:
        session.add(
            WebhookSubscription(
                external_client_id=CLIENT_ID,
                event_type=event_type,
                target_url=f"https://client.example.test/webhooks/{event_type}",
                secret_reference="secret-ref",
                status="active",
            )
        )
    session.flush()


def webhook_context() -> GmailOperationalWebhookContext:
    return GmailOperationalWebhookContext(
        settings=webhook_settings(),
        correlation_id="corr-gmail-operational",
        now=datetime(2026, 7, 18, 12, 0, tzinfo=UTC),
    )


def test_gmail_agent_descriptor_registration_is_idempotent_and_secret_free() -> None:
    factory = database_factory()
    with factory() as session:
        first = ensure_gmail_agent_registered(session)
        second = ensure_gmail_agent_registered(session)
        session.commit()

    assert second.agent_id == first.agent_id
    assert first.slug == "gmail-agent"
    assert first.risk_level == "high"
    assert first.supports_manual_run is True
    assert first.supports_scheduled_run is True
    assert first.required_connectors == ["gmail", "drive"]
    encoded = json.dumps(first.configuration_schema)
    assert "token" not in encoded.lower()
    assert "secret" not in encoded.lower()


def test_manual_and_scheduled_gmail_runs_enqueue_reference_only_packets() -> None:
    factory = database_factory()
    with factory() as session:
        seed_owner_client_and_connections(session)
        manual = create_gmail_manual_run(
            session,
            owner_user_id=OWNER_ID,
            idempotency_key="gmail-manual-run-key",
            correlation_id="corr-manual",
        )
        scheduled = create_gmail_scheduled_run(
            session,
            owner_user_id=OWNER_ID,
            idempotency_key="gmail-scheduled-run-key",
            correlation_id="corr-scheduled",
            scheduled_for=datetime(2026, 7, 18, 13, 0, tzinfo=UTC),
            schedule_id="sch_gmail",
        )
        session.commit()

        jobs = {
            job.resource_reference: job
            for job in session.scalars(select(QueueJob)).all()
        }

    assert manual.trigger_source == "manual"
    assert scheduled.trigger_source == "scheduled"
    assert jobs[manual.run_id].payload_metadata == {
        "run_id": manual.run_id,
        "agent_id": manual.agent_id,
        "trigger_source": "manual",
    }
    assert jobs[scheduled.run_id].payload_metadata == {
        "run_id": scheduled.run_id,
        "agent_id": scheduled.agent_id,
        "trigger_source": "scheduled",
        "scheduled_for": "2026-07-18T13:00:00+00:00",
        "schedule_id": "sch_gmail",
    }
    assert "body" not in json.dumps([job.payload_metadata for job in jobs.values()])
    assert "token" not in json.dumps([job.payload_metadata for job in jobs.values()])


def test_run_step_metadata_rejects_sensitive_operational_payloads() -> None:
    factory = database_factory()
    with factory() as session:
        seed_owner_client_and_connections(session)
        run = create_gmail_manual_run(
            session,
            owner_user_id=OWNER_ID,
            idempotency_key="gmail-sensitive-step-key",
            correlation_id="corr-sensitive-step",
        )

        with pytest.raises(ApiError) as blocked:
            record_run_step(
                session,
                run_id=run.run_id,
                step_name="unsafe_summary",
                status="succeeded",
                metadata={"message_body": "not allowed"},
            )

    assert blocked.value.code == "run_step_metadata_not_minimized"


def test_gmail_reconciliation_run_records_steps_webhooks_and_audit() -> None:
    factory = database_factory()
    with factory() as session:
        gmail_connection_id, _drive_connection_id = seed_owner_client_and_connections(
            session
        )
        subscribe(
            session,
            "run.state_changed",
            "message.held_for_manual_handling",
        )
        run = create_gmail_manual_run(
            session,
            owner_user_id=OWNER_ID,
            idempotency_key="gmail-reconcile-run-key",
            correlation_id="corr-reconcile",
            webhook_context=webhook_context(),
        )

        result = execute_gmail_reconciliation_run(
            session,
            owner_user_id=OWNER_ID,
            run_id=run.run_id,
            connection_id=gmail_connection_id,
            provider=FakeGmailProvider(
                [
                    FakeGmailMessage(
                        provider_message_reference="msg-recruiter",
                        provider_thread_reference="thread-recruiter",
                        sender_address="recruiter@example.test",
                        subject="Platform role",
                        snippet="Following up about the interview.",
                        label_names=("INBOX",),
                        received_at=datetime(2026, 7, 18, 11, 0, tzinfo=UTC),
                    ),
                    FakeGmailMessage(
                        provider_message_reference="msg-held",
                        provider_thread_reference="thread-held",
                        sender_address="care@example.test",
                        subject="Appointment reminder",
                        snippet="Reminder for your appointment.",
                        label_names=("INBOX",),
                        received_at=datetime(2026, 7, 18, 11, 5, tzinfo=UTC),
                    ),
                ]
            ),
            policy=GmailRetrievalPolicy(max_messages=10),
            webhook_context=webhook_context(),
        )
        session.commit()

        steps = list(
            session.scalars(
                select(AgentRunStep)
                .where(AgentRunStep.run_id == run.run_id)
                .order_by(AgentRunStep.sequence_number)
            )
        )
        attempts = list(session.scalars(select(WebhookDeliveryAttempt)))
        audits = list(
            session.scalars(
                select(AuditEvent).where(AuditEvent.resource_type == "agent_run")
            )
        )

    assert result.run.status == "succeeded"
    assert [step.step_name for step in steps] == [
        "eligibility",
        "classification",
        "suppression",
        "actions",
        "questions",
        "drafts",
        "approvals",
        "continuation",
        "outcomes",
    ]
    assert steps[0].metadata_json == {"eligible_count": 2, "skipped_count": 0}
    assert steps[2].metadata_json == {"suppressed_count": 1, "held_count": 1}
    assert {attempt.event_type for attempt in attempts} == {
        "run.state_changed",
        "message.held_for_manual_handling",
    }
    assert all(
        "message" not in json.dumps(attempt.payload_summary) for attempt in attempts
    )
    assert [event.action for event in audits] == [
        "queue",
        "start",
        "summarize",
        "complete",
    ]


def test_gmail_reconciliation_run_failure_is_terminal_and_minimized() -> None:
    factory = database_factory()
    with factory() as session:
        seed_owner_client_and_connections(session)
        subscribe(session, "run.state_changed")
        run = create_gmail_manual_run(
            session,
            owner_user_id=OWNER_ID,
            idempotency_key="gmail-failed-run-key",
            correlation_id="corr-failed",
        )

        result = execute_gmail_reconciliation_run(
            session,
            owner_user_id=OWNER_ID,
            run_id=run.run_id,
            connection_id="conn_missing",
            provider=FakeGmailProvider([]),
            policy=GmailRetrievalPolicy(max_messages=10),
            webhook_context=webhook_context(),
        )
        session.commit()

        failure_step = session.scalar(
            select(AgentRunStep).where(AgentRunStep.run_id == run.run_id)
        )
        attempts = list(session.scalars(select(WebhookDeliveryAttempt)))

    assert result.run.status == "failed"
    assert result.run.failure_reason_code == "connection_not_found"
    assert failure_step is not None
    assert failure_step.metadata_json == {"reason_code": "connection_not_found"}
    assert attempts[-1].payload_summary["status"] == "failed"
    assert "conn_missing" not in json.dumps(attempts[-1].payload_summary)


def test_gmail_operational_webhook_producers_are_minimized() -> None:
    factory = database_factory()
    with factory() as session:
        gmail_connection_id, _drive_connection_id = seed_owner_client_and_connections(
            session
        )
        subscribe(session, "approval.pending", WEBHOOK_EVENT_SEND_OUTCOME)
        agent = ensure_gmail_agent_registered(session)
        message = GmailMessageRecord(
            owner_user_id=OWNER_ID,
            connection_id=gmail_connection_id,
            provider_message_reference="msg-send",
            provider_thread_reference="thread-send",
            sender_address="sender@example.test",
            sender_domain="example.test",
            subject_preview="Project follow-up",
            content_excerpt_hash="0" * 64,
            attachment_metadata=[],
            label_names=["INBOX"],
            received_at=datetime(2026, 7, 18, 11, 0, tzinfo=UTC),
            eligibility_reason="query:in:inbox",
            classification_category="Recruiters",
            classification_confidence=78,
            classification_status="classified",
            review_reason_code=None,
            suppression_status="not_suppressed",
            source_integrity_hash="1" * 64,
        )
        session.add(message)
        session.flush()
        draft = GmailDraftRecord(
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message.gmail_message_record_id,
            connection_id=gmail_connection_id,
            provider_message_reference=message.provider_message_reference,
            provider_draft_reference="draft-send",
            scenario="recruiter_reply",
            status="created",
            idempotency_key="draft-operational-key",
            subject_preview="Re: Project follow-up",
            body_hash="2" * 64,
            facts_used=[],
            evidence_summary={"body_hash": "2" * 64},
            decision_context_manifest={"draft_body_hash": "2" * 64},
        )
        approval = ApprovalRequest(
            owner_user_id=OWNER_ID,
            agent_id=agent.agent_id,
            status="approved",
            revision=1,
            action_type="gmail.send",
            action_reference="gmail_draft:draft-send",
            action_payload_hash="3" * 64,
            evidence_summary={"gmail_draft_record_id": "draft"},
            decision_context_manifest={"draft_body_hash": "2" * 64},
            continuation_status="sent",
        )
        session.add_all([draft, approval])
        session.flush()
        outcome = GmailSendOutcomeRecord(
            owner_user_id=OWNER_ID,
            approval_id=approval.approval_id,
            gmail_draft_record_id=draft.gmail_draft_record_id,
            provider_draft_reference=draft.provider_draft_reference,
            provider_send_reference="send-provider-ref",
            outcome="sent",
            idempotency_key="send-operational-key",
            metadata_json={"outcome": "sent"},
        )
        session.add(outcome)
        session.flush()

        approval_attempts = enqueue_gmail_approval_pending_event(
            session,
            approval_id=approval.approval_id,
            webhook_context=webhook_context(),
        )
        send_attempts = enqueue_gmail_send_outcome_event(
            session,
            outcome=outcome,
            webhook_context=webhook_context(),
        )
        session.commit()

    assert approval_attempts[0].event_type == "approval.pending"
    assert approval_attempts[0].payload_summary == {
        "resource_id": approval.approval_id,
        "resource_type": "approval",
        "status": "pending",
        "reconciliation_path": f"/api/v1/approvals/{approval.approval_id}/evidence",
    }
    assert send_attempts[0].event_type == WEBHOOK_EVENT_SEND_OUTCOME
    assert send_attempts[0].payload_summary == {
        "resource_id": approval.approval_id,
        "resource_type": "approval",
        "status": "sent",
        "reconciliation_path": f"/api/v1/approvals/{approval.approval_id}/evidence",
    }
    encoded = json.dumps([attempt.payload_summary for attempt in send_attempts])
    assert "send-provider-ref" not in encoded
    assert "Project follow-up" not in encoded
