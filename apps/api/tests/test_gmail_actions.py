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
from atlas_api.models.gmail_message import GmailActionOperation
from atlas_api.models.idempotency import ApiIdempotencyRecord
from atlas_api.services.connectors import (
    DRIVE_SCOPE_FILE,
    GMAIL_SCOPE_MODIFY,
    ensure_default_connector_types,
)
from atlas_api.services.gmail_actions import (
    FakeDriveProvider,
    FakeGmailActionProvider,
    GmailLowRiskActionPolicy,
    execute_low_risk_mailbox_actions,
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


def seed_connection(
    session: Session,
    *,
    connector_type: str,
    scope: str,
    account_identifier: str,
) -> str:
    seed_owner(session)
    ensure_default_connector_types(session)
    credential = ConnectorCredentialReference(
        owner_user_id=OWNER_ID,
        connector_type=connector_type,
        reference_label=f"{connector_type}:oauth:ref",
        key_version="local-fake-v1",
        status="active",
    )
    session.add(credential)
    session.flush()
    connection = ConnectorConnection(
        owner_user_id=OWNER_ID,
        connector_type=connector_type,
        display_name=connector_type,
        account_identifier=account_identifier,
        status="connected",
        granted_scopes=[scope],
        credential_reference_id=credential.credential_reference_id,
        health_status="healthy",
    )
    session.add(connection)
    session.flush()
    connection_id = connection.connection_id
    session.commit()
    return connection_id


def seed_classified_message(
    session: Session,
    *,
    connection_id: str,
    provider_message_reference: str = "msg-receipt",
    sender: str = "store@example.test",
    subject: str = "Your receipt",
    snippet: str = "Receipt for order 123.",
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
                attachments=(
                    FakeGmailAttachment(
                        provider_attachment_reference="att-receipt",
                        filename="receipt.pdf",
                        mime_type="application/pdf",
                        size_bytes=1234,
                    ),
                ),
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


def receipt_policy() -> GmailLowRiskActionPolicy:
    return GmailLowRiskActionPolicy(
        label_by_category={"Receipts": "Atlas/Receipts"},
        archive_categories=frozenset({"Receipts"}),
        attachment_save_categories=frozenset({"Receipts"}),
        drive_folder_reference="drive-folder-receipts",
    )


def test_low_risk_actions_are_idempotent_and_minimized(
    database_factory: sessionmaker[Session],
) -> None:
    gmail_provider = FakeGmailActionProvider(attachments={"att-receipt": b"pdf bytes"})
    drive_provider = FakeDriveProvider()
    with database_factory() as session:
        gmail_connection_id = seed_connection(
            session,
            connector_type="gmail",
            scope=GMAIL_SCOPE_MODIFY,
            account_identifier="owner@example.test",
        )
        drive_connection_id = seed_connection(
            session,
            connector_type="google_drive",
            scope=DRIVE_SCOPE_FILE,
            account_identifier="owner-drive@example.test",
        )
        message_id = seed_classified_message(
            session,
            connection_id=gmail_connection_id,
        )

        first = execute_low_risk_mailbox_actions(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            gmail_provider=gmail_provider,
            drive_provider=drive_provider,
            policy=receipt_policy(),
            idempotency_key_prefix="receipt-action-1",
            drive_connection_id=drive_connection_id,
            correlation_id="corr-actions",
        )
        second = execute_low_risk_mailbox_actions(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            gmail_provider=gmail_provider,
            drive_provider=drive_provider,
            policy=receipt_policy(),
            idempotency_key_prefix="receipt-action-1",
            drive_connection_id=drive_connection_id,
            correlation_id="corr-actions",
        )
        session.commit()

    assert [item.operation_type for item in first.operations] == [
        "gmail.apply_label",
        "gmail.archive_message",
        "gmail.get_attachment",
        "drive.save_attachment",
    ]
    assert first.denied_count == 0
    assert first.replayed_count == 0
    assert second.replayed_count == 4
    assert gmail_provider.applied_labels == [("msg-receipt", "Atlas/Receipts")]
    assert gmail_provider.archived_messages == ["msg-receipt"]
    assert gmail_provider.retrieved_attachments == [("msg-receipt", "att-receipt")]
    assert len(drive_provider.saved_attachments) == 1
    with database_factory() as session:
        operations = list(session.scalars(select(GmailActionOperation)))
        idempotency_records = list(session.scalars(select(ApiIdempotencyRecord)))
        assert len(operations) == 4
        assert len(idempotency_records) == 4
        assert {item.status for item in operations} == {"succeeded"}
        assert "pdf bytes" not in str([item.metadata_json for item in operations])
        assert session.scalar(
            select(AuditEvent).where(AuditEvent.event_type == "gmail.low_risk_action")
        )


def test_policy_denial_records_no_provider_side_effect(
    database_factory: sessionmaker[Session],
) -> None:
    gmail_provider = FakeGmailActionProvider()
    drive_provider = FakeDriveProvider()
    with database_factory() as session:
        gmail_connection_id = seed_connection(
            session,
            connector_type="gmail",
            scope=GMAIL_SCOPE_MODIFY,
            account_identifier="owner@example.test",
        )
        message_id = seed_classified_message(
            session,
            connection_id=gmail_connection_id,
            provider_message_reference="msg-recruiter",
            sender="recruiter@example.test",
            subject="Interview opportunity",
            snippet="Following up about the role.",
        )

        result = execute_low_risk_mailbox_actions(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            gmail_provider=gmail_provider,
            drive_provider=drive_provider,
            policy=receipt_policy(),
            idempotency_key_prefix="policy-denied-1",
        )
        session.commit()

    assert result.denied_count == 1
    assert not gmail_provider.applied_labels
    with database_factory() as session:
        operation = session.scalar(select(GmailActionOperation))
        assert operation is not None
        assert operation.status == "denied"
        assert operation.reason_code == "gmail_action_policy_denied"


def test_suppressed_message_denial_is_recorded_before_error(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        gmail_connection_id = seed_connection(
            session,
            connector_type="gmail",
            scope=GMAIL_SCOPE_MODIFY,
            account_identifier="owner@example.test",
        )
        message_id = seed_classified_message(
            session,
            connection_id=gmail_connection_id,
            provider_message_reference="msg-clinical",
            sender="clinic@example.test",
            subject="Clinic appointment",
            snippet="Appointment reminder.",
        )

        with pytest.raises(ApiError) as blocked:
            execute_low_risk_mailbox_actions(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=message_id,
                gmail_provider=FakeGmailActionProvider(),
                drive_provider=FakeDriveProvider(),
                policy=receipt_policy(),
                idempotency_key_prefix="suppressed-denied-1",
            )
        session.commit()

    assert blocked.value.code == "gmail_message_suppressed"
    with database_factory() as session:
        operation = session.scalar(select(GmailActionOperation))
        assert operation is not None
        assert operation.status == "denied"
        assert operation.reason_code == "gmail_message_suppressed"


def test_provider_failure_is_normalized_and_replayable(
    database_factory: sessionmaker[Session],
) -> None:
    gmail_provider = FakeGmailActionProvider(fail_operations={"gmail.archive_message"})
    with database_factory() as session:
        gmail_connection_id = seed_connection(
            session,
            connector_type="gmail",
            scope=GMAIL_SCOPE_MODIFY,
            account_identifier="owner@example.test",
        )
        message_id = seed_classified_message(
            session,
            connection_id=gmail_connection_id,
        )
        policy = GmailLowRiskActionPolicy(
            label_by_category={},
            archive_categories=frozenset({"Receipts"}),
            attachment_save_categories=frozenset(),
        )

        first = execute_low_risk_mailbox_actions(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            gmail_provider=gmail_provider,
            drive_provider=FakeDriveProvider(),
            policy=policy,
            idempotency_key_prefix="archive-failure-1",
        )
        second = execute_low_risk_mailbox_actions(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            gmail_provider=gmail_provider,
            drive_provider=FakeDriveProvider(),
            policy=policy,
            idempotency_key_prefix="archive-failure-1",
        )
        session.commit()

    assert first.operations[0].status == "failed"
    assert first.operations[0].reason_code == "gmail.archive_message.provider_failed"
    assert second.replayed_count == 1
    assert gmail_provider.archived_messages == []


def test_attachment_save_requires_drive_connection(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        gmail_connection_id = seed_connection(
            session,
            connector_type="gmail",
            scope=GMAIL_SCOPE_MODIFY,
            account_identifier="owner@example.test",
        )
        message_id = seed_classified_message(
            session,
            connection_id=gmail_connection_id,
        )
        policy = GmailLowRiskActionPolicy(
            label_by_category={},
            archive_categories=frozenset(),
            attachment_save_categories=frozenset({"Receipts"}),
            drive_folder_reference="drive-folder-receipts",
        )

        result = execute_low_risk_mailbox_actions(
            session,
            owner_user_id=OWNER_ID,
            gmail_message_record_id=message_id,
            gmail_provider=FakeGmailActionProvider(),
            drive_provider=FakeDriveProvider(),
            policy=policy,
            idempotency_key_prefix="drive-denied-1",
        )
        session.commit()

    assert result.denied_count == 1
    with database_factory() as session:
        operations = list(session.scalars(select(GmailActionOperation)))
        assert [item.operation_type for item in operations] == [
            "gmail.get_attachment",
            "drive.save_attachment",
        ]
        assert operations[1].status == "denied"
        assert operations[1].reason_code == "drive_connection_required"
