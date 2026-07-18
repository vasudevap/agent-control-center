from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.core.events import WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING
from atlas_api.db.base import Base, utc_now
from atlas_api.models.approval import ApprovalRequest
from atlas_api.models.audit import AuditEvent
from atlas_api.models.connector import (
    ConnectorConnection,
    ConnectorCredentialReference,
)
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.knowledge import (
    KnowledgeAnswer,
    KnowledgeFact,
    KnowledgeFactRevision,
    KnowledgeQuestion,
)
from atlas_api.models.webhook import WebhookDeliveryAttempt, WebhookSubscription
from atlas_api.services.connectors import (
    GMAIL_SCOPE_MODIFY,
    ensure_default_connector_types,
)
from atlas_api.services.gmail_knowledge import (
    GmailKnowledgeWebhookContext,
    prepare_gmail_knowledge_context,
    submit_gmail_knowledge_answer,
)
from atlas_api.services.gmail_messages import (
    FakeGmailMessage,
    FakeGmailProvider,
    GmailRetrievalPolicy,
    retrieve_and_classify_messages,
)
from atlas_api.services.knowledge_facts import create_fact

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


def seed_owner(session: Session) -> None:
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


def seed_gmail_connection(session: Session) -> str:
    seed_owner(session)
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


def seed_message(
    session: Session,
    *,
    connection_id: str,
    provider_message_reference: str = "msg-recruiter",
    sender: str = "recruiter@example.test",
    subject: str = "Interview opportunity",
    snippet: str = "Following up about the platform role.",
) -> str:
    provider = FakeGmailProvider(
        [
            FakeGmailMessage(
                provider_message_reference=provider_message_reference,
                provider_thread_reference=f"thread-{provider_message_reference}",
                sender_address=sender,
                subject=subject,
                snippet=snippet,
                label_names=("INBOX",),
                received_at=datetime(2026, 7, 18, 12, 0, tzinfo=UTC),
            )
        ]
    )
    result = retrieve_and_classify_messages(
        session,
        owner_user_id=OWNER_ID,
        connection_id=connection_id,
        provider=provider,
        policy=GmailRetrievalPolicy(max_messages=10),
    )
    session.commit()
    return result.records[0].gmail_message_record_id


