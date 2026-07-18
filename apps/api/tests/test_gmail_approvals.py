from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.errors import ApiError
from atlas_api.db.base import Base
from atlas_api.models.approval import ApprovalRequest
from atlas_api.models.audit import AuditEvent
from atlas_api.models.connector import (
    ConnectorConnection,
    ConnectorCredentialReference,
)
from atlas_api.models.external_client import User
from atlas_api.models.gmail_message import GmailSendOutcomeRecord
from atlas_api.models.knowledge import KnowledgeFact
from atlas_api.services.approval_contracts import submit_decision
from atlas_api.services.connectors import (
    GMAIL_SCOPE_MODIFY,
    ensure_default_connector_types,
)
from atlas_api.services.gmail_approvals import (
    FakeGmailSendProvider,
    FakeSendResult,
    continue_approved_gmail_send,
    create_gmail_send_approval,
    provider_send_reference,
)
from atlas_api.services.gmail_drafts import (
    FakeDraftGenerator,
    FakeGmailDraftProvider,
    GeneratedDraftOutput,
    create_gmail_draft,
)
from atlas_api.services.gmail_messages import (
    FakeGmailMessage,
    FakeGmailProvider,
    GmailRetrievalPolicy,
    retrieve_and_classify_messages,
)
from atlas_api.services.knowledge_facts import create_fact, update_fact

OWNER_ID = "usr_owner"


@pytest.fixture
def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


def seed_connection(session: Session) -> str:
    if session.get(User, OWNER_ID) is None:
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
    ensure_default_connector_types(session)
    credential = ConnectorCredentialReference(
        owner_user_id=OWNER_ID,
        connector_type="gmail",
        reference_label="gmail:oauth:ref",
        key_version="local-fake-v1",
        status="active",
    )
    session.add(credential)
    session.flush()
    connection = ConnectorConnection(
        owner_user_id=OWNER_ID,
        connector_type="gmail",
        display_name="Owner Gmail",
        account_identifier="owner@example.test",
        status="connected",
        granted_scopes=[GMAIL_SCOPE_MODIFY],
        credential_reference_id=credential.credential_reference_id,
        health_status="healthy",
    )
    session.add(connection)
    session.flush()
    connection_id = connection.connection_id
    session.commit()
    return connection_id


def seed_message(session: Session, *, connection_id: str) -> str:
    result = retrieve_and_classify_messages(
        session,
        owner_user_id=OWNER_ID,
        connection_id=connection_id,
        provider=FakeGmailProvider(
            [
                FakeGmailMessage(
                    provider_message_reference="msg-recruiter",
                    provider_thread_reference="thread-msg-recruiter",
                    sender_address="recruiter@example.test",
                    subject="Interview opportunity",
                    snippet="Following up about the platform role.",
                    label_names=("INBOX",),
                    received_at=datetime(2026, 7, 18, 12, 0, tzinfo=UTC),
                )
            ]
        ),
        policy=GmailRetrievalPolicy(max_messages=10),
    )
    session.commit()
    return result.records[0].gmail_message_record_id


def seed_required_facts(session: Session) -> list[str]:
    fact_ids: list[str] = []
    for fact_key, value, volatile in (
        ("gmail.reply.availability", "Tuesday afternoon.", True),
        ("gmail.reply.role_preferences", "Platform architecture roles.", False),
    ):
        fact, _revision = create_fact(
            session,
            owner_user_id=OWNER_ID,
            fact_key=fact_key,
            display_value=value,
            classification="internal",
            source_type="human",
            source_reference="manual:test",
            provenance_summary="Synthetic test fact.",
            is_volatile=volatile,
            confirmed=True,
        )
        fact_ids.append(fact.knowledge_fact_id)
    session.commit()
    return fact_ids


def seed_draft(session: Session) -> str:
    connection_id = seed_connection(session)
    message_id = seed_message(session, connection_id=connection_id)
    seed_required_facts(session)
    result = create_gmail_draft(
        session,
        owner_user_id=OWNER_ID,
        gmail_message_record_id=message_id,
        scenario="recruiter_reply",
        generator=FakeDraftGenerator(
            GeneratedDraftOutput(
                subject="Re: Interview opportunity",
                body="Thanks for reaching out. Tuesday afternoon works for me.",
            )
        ),
        provider=FakeGmailDraftProvider(),
        idempotency_key="draft-for-approval-key",
        correlation_id="corr-draft",
    )
    session.commit()
    return result.draft.gmail_draft_record_id


def approve(session: Session, approval_id: str) -> ApprovalRequest:
    approval, _decision = submit_decision(
        session,
        owner_user_id=OWNER_ID,
        approval_id=approval_id,
        decision="approve",
        submitted_revision=1,
        channel="internal",
        external_client_id=None,
        reviewer_user_id=OWNER_ID,
    )
    session.flush()
    return approval


