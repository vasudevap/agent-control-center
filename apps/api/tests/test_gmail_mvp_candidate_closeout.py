from __future__ import annotations

import json
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.db.base import Base
from atlas_api.models.approval import ApprovalRequest, ManualHandlingRecord
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.gmail_message import (
    GmailDraftRecord,
    GmailMessageRecord,
    GmailSendOutcomeRecord,
)
from atlas_api.models.knowledge import KnowledgeAnswer, KnowledgeQuestion
from atlas_api.models.run import AgentRunStep
from atlas_api.models.webhook import WebhookDeliveryAttempt, WebhookSubscription
from atlas_api.services.approval_contracts import submit_decision
from atlas_api.services.connectors import (
    DRIVE_SCOPE_FILE,
    GMAIL_SCOPE_MODIFY,
    REJECTED_GMAIL_SCOPE_FULL_MAILBOX,
    complete_oauth_connection,
    start_oauth_connection,
)
from atlas_api.services.gmail_actions import (
    FakeDriveProvider,
    FakeGmailActionProvider,
    GmailLowRiskActionPolicy,
    execute_low_risk_mailbox_actions,
)
from atlas_api.services.gmail_approvals import (
    FakeGmailSendProvider,
    FakeSendResult,
    continue_approved_gmail_send,
    create_gmail_send_approval,
)
from atlas_api.services.gmail_drafts import (
    FakeDraftGenerator,
    FakeGmailDraftProvider,
    GeneratedDraftOutput,
    create_gmail_draft,
)
from atlas_api.services.gmail_knowledge import (
    GmailKnowledgeWebhookContext,
    prepare_gmail_knowledge_context,
    submit_gmail_knowledge_answer,
)
from atlas_api.services.gmail_messages import (
    FakeGmailAttachment,
    FakeGmailMessage,
    FakeGmailProvider,
    GmailRetrievalPolicy,
    retrieve_and_classify_messages,
)
from atlas_api.services.gmail_operational import (
    WEBHOOK_EVENT_SEND_OUTCOME,
    GmailOperationalWebhookContext,
    create_gmail_manual_run,
    enqueue_gmail_approval_pending_event,
    enqueue_gmail_send_outcome_event,
    execute_gmail_reconciliation_run,
)

OWNER_ID = "usr_owner"
CLIENT_ID = "external-client-1"


@pytest.fixture
def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


def settings() -> Settings:
    return Settings(
        environment="test",
        webhook_signing_key_id="current",
        webhook_signing_secret=SecretStr("webhook-secret"),
    )


def seed_owner_and_client(session: Session) -> None:
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
    session.flush()


def connect_fake_oauth(
    session: Session,
    *,
    connector_type: str,
    requested_scope: str,
    account_identifier: str,
) -> str:
    start = start_oauth_connection(
        session,
        owner_user_id=OWNER_ID,
        connector_type=connector_type,
        requested_scopes=[requested_scope],
        redirect_uri="https://client.example.test/oauth/callback",
    )
    state = parse_qs(urlparse(start.authorization_url).query)["state"][0]
    connection = complete_oauth_connection(
        session,
        owner_user_id=OWNER_ID,
        connector_type=connector_type,
        state=state,
        authorization_code=f"fake-{connector_type}-authorization-code",
        account_identifier=account_identifier,
        granted_scopes=[requested_scope],
        display_name=f"Owner {connector_type}",
    )
    return connection.connection_id


def subscribe(session: Session) -> None:
    for event_type in (
        "run.state_changed",
        "message.held_for_manual_handling",
        "knowledge.question.pending",
        "knowledge.question.answered",
        "approval.pending",
        WEBHOOK_EVENT_SEND_OUTCOME,
    ):
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
        settings=settings(),
        correlation_id="corr-gmail-closeout",
        now=datetime(2026, 7, 18, 12, 0, tzinfo=UTC),
    )


def knowledge_webhook_context() -> GmailKnowledgeWebhookContext:
    return GmailKnowledgeWebhookContext(
        settings=settings(),
        correlation_id="corr-gmail-closeout",
        now=datetime(2026, 7, 18, 12, 0, tzinfo=UTC),
    )


def closeout_messages() -> list[FakeGmailMessage]:
    return [
        FakeGmailMessage(
            provider_message_reference="msg-recruiter-closeout",
            provider_thread_reference="thread-recruiter-closeout",
            sender_address="recruiter@example.test",
            subject="Interview opportunity",
            snippet="Following up about the platform role.",
            label_names=("INBOX",),
            received_at=datetime(2026, 7, 18, 11, 0, tzinfo=UTC),
        ),
        FakeGmailMessage(
            provider_message_reference="msg-receipt-closeout",
            provider_thread_reference="thread-receipt-closeout",
            sender_address="store@example.test",
            subject="Your receipt",
            snippet="Receipt for order 123.",
            label_names=("INBOX",),
            received_at=datetime(2026, 7, 18, 11, 5, tzinfo=UTC),
            attachments=(
                FakeGmailAttachment(
                    provider_attachment_reference="att-receipt-closeout",
                    filename="receipt.pdf",
                    mime_type="application/pdf",
                    size_bytes=1234,
                ),
            ),
        ),
        FakeGmailMessage(
            provider_message_reference="msg-held-closeout",
            provider_thread_reference="thread-held-closeout",
            sender_address="care@example.test",
            subject="Appointment reminder",
            snippet="Reminder for your appointment.",
            label_names=("INBOX",),
            received_at=datetime(2026, 7, 18, 11, 10, tzinfo=UTC),
        ),
    ]