def seed_fact(
    session: Session,
    *,
    fact_key: str,
    value: str,
    volatile: bool = False,
) -> str:
    _fact, revision = create_fact(
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
    session.flush()
    return revision.knowledge_fact_revision_id


def test_missing_required_facts_create_questions_not_approvals(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        message_id = seed_message(session, connection_id=connection_id)

        context = prepare_gmail_knowledge_context(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            scenario="recruiter_reply",
            correlation_id="corr-missing",
        )
        session.commit()

    assert context.status == "questions_pending"
    assert len(context.question_ids) == 2
    assert not context.fact_revision_ids
    with database_factory() as session:
        questions = list(session.scalars(select(KnowledgeQuestion)))
        assert {item.required_fact_key for item in questions} == {
            "gmail.reply.availability",
            "gmail.reply.role_preferences",
        }
        assert all(item.source_reference == "gmail:msg-recruiter" for item in questions)
        assert not list(session.scalars(select(ApprovalRequest)))


def test_fresh_governed_facts_are_returned_without_questions(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        message_id = seed_message(session, connection_id=connection_id)
        availability_revision_id = seed_fact(
            session,
            fact_key="gmail.reply.availability",
            value="Tuesday afternoon.",
            volatile=True,
        )
        preferences_revision_id = seed_fact(
            session,
            fact_key="gmail.reply.role_preferences",
            value="Platform architecture roles.",
        )

        context = prepare_gmail_knowledge_context(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            scenario="recruiter_reply",
            correlation_id="corr-ready",
        )
        session.commit()

    assert context.status == "ready"
    assert set(context.fact_revision_ids) == {
        availability_revision_id,
        preferences_revision_id,
    }
    assert not context.question_ids


def test_stale_volatile_fact_creates_reconfirmation_question(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        message_id = seed_message(session, connection_id=connection_id)
        seed_fact(
            session,
            fact_key="gmail.reply.availability",
            value="Tuesday afternoon.",
            volatile=True,
        )
        seed_fact(
            session,
            fact_key="gmail.reply.role_preferences",
            value="Platform architecture roles.",
        )
        stale_revision = session.scalar(
            select(KnowledgeFactRevision).where(
                KnowledgeFactRevision.source_reference == "manual:test",
                KnowledgeFactRevision.is_volatile.is_(True),
            )
        )
        assert stale_revision is not None
        stale_revision.confirmed_at = utc_now() - timedelta(days=45)

        context = prepare_gmail_knowledge_context(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            scenario="recruiter_reply",
            correlation_id="corr-stale",
            now=utc_now(),
        )
        session.commit()

    assert context.status == "questions_pending"
    assert len(context.fact_revision_ids) == 1
    with database_factory() as session:
        question = session.scalar(select(KnowledgeQuestion))
        assert question is not None
        assert question.required_fact_key == "gmail.reply.availability"


def test_answer_validation_rejects_prohibited_content(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        message_id = seed_message(session, connection_id=connection_id)
        context = prepare_gmail_knowledge_context(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            scenario="travel_admin",
            correlation_id="corr-answer",
        )

        with pytest.raises(ApiError) as rejected:
            submit_gmail_knowledge_answer(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=message_id,
                question_id=context.question_ids[0],
                answer_text="Use access_token abc123",
                correlation_id="corr-answer",
            )

    assert rejected.value.code == "knowledge_fact_prohibited_content"


def test_valid_answer_creates_fact_revision_with_safe_gmail_reference(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        message_id = seed_message(session, connection_id=connection_id)
        context = prepare_gmail_knowledge_context(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            scenario="travel_admin",
            correlation_id="corr-answer-valid",
        )

        _question, answer = submit_gmail_knowledge_answer(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            question_id=context.question_ids[0],
            answer_text="Use the ACME loyalty number.",
            correlation_id="corr-answer-valid",
        )
        session.commit()

    assert answer.validation_status == "accepted"
    with database_factory() as session:
        revision = session.get(KnowledgeFactRevision, answer.created_fact_revision_id)
        assert revision is not None
        assert revision.source_reference == "gmail:msg-recruiter"
        assert "Interview opportunity" not in revision.source_reference
        assert session.scalar(select(KnowledgeAnswer)) is not None


def test_suppressed_source_cannot_create_questions_or_answers(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        message_id = seed_message(
            session,
            connection_id=connection_id,
            provider_message_reference="msg-clinical",
            sender="clinic@example.test",
            subject="Clinic appointment",
            snippet="Appointment reminder.",
        )

        with pytest.raises(ApiError) as blocked:
            prepare_gmail_knowledge_context(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=message_id,
                scenario="travel_admin",
                correlation_id="corr-suppressed",
            )
        session.commit()

    assert blocked.value.code == "gmail_message_suppressed"
    with database_factory() as session:
        assert not list(session.scalars(select(KnowledgeQuestion)))
        assert not list(session.scalars(select(KnowledgeFact)))


def test_question_webhook_and_audit_are_minimized(
    database_factory: sessionmaker[Session],
) -> None:
    settings = Settings(
        environment="test",
        webhook_signing_key_id="current",
        webhook_signing_secret=SecretStr("webhook-secret"),
    )
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        message_id = seed_message(session, connection_id=connection_id)
        session.add(
            ExternalProductClient(
                external_client_id="client-1",
                display_name="Client",
                status="active",
                authentication_key_reference="key-ref",
                human_owner_user_id=OWNER_ID,
            )
        )
        session.flush()
        session.add(
            WebhookSubscription(
                external_client_id="client-1",
                event_type=WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING,
                target_url="https://client.example.test/webhooks/atlas",
                secret_reference="webhook-secret-ref",
                status="active",
            )
        )

        prepare_gmail_knowledge_context(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            scenario="travel_admin",
            correlation_id="corr-webhook",
            webhook_context=GmailKnowledgeWebhookContext(
                settings=settings,
                correlation_id="corr-webhook",
                now=datetime(2026, 7, 18, 13, 0, tzinfo=UTC),
            ),
        )
        session.commit()

    with database_factory() as session:
        attempt = session.scalar(select(WebhookDeliveryAttempt))
        assert attempt is not None
        assert set(attempt.payload_summary) == {
            "fact_key",
            "resource_id",
            "resource_type",
            "status",
            "reconciliation_path",
        }
        assert "Interview opportunity" not in str(attempt.payload_summary)
        audit_event = session.scalar(
            select(AuditEvent).where(
                AuditEvent.event_type == "gmail.knowledge_question_pending"
            )
        )
        assert audit_event is not None
        assert "Interview opportunity" not in str(audit_event.metadata_json)
