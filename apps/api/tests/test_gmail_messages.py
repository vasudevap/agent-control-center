from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.core.events import WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING
from atlas_api.db.base import Base
from atlas_api.models.approval import ManualHandlingRecord
from atlas_api.models.audit import AuditEvent
from atlas_api.models.connector import (
    ConnectorConnection,
    ConnectorCredentialReference,
)
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.gmail_message import GmailMessageRecord
from atlas_api.models.webhook import WebhookDeliveryAttempt, WebhookSubscription
from atlas_api.services.connectors import (
    GMAIL_SCOPE_MODIFY,
    ensure_default_connector_types,
)
from atlas_api.services.gmail_messages import (
    FakeGmailAttachment,
    FakeGmailMessage,
    FakeGmailProvider,
    GmailRetrievalPolicy,
    GmailSuppressionWebhookContext,
    SuppressionDecision,
    ensure_gmail_message_allowed_for_downstream_use,
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
            select(AuditEvent).where(
                AuditEvent.event_type == "gmail.messages_retrieved"
            )
        )
        assert audit_event is not None
        assert audit_event.metadata_json["count"] == 4
        assert audit_event.metadata_json["suppressed_count"] == 1


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


def test_clinical_and_phi_messages_are_suppressed_before_persistence(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        provider = FakeGmailProvider(
            [
                message(
                    "msg-clinical",
                    sender="clinic@example.test",
                    subject="Clinic appointment with Dr Smith",
                    snippet="Appointment reminder with diagnosis notes.",
                ),
                message(
                    "msg-phi",
                    sender="benefits@example.test",
                    subject="Patient ID update",
                    snippet="Protected health information enclosed.",
                ),
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

    assert result.suppressed_count == 2
    with database_factory() as session:
        rows = list(session.scalars(select(GmailMessageRecord)))
        manual_records = list(session.scalars(select(ManualHandlingRecord)))
        assert len(manual_records) == 2
        for row in rows:
            assert row.suppression_status == "suppressed"
            assert row.manual_handling_id is not None
            assert row.subject_preview == "[suppressed]"
            assert row.sender_address == "suppressed@example.invalid"
            assert row.sender_domain == "suppressed.invalid"
            assert row.label_names == ["SUPPRESSED"]
            assert row.attachment_metadata[0]["filename"] == "[suppressed]"
            assert "Clinic appointment" not in row.content_excerpt_hash
        for manual in manual_records:
            assert manual.source_reference.startswith("gmail:msg-")
            assert manual.sensitivity_classification == "restricted"
            assert set(manual.metadata_json) == {
                "connector_type",
                "connection_id",
                "provider_message_reference",
                "provider_thread_reference",
                "suppression_reason_code",
            }
            assert "Clinic appointment" not in str(manual.metadata_json)
        suppression_audits = list(
            session.scalars(select(AuditEvent).where(AuditEvent.action == "suppress"))
        )
        assert len(suppression_audits) == 2
        assert all(
            "Clinic appointment" not in str(item.metadata_json)
            for item in suppression_audits
        )


def test_suppression_detector_schema_fails_closed_to_manual_handling(
    database_factory: sessionmaker[Session],
) -> None:
    def invalid_detector(
        _message: FakeGmailMessage,
        _classification: object,
    ) -> SuppressionDecision:
        return SuppressionDecision(
            is_suppressed=True,
            reason_category="Unexpected",
            sensitivity_classification="standard",
            reason_code="bad_reason",
        )

    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        provider = FakeGmailProvider(
            [
                message(
                    "msg-ordinary",
                    sender="store@example.test",
                    subject="Your receipt",
                    snippet="Receipt for order 123.",
                )
            ]
        )

        result = retrieve_and_classify_messages(
            session,
            owner_user_id=OWNER_ID,
            connection_id=connection_id,
            provider=provider,
            policy=GmailRetrievalPolicy(),
            suppression_detector=invalid_detector,
        )
        session.commit()

    assert result.suppressed_count == 1
    with database_factory() as session:
        record = session.scalar(select(GmailMessageRecord))
        manual = session.scalar(select(ManualHandlingRecord))
        assert record is not None
        assert manual is not None
        assert record.suppression_status == "suppressed"
        assert record.suppression_reason_code == "suppression_detector_invalid"
        assert manual.reason_category == "ProtectedHealthInformation"


def test_suppressed_messages_cannot_enter_any_downstream_path(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        provider = FakeGmailProvider(
            [
                message(
                    "msg-clinical",
                    sender="clinic@example.test",
                    subject="Clinic appointment",
                    snippet="Appointment reminder.",
                )
            ]
        )
        result = retrieve_and_classify_messages(
            session,
            owner_user_id=OWNER_ID,
            connection_id=connection_id,
            provider=provider,
            policy=GmailRetrievalPolicy(),
        )
        record_id = result.records[0].gmail_message_record_id

        for downstream_use in (
            "knowledge",
            "question",
            "draft",
            "approval",
            "action",
            "send",
            "learning",
        ):
            with pytest.raises(ApiError) as blocked:
                ensure_gmail_message_allowed_for_downstream_use(
                    session,
                    owner_user_id=OWNER_ID,
                    gmail_message_record_id=record_id,
                    downstream_use=downstream_use,
                )
            assert blocked.value.code == "gmail_message_suppressed"
            assert blocked.value.details is not None
            assert blocked.value.details["downstream_use"] == downstream_use

        not_suppressed = list(
            session.scalars(
                select(GmailMessageRecord).where(
                    GmailMessageRecord.suppression_status == "not_suppressed"
                )
            )
        )
        assert not not_suppressed


def test_review_required_message_is_not_allowed_downstream(
    database_factory: sessionmaker[Session],
) -> None:
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
        provider = FakeGmailProvider(
            [
                message(
                    "msg-friend",
                    sender="friend@gmail.com",
                    subject="Coffee",
                    snippet="Want to catch up?",
                )
            ]
        )
        result = retrieve_and_classify_messages(
            session,
            owner_user_id=OWNER_ID,
            connection_id=connection_id,
            provider=provider,
            policy=GmailRetrievalPolicy(),
        )
        record_id = result.records[0].gmail_message_record_id

        with pytest.raises(ApiError) as blocked:
            ensure_gmail_message_allowed_for_downstream_use(
                session,
                owner_user_id=OWNER_ID,
                gmail_message_record_id=record_id,
                downstream_use="draft",
            )

        assert blocked.value.code == "gmail_message_requires_manual_review"


def test_suppression_enqueues_minimized_manual_handling_webhook(
    database_factory: sessionmaker[Session],
) -> None:
    settings = Settings(
        environment="test",
        webhook_signing_key_id="current",
        webhook_signing_secret=SecretStr("webhook-secret"),
    )
    with database_factory() as session:
        connection_id = seed_gmail_connection(session)
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
                event_type=WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING,
                target_url="https://client.example.test/webhooks/atlas",
                secret_reference="webhook-secret-ref",
                status="active",
            )
        )
        provider = FakeGmailProvider(
            [
                message(
                    "msg-phi",
                    sender="clinic@example.test",
                    subject="Patient ID update",
                    snippet="Protected health information enclosed.",
                )
            ]
        )

        retrieve_and_classify_messages(
            session,
            owner_user_id=OWNER_ID,
            connection_id=connection_id,
            provider=provider,
            policy=GmailRetrievalPolicy(),
            correlation_id="corr-suppression",
            webhook_context=GmailSuppressionWebhookContext(
                settings=settings,
                correlation_id="corr-suppression",
                now=datetime(2026, 7, 18, 13, 0, tzinfo=UTC),
            ),
        )
        session.commit()

    with database_factory() as session:
        attempt = session.scalar(select(WebhookDeliveryAttempt))
        assert attempt is not None
        assert attempt.event_type == WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING
        assert set(attempt.payload_summary) == {
            "reason_category",
            "resource_id",
            "resource_type",
            "sensitivity_classification",
            "status",
            "reconciliation_path",
        }
        assert "Patient ID" not in str(attempt.payload_summary)
        webhook_audit = session.scalar(
            select(AuditEvent).where(AuditEvent.actor_id == "webhook_delivery")
        )
        assert webhook_audit is not None
        assert webhook_audit.metadata_json["status"] == "pending"
