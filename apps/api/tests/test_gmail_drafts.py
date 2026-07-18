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
from atlas_api.models.gmail_message import GmailDraftRecord
from atlas_api.models.idempotency import ApiIdempotencyRecord
from atlas_api.models.knowledge import KnowledgeQuestion
from atlas_api.services.connectors import (
    GMAIL_SCOPE_MODIFY,
    ensure_default_connector_types,
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


def seed_message(
    session: Session,
    *,
    connection_id: str,
    sender: str = "recruiter@example.test",
    subject: str = "Interview opportunity",
    snippet: str = "Following up about the platform role.",
    provider_message_reference: str = "msg-recruiter",
) -> str:
    result = retrieve_and_classify_messages(
        session,
        owner_user_id=OWNER_ID,
        connection_id=connection_id,
        provider=FakeGmailProvider(
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
        ),
        policy=GmailRetrievalPolicy(max_messages=10),
    )
    session.commit()
    return result.records[0].gmail_message_record_id


def seed_required_facts(session: Session) -> list[str]:
    revision_ids: list[str] = []
    for fact_key, value, volatile in (
        ("gmail.reply.availability", "Tuesday afternoon.", True),
        ("gmail.reply.role_preferences", "Platform architecture roles.", False),
    ):
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
        revision_ids.append(revision.knowledge_fact_revision_id)
    session.commit()
    return revision_ids


def valid_generator() -> FakeDraftGenerator:
    return FakeDraftGenerator(
        GeneratedDraftOutput(
            subject="Re: Interview opportunity",
            body="Thanks for reaching out. Tuesday afternoon works for me.",
        )
    )


def test_successful_draft_creation_binds_facts_and_never_sends(
    database_factory: sessionmaker[Session],
) -> None:
    provider = FakeGmailDraftProvider()
    with database_factory() as session:
        connection_id = seed_connection(session)
        message_id = seed_message(session, connection_id=connection_id)
        revision_ids = seed_required_facts(session)

        result = create_gmail_draft(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            scenario="recruiter_reply",
            generator=valid_generator(),
            provider=provider,
            idempotency_key="draft-create-key-1",
            correlation_id="corr-draft",
        )
        session.commit()

    assert result.replayed is False
    assert provider.created_drafts
    assert not provider.sent_messages
    draft = result.draft
    assert draft.status == "created"
    assert draft.body_hash
    assert set(item["knowledge_fact_revision_id"] for item in draft.facts_used) == set(
        revision_ids
    )
    assert "fact_revision_bindings" in draft.decision_context_manifest
    assert "Tuesday afternoon works" not in str(draft.evidence_summary)
    with database_factory() as session:
        assert session.scalar(select(GmailDraftRecord)) is not None
        assert not list(session.scalars(select(ApprovalRequest)))


def test_missing_facts_deny_draft_and_create_questions(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_connection(session)
        message_id = seed_message(session, connection_id=connection_id)

        with pytest.raises(ApiError) as denied:
            create_gmail_draft(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=message_id,
                scenario="recruiter_reply",
                generator=valid_generator(),
                provider=FakeGmailDraftProvider(),
                idempotency_key="draft-missing-key-1",
                correlation_id="corr-missing",
            )
        session.commit()

    assert denied.value.code == "gmail_required_facts_missing"
    with database_factory() as session:
        assert len(list(session.scalars(select(KnowledgeQuestion)))) == 2
        assert not list(session.scalars(select(GmailDraftRecord)))


def test_generated_draft_output_prohibited_content_is_rejected(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_connection(session)
        message_id = seed_message(session, connection_id=connection_id)
        seed_required_facts(session)

        with pytest.raises(ApiError) as rejected:
            create_gmail_draft(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=message_id,
                scenario="recruiter_reply",
                generator=FakeDraftGenerator(
                    GeneratedDraftOutput(
                        subject="Re: Interview",
                        body="Use access_token abc123.",
                    )
                ),
                provider=FakeGmailDraftProvider(),
                idempotency_key="draft-prohibited-key-1",
                correlation_id="corr-prohibited",
            )

    assert rejected.value.code == "gmail_draft_prohibited_content"


def test_suppressed_source_cannot_create_draft(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_connection(session)
        message_id = seed_message(
            session,
            connection_id=connection_id,
            sender="clinic@example.test",
            subject="Clinic appointment",
            snippet="Appointment reminder.",
            provider_message_reference="msg-clinical",
        )
        seed_required_facts(session)

        with pytest.raises(ApiError) as blocked:
            create_gmail_draft(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=message_id,
                scenario="recruiter_reply",
                generator=valid_generator(),
                provider=FakeGmailDraftProvider(),
                idempotency_key="draft-suppressed-key-1",
                correlation_id="corr-suppressed",
            )

    assert blocked.value.code == "gmail_message_suppressed"


def test_draft_creation_is_idempotent(
    database_factory: sessionmaker[Session],
) -> None:
    provider = FakeGmailDraftProvider()
    generator = valid_generator()
    with database_factory() as session:
        connection_id = seed_connection(session)
        message_id = seed_message(session, connection_id=connection_id)
        seed_required_facts(session)

        first = create_gmail_draft(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            scenario="recruiter_reply",
            generator=generator,
            provider=provider,
            idempotency_key="draft-idempotent-key-1",
            correlation_id="corr-idem",
        )
        second = create_gmail_draft(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            scenario="recruiter_reply",
            generator=generator,
            provider=provider,
            idempotency_key="draft-idempotent-key-1",
            correlation_id="corr-idem",
        )
        session.commit()

    assert first.draft.gmail_draft_record_id == second.draft.gmail_draft_record_id
    assert second.replayed is True
    assert len(provider.created_drafts) == 1
    assert len(generator.calls) == 1
    with database_factory() as session:
        assert len(list(session.scalars(select(ApiIdempotencyRecord)))) == 1


def test_provider_failure_is_normalized_and_audited(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_connection(session)
        message_id = seed_message(session, connection_id=connection_id)
        seed_required_facts(session)

        with pytest.raises(ApiError) as failed:
            create_gmail_draft(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=message_id,
                scenario="recruiter_reply",
                generator=valid_generator(),
                provider=FakeGmailDraftProvider(fail=True),
                idempotency_key="draft-provider-failed-1",
                correlation_id="corr-provider",
            )
        session.commit()

    assert failed.value.code == "gmail.create_draft.provider_failed"
    with database_factory() as session:
        audit = session.scalar(
            select(AuditEvent).where(AuditEvent.result == "failed")
        )
        assert audit is not None
        assert audit.reason_code == "gmail.create_draft.provider_failed"