def test_send_approval_creation_is_minimized(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        draft_id = seed_draft(session)

        approval = create_gmail_send_approval(
            session,
            owner_user_id=OWNER_ID,
            gmail_draft_record_id=draft_id,
            correlation_id="corr-approval",
        )
        session.commit()

    assert approval.action_type == "gmail.send"
    assert approval.status == "pending"
    assert "facts_used" in approval.evidence_summary
    assert "fact_revision_bindings" in approval.decision_context_manifest
    assert "Tuesday afternoon works" not in str(approval.evidence_summary)


def test_edit_then_approve_supersedes_original_approval(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        draft_id = seed_draft(session)
        approval = create_gmail_send_approval(
            session,
            owner_user_id=OWNER_ID,
            gmail_draft_record_id=draft_id,
        )

        replacement, _decision = submit_decision(
            session,
            owner_user_id=OWNER_ID,
            approval_id=approval.approval_id,
            decision="edit_approve",
            submitted_revision=1,
            channel="internal",
            external_client_id=None,
            reviewer_user_id=OWNER_ID,
            edited_action_payload={
                "gmail_draft_record_id": draft_id,
                "draft_body_hash": "edited-hash",
            },
        )
        session.commit()

    assert replacement.status == "approved"
    with database_factory() as session:
        original = session.get(ApprovalRequest, approval.approval_id)
        assert original is not None
        assert original.status == "superseded"
        assert original.superseded_by_approval_id == replacement.approval_id


def test_rejected_approval_stops_send_continuation(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        draft_id = seed_draft(session)
        approval = create_gmail_send_approval(
            session,
            owner_user_id=OWNER_ID,
            gmail_draft_record_id=draft_id,
        )
        submit_decision(
            session,
            owner_user_id=OWNER_ID,
            approval_id=approval.approval_id,
            decision="reject",
            submitted_revision=1,
            channel="internal",
            external_client_id=None,
            reviewer_user_id=OWNER_ID,
        )

        with pytest.raises(ApiError) as blocked:
            continue_approved_gmail_send(
                session,
                owner_user_id=OWNER_ID,
                approval_id=approval.approval_id,
                provider=FakeGmailSendProvider(FakeSendResult("sent", "sent-1")),
                idempotency_key="send-rejected-key-1",
            )

    assert blocked.value.code == "gmail_send_approval_not_approved"


def test_approved_send_continuation_records_sent_and_replays(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        draft_id = seed_draft(session)
        approval = create_gmail_send_approval(
            session,
            owner_user_id=OWNER_ID,
            gmail_draft_record_id=draft_id,
        )
        approve(session, approval.approval_id)
        provider = FakeGmailSendProvider(
            FakeSendResult(
                "sent",
                provider_send_reference("draft-provider-ref"),
            )
        )

        first = continue_approved_gmail_send(
            session,
            owner_user_id=OWNER_ID,
            approval_id=approval.approval_id,
            provider=provider,
            idempotency_key="send-approved-key-1",
            correlation_id="corr-send",
        )
        second = continue_approved_gmail_send(
            session,
            owner_user_id=OWNER_ID,
            approval_id=approval.approval_id,
            provider=provider,
            idempotency_key="send-approved-key-1",
            correlation_id="corr-send",
        )
        session.commit()

    assert first.outcome.outcome == "sent"
    assert second.replayed is True
    assert len(provider.send_attempts) == 1
    with database_factory() as session:
        approval = session.get(ApprovalRequest, approval.approval_id)
        assert approval is not None
        assert approval.continuation_status == "sent"
        assert session.scalar(select(GmailSendOutcomeRecord)) is not None


def test_changed_fact_blocks_send_continuation(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        draft_id = seed_draft(session)
        approval = create_gmail_send_approval(
            session,
            owner_user_id=OWNER_ID,
            gmail_draft_record_id=draft_id,
        )
        approve(session, approval.approval_id)
        fact = session.scalar(
            select(KnowledgeFact).where(
                KnowledgeFact.fact_key == "gmail.reply.availability"
            )
        )
        assert fact is not None
        update_fact(
            session,
            owner_user_id=OWNER_ID,
            knowledge_fact_id=fact.knowledge_fact_id,
            display_value="Wednesday morning.",
            source_type="human",
            source_reference="manual:test",
            provenance_summary="Changed fact.",
            is_volatile=True,
            confirmed=True,
        )

        with pytest.raises(ApiError) as blocked:
            continue_approved_gmail_send(
                session,
                owner_user_id=OWNER_ID,
                approval_id=approval.approval_id,
                provider=FakeGmailSendProvider(FakeSendResult("sent", "sent-1")),
                idempotency_key="send-stale-key-1",
            )

    assert blocked.value.code == "fact_revision_changed"


@pytest.mark.parametrize("outcome", ["failed", "indeterminate"])
def test_provider_non_success_outcomes_are_recorded(
    database_factory: sessionmaker[Session],
    outcome: str,
) -> None:
    with database_factory() as session:
        draft_id = seed_draft(session)
        approval = create_gmail_send_approval(
            session,
            owner_user_id=OWNER_ID,
            gmail_draft_record_id=draft_id,
        )
        approve(session, approval.approval_id)

        result = continue_approved_gmail_send(
            session,
            owner_user_id=OWNER_ID,
            approval_id=approval.approval_id,
            provider=FakeGmailSendProvider(
                FakeSendResult(outcome, None, f"provider_{outcome}")
            ),
            idempotency_key=f"send-{outcome}-key-1",
            correlation_id=f"corr-{outcome}",
        )
        session.commit()

    assert result.outcome.outcome == outcome
    assert result.outcome.reason_code == f"provider_{outcome}"
    with database_factory() as session:
        audit = session.scalar(
            select(AuditEvent).where(AuditEvent.event_type == "gmail.send_outcome")
        )
        assert audit is not None
        assert audit.result == outcome
