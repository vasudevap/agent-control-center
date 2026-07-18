from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.errors import ApiError
from atlas_api.db.base import Base
from atlas_api.models.audit import AuditEvent
from atlas_api.models.connector import (
    ConnectorConnection,
    ConnectorCredentialReference,
)
from atlas_api.models.external_client import User
from atlas_api.models.gmail_message import GmailMessageRecord
from atlas_api.services.connectors import (
    GMAIL_SCOPE_MODIFY,
    ensure_default_connector_types,
)
from atlas_api.services.gmail_messages import (
    FakeGmailAttachment,
    FakeGmailMessage,
    FakeGmailProvider,
    GmailRetrievalPolicy,
    retrieve_and_classify_messages,
)

OWNER_ID = "usr_owner"


@pytest.fixture
def database_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine)


def seed_gmail_connection(
    session: Session,
    *,
    status: str = "connected",
    scopes: list[str] | None = None,
    account_identifier: str = "owner@example.test",
) -> str:
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
        account_identifier=account_identifier,
        status=status,
        granted_scopes=scopes if scopes is not None else [GMAIL_SCOPE_MODIFY],
        credential_reference_id=credential.credential_reference_id,
        health_status="healthy" if status == "connected" else "revoked",
    )
    session.add(connection)
    session.flush()
    connection_id = connection.connection_id
    session.commit()
    return connection_id


def message(
    provider_message_reference: str,
    *,
    sender: str,
    subject: str,
    snippet: str,
    query: str = "in:inbox",
) -> FakeGmailMessage:
    return FakeGmailMessage(
        provider_message_reference=provider_message_reference,
        provider_thread_reference=f"thread-{provider_message_reference}",
        sender_address=sender,
        subject=subject,
        snippet=snippet,
        label_names=("INBOX",),
        received_at=datetime(2026, 7, 18, 12, 0, tzinfo=UTC),
        eligible_queries=(query,),
        attachments=(
            FakeGmailAttachment(
                provider_attachment_reference=f"att-{provider_message_reference}",
                filename="receipt.pdf",
                mime_type="application/pdf",
                size_bytes=1234,
            ),
        ),
    )


def test_gmail_message_record_schema_avoids_full_body_storage() -> None:
    table = Base.metadata.tables["gmail_message_records"]

    assert "subject_preview" in table.c
    assert "content_excerpt_hash" in table.c
    assert "attachment_metadata" in table.c
    assert "body" not in table.c
    assert "full_body" not in table.c
    assert "raw_content" not in table.c


def test_retrieve_and_classify_eligible_messages_with_minimized_persistence(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        provider = FakeGmailProvider(
            [
                message(
                    "msg-1",
                    sender="store@example.test",
                    subject="Your receipt",
                    snippet="Receipt for order 123.",
                ),
                message(
                    "msg-2",
                    sender="recruiter@example.test",
                    subject="Interview opportunity",
                    snippet="Following up about the platform role.",
                ),
                message(
                    "msg-3",
                    sender="friend@gmail.com",
                    subject="Coffee",
                    snippet="Want to catch up?",
                ),
                message(
                    "msg-4",
                    sender="clinic@example.test",
                    subject="Clinic appointment",
                    snippet="Appointment reminder.",
                ),
                message(
                    "msg-5",
                    sender="other@example.test",
                    subject="Outside query",
                    snippet="Should not be retrieved.",
                    query="label:later",
                ),
            ]
        )

        result = retrieve_and_classify_messages(
            session,
            owner_user_id=OWNER_ID,
            connection_id=connection_id,
            provider=provider,
            policy=GmailRetrievalPolicy(eligibility_query="in:inbox", max_messages=10),
        )
        categories = [record.classification_category for record in result.records]
        session.commit()

    assert result.skipped_count == 0
    assert categories == [
        "Receipts",
        "Recruiters",
        "Review Required",
        "Clinical",
    ]
    with database_factory() as session:
        rows = list(session.scalars(select(GmailMessageRecord)))
        assert len(rows) == 4
        assert {row.provider_message_reference for row in rows} == {
            "msg-1",
            "msg-2",
            "msg-3",
            "msg-4",
        }
        friend = next(row for row in rows if row.provider_message_reference == "msg-3")
        assert friend.review_reason_code == "classification_confidence_low"
        assert friend.content_excerpt_hash != "Want to catch up?"
        assert rows[0].attachment_metadata[0]["filename"] == "receipt.pdf"
        audit_event = session.scalar(
            select(AuditEvent).where(AuditEvent.action == "retrieve_and_classify")
        )
        assert audit_event is not None
        assert audit_event.metadata_json["count"] == 4


def test_retrieval_upserts_existing_provider_message(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        first_provider = FakeGmailProvider(
            [
                message(
                    "msg-1",
                    sender="store@example.test",
                    subject="Your receipt",
                    snippet="Receipt for order 123.",
                )
            ]
        )
        retrieve_and_classify_messages(
            session,
            owner_user_id=OWNER_ID,
            connection_id=connection_id,
            provider=first_provider,
            policy=GmailRetrievalPolicy(),
        )
        second_provider = FakeGmailProvider(
            [
                message(
                    "msg-1",
                    sender="store@example.test",
                    subject="Your updated receipt",
                    snippet="Receipt for updated order.",
                )
            ]
        )
        retrieve_and_classify_messages(
            session,
            owner_user_id=OWNER_ID,
            connection_id=connection_id,
            provider=second_provider,
            policy=GmailRetrievalPolicy(),
        )
        session.commit()

    with database_factory() as session:
        rows = list(session.scalars(select(GmailMessageRecord)))
        assert len(rows) == 1
        assert rows[0].subject_preview == "Your updated receipt"


def test_retrieval_requires_connected_gmail_scope(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        revoked_connection_id = seed_gmail_connection(
            session,
            status="revoked",
            account_identifier="revoked@example.test",
        )
        provider = FakeGmailProvider([])
        with pytest.raises(ApiError) as revoked:
            retrieve_and_classify_messages(
                session,
                owner_user_id=OWNER_ID,
                connection_id=revoked_connection_id,
                provider=provider,
                policy=GmailRetrievalPolicy(),
            )
        assert revoked.value.code == "connector_not_connected"

    with database_factory() as session:
        missing_scope_id = seed_gmail_connection(
            session,
            scopes=[],
            account_identifier="missing-scope@example.test",
        )
        with pytest.raises(ApiError) as missing_scope:
            retrieve_and_classify_messages(
                session,
                owner_user_id=OWNER_ID,
                connection_id=missing_scope_id,
                provider=FakeGmailProvider([]),
                policy=GmailRetrievalPolicy(),
            )
        assert missing_scope.value.code == "connector_scope_missing"