def action_policy() -> GmailLowRiskActionPolicy:
    return GmailLowRiskActionPolicy(
        label_by_category={"Receipts": "Atlas/Receipts"},
        archive_categories=frozenset({"Receipts"}),
        attachment_save_categories=frozenset({"Receipts"}),
        drive_folder_reference="drive-folder-receipts",
    )


def test_gmail_mvp_candidate_fake_provider_workflow_is_coherent(
    database_factory: sessionmaker[Session],
) -> None:
    gmail_action_provider = FakeGmailActionProvider(
        attachments={"att-receipt-closeout": b"synthetic-pdf"}
    )
    drive_provider = FakeDriveProvider()
    draft_provider = FakeGmailDraftProvider()
    send_provider = FakeGmailSendProvider(FakeSendResult("sent", "send-closeout"))
    with database_factory() as session:
        seed_owner_and_client(session)
        gmail_connection_id = connect_fake_oauth(
            session,
            connector_type="gmail",
            requested_scope=GMAIL_SCOPE_MODIFY,
            account_identifier="owner@example.test",
        )
        drive_connection_id = connect_fake_oauth(
            session,
            connector_type="google_drive",
            requested_scope=DRIVE_SCOPE_FILE,
            account_identifier="owner-drive@example.test",
        )
        subscribe(session)
        run = create_gmail_manual_run(
            session,
            owner_user_id=OWNER_ID,
            idempotency_key="gmail-closeout-run",
            correlation_id="corr-gmail-closeout",
            webhook_context=webhook_context(),
        )
        run_result = execute_gmail_reconciliation_run(
            session,
            owner_user_id=OWNER_ID,
            run_id=run.run_id,
            connection_id=gmail_connection_id,
            provider=FakeGmailProvider(closeout_messages()),
            policy=GmailRetrievalPolicy(max_messages=10),
            webhook_context=webhook_context(),
        )
        messages = {
            record.provider_message_reference: record
            for record in session.scalars(select(GmailMessageRecord)).all()
        }
        recruiter = messages["msg-recruiter-closeout"]
        receipt = messages["msg-receipt-closeout"]
        held = messages["msg-held-closeout"]

        actions = execute_low_risk_mailbox_actions(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=receipt.gmail_message_record_id,
            gmail_provider=gmail_action_provider,
            drive_provider=drive_provider,
            policy=action_policy(),
            idempotency_key_prefix="gmail-closeout-actions",
            drive_connection_id=drive_connection_id,
            correlation_id="corr-gmail-closeout",
        )
        missing = prepare_gmail_knowledge_context(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=recruiter.gmail_message_record_id,
            scenario="recruiter_reply",
            correlation_id="corr-gmail-closeout",
            webhook_context=knowledge_webhook_context(),
        )
        for question_id, answer_text in zip(
            missing.question_ids,
            ["Tuesday afternoon.", "Platform architecture roles."],
            strict=True,
        ):
            submit_gmail_knowledge_answer(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=recruiter.gmail_message_record_id,
                question_id=question_id,
                answer_text=answer_text,
                correlation_id="corr-gmail-closeout",
                webhook_context=knowledge_webhook_context(),
            )
        ready = prepare_gmail_knowledge_context(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=recruiter.gmail_message_record_id,
            scenario="recruiter_reply",
            correlation_id="corr-gmail-closeout",
        )
        draft = create_gmail_draft(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=recruiter.gmail_message_record_id,
            scenario="recruiter_reply",
            generator=FakeDraftGenerator(
                GeneratedDraftOutput(
                    subject="Re: Interview opportunity",
                    body="Thanks for reaching out. Tuesday afternoon works for me.",
                )
            ),
            provider=draft_provider,
            idempotency_key="gmail-closeout-draft",
            correlation_id="corr-gmail-closeout",
        )
        approval = create_gmail_send_approval(
            session,
            owner_user_id=OWNER_ID,
            gmail_draft_record_id=draft.draft.gmail_draft_record_id,
            correlation_id="corr-gmail-closeout",
        )
        enqueue_gmail_approval_pending_event(
            session,
            approval_id=approval.approval_id,
            webhook_context=webhook_context(),
        )
        approved, _decision = submit_decision(
            session,
            owner_user_id=OWNER_ID,
            approval_id=approval.approval_id,
            decision="approve",
            submitted_revision=1,
            channel="internal",
            external_client_id=None,
            reviewer_user_id=OWNER_ID,
        )
        send = continue_approved_gmail_send(
            session,
            owner_user_id=OWNER_ID,
            approval_id=approved.approval_id,
            provider=send_provider,
            idempotency_key="gmail-closeout-send",
            correlation_id="corr-gmail-closeout",
        )
        enqueue_gmail_send_outcome_event(
            session,
            outcome=send.outcome,
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
        webhook_attempts = list(session.scalars(select(WebhookDeliveryAttempt)))
        audit_events = list(session.scalars(select(AuditEvent)))
        manual_holds = list(session.scalars(select(ManualHandlingRecord)))
        questions = list(session.scalars(select(KnowledgeQuestion)))
        answers = list(session.scalars(select(KnowledgeAnswer)))
        drafts = list(session.scalars(select(GmailDraftRecord)))
        approvals = list(session.scalars(select(ApprovalRequest)))
        outcomes = list(session.scalars(select(GmailSendOutcomeRecord)))

    assert run_result.run.status == "succeeded"
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
    assert actions.denied_count == 0
    assert [operation.operation_type for operation in actions.operations] == [
        "gmail.apply_label",
        "gmail.archive_message",
        "gmail.get_attachment",
        "drive.save_attachment",
    ]
    assert missing.status == "questions_pending"
    assert len(missing.question_ids) == 2
    assert ready.status == "ready"
    assert len(questions) == 2
    assert len(answers) == 2
    assert len(drafts) == 1
    assert len(approvals) == 1
    assert outcomes[0].outcome == "sent"
    assert approved.continuation_status == "sent"
    assert len(send_provider.send_attempts) == 1
    assert held.manual_handling_id == manual_holds[0].manual_handling_id
    assert held.suppression_status == "suppressed"
    assert all(
        draft.gmail_message_record_id != held.gmail_message_record_id
        for draft in drafts
    )
    assert {attempt.event_type for attempt in webhook_attempts} >= {
        "run.state_changed",
        "message.held_for_manual_handling",
        "knowledge.question.pending",
        "knowledge.question.answered",
        "approval.pending",
        WEBHOOK_EVENT_SEND_OUTCOME,
    }
    encoded_webhooks = json.dumps(
        [attempt.payload_summary for attempt in webhook_attempts]
    )
    assert "Tuesday afternoon works" not in encoded_webhooks
    assert "synthetic-pdf" not in encoded_webhooks
    assert "fake-gmail-authorization-code" not in encoded_webhooks
    assert {event.result for event in audit_events} >= {"succeeded"}


def test_gmail_mvp_candidate_security_negatives_fail_closed(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        seed_owner_and_client(session)
        with pytest.raises(ApiError) as broad_scope:
            start_oauth_connection(
                session,
                owner_user_id=OWNER_ID,
                connector_type="gmail",
                requested_scopes=[
                    GMAIL_SCOPE_MODIFY,
                    REJECTED_GMAIL_SCOPE_FULL_MAILBOX,
                ],
                redirect_uri="https://client.example.test/oauth/callback",
            )
        gmail_connection_id = connect_fake_oauth(
            session,
            connector_type="gmail",
            requested_scope=GMAIL_SCOPE_MODIFY,
            account_identifier="owner@example.test",
        )
        result = retrieve_and_classify_messages(
            session,
            owner_user_id=OWNER_ID,
            connection_id=gmail_connection_id,
            provider=FakeGmailProvider([closeout_messages()[-1]]),
            policy=GmailRetrievalPolicy(max_messages=10),
        )
        suppressed = result.records[0]

        with pytest.raises(ApiError) as question_blocked:
            prepare_gmail_knowledge_context(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=suppressed.gmail_message_record_id,
                scenario="recruiter_reply",
                correlation_id="corr-suppressed-question",
            )
        with pytest.raises(ApiError) as draft_blocked:
            create_gmail_draft(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=suppressed.gmail_message_record_id,
                scenario="recruiter_reply",
                generator=FakeDraftGenerator(
                    GeneratedDraftOutput(
                        subject="Re: Appointment",
                        body="This should not be created.",
                    )
                ),
                provider=FakeGmailDraftProvider(),
                idempotency_key="suppressed-closeout-draft",
                correlation_id="corr-suppressed-draft",
            )
        session.commit()

        assert broad_scope.value.code == "connector_scope_rejected"
        assert question_blocked.value.code == "gmail_message_suppressed"
        assert draft_blocked.value.code == "gmail_message_suppressed"
        assert not list(session.scalars(select(GmailDraftRecord)))
        assert not list(session.scalars(select(KnowledgeQuestion)))
        assert not list(session.scalars(select(ApprovalRequest)))
        assert "mail.google.com" not in json.dumps(
            [event.metadata_json for event in session.scalars(select(AuditEvent))]
        )
        assert "authorization-code" not in json.dumps(
            [event.metadata_json for event in session.scalars(select(AuditEvent))]
        )
