from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.connector import ConnectorConnection
from atlas_api.models.gmail_message import GmailMessageRecord
from atlas_api.services.approval_contracts import create_manual_handling_record
from atlas_api.services.audit import (
    AuditEventInput,
    record_audit_event,
    record_webhook_audit_event,
)
from atlas_api.services.connectors import GMAIL_SCOPE_MODIFY
from atlas_api.services.platform_events import (
    enqueue_platform_webhook_event,
    message_held_for_manual_handling_event,
)

GMAIL_AGENT_ID = "gmail-agent"
MIN_CLASSIFICATION_CONFIDENCE = 60
MAX_SUBJECT_PREVIEW_LENGTH = 240
SUPPRESSED_VALUE = "[suppressed]"
SUPPRESSION_STATUS_NOT_SUPPRESSED = "not_suppressed"
SUPPRESSION_STATUS_SUPPRESSED = "suppressed"
SUPPRESSION_REASON_CLINICAL = "clinical_source_suppressed"
SUPPRESSION_REASON_PHI = "protected_health_information_suppressed"
SUPPRESSION_REASON_DETECTOR_INVALID = "suppression_detector_invalid"
GMAIL_DOWNSTREAM_USES = frozenset(
    {"knowledge", "question", "draft", "approval", "action", "send", "learning"}
)

GMAIL_CLASSIFICATION_CATEGORIES = frozenset(
    {
        "Family",
        "Friends",
        "Work",
        "Recruiters",
        "Shopping",
        "Subscriptions",
        "Receipts",
        "Travel",
        "Personal Administration",
        "Needs Reply",
        "Review Required",
        "Unknown",
        "Clinical",
        "Protected Health Information",
    }
)

_CLINICAL_PATTERN = re.compile(
    r"\b(appointment|clinic|doctor|diagnosis|laboratory|prescription)\b",
    re.IGNORECASE,
)
_PHI_PATTERN = re.compile(
    r"\b(protected health|patient id|medical record|health card|\bphi\b)\b",
    re.IGNORECASE,
)
_RECEIPT_PATTERN = re.compile(r"\b(receipt|invoice|order|payment)\b", re.IGNORECASE)
_SHOPPING_PATTERN = re.compile(r"\b(shipping|delivered|cart|sale)\b", re.IGNORECASE)
_TRAVEL_PATTERN = re.compile(r"\b(flight|hotel|itinerary|boarding)\b", re.IGNORECASE)
_RECRUITER_PATTERN = re.compile(
    r"\b(recruiter|opportunity|interview|role|position)\b",
    re.IGNORECASE,
)
_SUBSCRIPTION_PATTERN = re.compile(
    r"\b(newsletter|unsubscribe|subscription|digest)\b",
    re.IGNORECASE,
)
_NEEDS_REPLY_PATTERN = re.compile(
    r"\b(can you|could you|please reply|question|follow up)\b",
    re.IGNORECASE,
)
_ADMIN_PATTERN = re.compile(
    r"\b(statement|insurance|tax|account|renewal)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FakeGmailAttachment:
    provider_attachment_reference: str
    filename: str
    mime_type: str
    size_bytes: int


@dataclass(frozen=True)
class FakeGmailMessage:
    provider_message_reference: str
    provider_thread_reference: str
    sender_address: str
    subject: str
    snippet: str
    label_names: tuple[str, ...]
    received_at: datetime
    eligible_queries: tuple[str, ...] = ("in:inbox",)
    attachments: tuple[FakeGmailAttachment, ...] = ()


@dataclass(frozen=True)
class GmailRetrievalPolicy:
    eligibility_query: str = "in:inbox"
    max_messages: int = 25


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    confidence: int
    status: str
    review_reason_code: str | None


@dataclass(frozen=True)
class SuppressionDecision:
    is_suppressed: bool
    reason_category: str | None
    sensitivity_classification: str
    reason_code: str | None


@dataclass(frozen=True)
class GmailRetrievalResult:
    records: list[GmailMessageRecord]
    skipped_count: int
    suppressed_count: int


@dataclass(frozen=True)
class GmailSuppressionWebhookContext:
    settings: Settings
    correlation_id: str
    now: datetime | None = None


SuppressionDetector = Callable[
    [FakeGmailMessage, ClassificationResult],
    SuppressionDecision,
]


class FakeGmailProvider:
    def __init__(self, messages: list[FakeGmailMessage]) -> None:
        self._messages = messages

    def list_message_references(self, *, query: str, max_results: int) -> list[str]:
        return [
            message.provider_message_reference
            for message in self._messages
            if query in message.eligible_queries
        ][:max_results]

    def get_message(self, provider_message_reference: str) -> FakeGmailMessage:
        for message in self._messages:
            if message.provider_message_reference == provider_message_reference:
                return message
        raise ApiError(404, "gmail_message_not_found", "Gmail message was not found.")


def retrieve_and_classify_messages(
    session: Session,
    *,
    owner_user_id: str,
    connection_id: str,
    provider: FakeGmailProvider,
    policy: GmailRetrievalPolicy,
    actor_id: str = GMAIL_AGENT_ID,
    correlation_id: str | None = None,
    suppression_detector: SuppressionDetector | None = None,
    webhook_context: GmailSuppressionWebhookContext | None = None,
) -> GmailRetrievalResult:
    _validate_policy(policy)
    connection = _require_gmail_connection(
        session,
        owner_user_id=owner_user_id,
        connection_id=connection_id,
    )
    references = provider.list_message_references(
        query=policy.eligibility_query,
        max_results=policy.max_messages,
    )
    records: list[GmailMessageRecord] = []
    skipped_count = 0
    suppressed_count = 0
    for reference in references:
        try:
            message = provider.get_message(reference)
        except ApiError:
            skipped_count += 1
            continue
        record = _upsert_message_record(
            session,
            owner_user_id=owner_user_id,
            connection=connection,
            message=message,
            eligibility_reason=f"query:{policy.eligibility_query}",
            actor_id=actor_id,
            correlation_id=correlation_id,
            suppression_detector=suppression_detector or detect_message_suppression,
            webhook_context=webhook_context,
        )
        if record.suppression_status == SUPPRESSION_STATUS_SUPPRESSED:
            suppressed_count += 1
        records.append(record)
    record_audit_event(
        session,
        AuditEventInput(
            event_type="gmail.messages_retrieved",
            actor_type="service",
            actor_id=actor_id,
            channel="service",
            action="retrieve_and_classify",
            resource_type="gmail_message",
            resource_id=connection.connection_id,
            result="succeeded",
            correlation_id=correlation_id,
            metadata={
                "connector_type": "gmail",
                "connection_id": connection.connection_id,
                "count": len(records),
                "skipped_count": skipped_count,
                "suppressed_count": suppressed_count,
            },
        ),
    )
    session.flush()
    return GmailRetrievalResult(
        records=records,
        skipped_count=skipped_count,
        suppressed_count=suppressed_count,
    )


def classify_message(message: FakeGmailMessage) -> ClassificationResult:
    text = f"{message.sender_address} {message.subject} {message.snippet}"
    category = "Unknown"
    confidence = 40
    if _PHI_PATTERN.search(text):
        category = "Protected Health Information"
        confidence = 95
    elif _CLINICAL_PATTERN.search(text):
        category = "Clinical"
        confidence = 90
    elif _RECRUITER_PATTERN.search(text):
        category = "Recruiters"
        confidence = 78
    elif _TRAVEL_PATTERN.search(text):
        category = "Travel"
        confidence = 82
    elif _RECEIPT_PATTERN.search(text):
        category = "Receipts"
        confidence = 80
    elif _SUBSCRIPTION_PATTERN.search(text):
        category = "Subscriptions"
        confidence = 76
    elif _SHOPPING_PATTERN.search(text):
        category = "Shopping"
        confidence = 72
    elif _NEEDS_REPLY_PATTERN.search(text):
        category = "Needs Reply"
        confidence = 70
    elif _ADMIN_PATTERN.search(text):
        category = "Personal Administration"
        confidence = 68
    elif _sender_domain(message.sender_address) in {"gmail.com", "icloud.com"}:
        category = "Friends"
        confidence = 55
    result = _validated_classification(category=category, confidence=confidence)
    if result.confidence < MIN_CLASSIFICATION_CONFIDENCE:
        return ClassificationResult(
            category="Review Required",
            confidence=result.confidence,
            status="review_required",
            review_reason_code="classification_confidence_low",
        )
    return result


def detect_message_suppression(
    message: FakeGmailMessage,
    classification: ClassificationResult,
) -> SuppressionDecision:
    text = f"{message.sender_address} {message.subject} {message.snippet}"
    if (
        classification.category == "Protected Health Information"
        or _PHI_PATTERN.search(text)
    ):
        return SuppressionDecision(
            is_suppressed=True,
            reason_category="ProtectedHealthInformation",
            sensitivity_classification="restricted",
            reason_code=SUPPRESSION_REASON_PHI,
        )
    if classification.category == "Clinical" or _CLINICAL_PATTERN.search(text):
        return SuppressionDecision(
            is_suppressed=True,
            reason_category="Clinical",
            sensitivity_classification="restricted",
            reason_code=SUPPRESSION_REASON_CLINICAL,
        )
    return SuppressionDecision(
        is_suppressed=False,
        reason_category=None,
        sensitivity_classification="standard",
        reason_code=None,
    )


def ensure_gmail_message_allowed_for_downstream_use(
    session: Session,
    *,
    owner_user_id: str,
    gmail_message_record_id: str,
    downstream_use: str,
) -> GmailMessageRecord:
    if downstream_use not in GMAIL_DOWNSTREAM_USES:
        raise ApiError(
            422,
            "gmail_downstream_use_invalid",
            "Downstream use is invalid.",
        )
    record = session.get(GmailMessageRecord, gmail_message_record_id)
    if record is None or record.owner_user_id != owner_user_id:
        raise ApiError(404, "gmail_message_record_not_found", "Message was not found.")
    if record.suppression_status != SUPPRESSION_STATUS_NOT_SUPPRESSED:
        raise ApiError(
            409,
            "gmail_message_suppressed",
            "Suppressed Gmail messages cannot be used downstream.",
            details={
                "downstream_use": downstream_use,
                "suppression_reason_code": record.suppression_reason_code,
                "manual_handling_id": record.manual_handling_id,
            },
        )
    if record.classification_status != "classified":
        raise ApiError(
            409,
            "gmail_message_requires_manual_review",
            "Gmail message requires manual review before downstream use.",
            details={"downstream_use": downstream_use},
        )
    return record


def _upsert_message_record(
    session: Session,
    *,
    owner_user_id: str,
    connection: ConnectorConnection,
    message: FakeGmailMessage,
    eligibility_reason: str,
    actor_id: str,
    correlation_id: str | None,
    suppression_detector: SuppressionDetector,
    webhook_context: GmailSuppressionWebhookContext | None,
) -> GmailMessageRecord:
    classification = classify_message(message)
    suppression = _validated_suppression_decision(
        suppression_detector(message, classification)
    )
    existing = session.scalar(
        select(GmailMessageRecord).where(
            GmailMessageRecord.owner_user_id == owner_user_id,
            GmailMessageRecord.connection_id == connection.connection_id,
            GmailMessageRecord.provider_message_reference
            == message.provider_message_reference,
        )
    )
    manual_handling_id = existing.manual_handling_id if existing is not None else None
    if suppression.is_suppressed and manual_handling_id is None:
        manual = create_manual_handling_record(
            session,
            owner_user_id=owner_user_id,
            agent_id=actor_id,
            source_reference=f"gmail:{_safe_reference(message.provider_message_reference)}",
            reason_category=suppression.reason_category
            or "ProtectedHealthInformation",
            sensitivity_classification=suppression.sensitivity_classification,
            metadata_json={
                "connector_type": "gmail",
                "connection_id": connection.connection_id,
                "provider_message_reference": _safe_reference(
                    message.provider_message_reference
                ),
                "provider_thread_reference": _safe_reference(
                    message.provider_thread_reference
                ),
                "suppression_reason_code": suppression.reason_code,
            },
        )
        manual_handling_id = manual.manual_handling_id
        _emit_suppression_events(
            session,
            manual_handling_id=manual.manual_handling_id,
            reason_category=manual.reason_category,
            sensitivity_classification=manual.sensitivity_classification,
            actor_id=actor_id,
            correlation_id=correlation_id,
            webhook_context=webhook_context,
        )
    sanitized = _message_payload_values(
        message,
        eligibility_reason=eligibility_reason,
        classification=classification,
        suppression=suppression,
    )
    values = {
        **sanitized,
        "suppression_status": (
            SUPPRESSION_STATUS_SUPPRESSED
            if suppression.is_suppressed
            else SUPPRESSION_STATUS_NOT_SUPPRESSED
        ),
        "suppression_reason_code": suppression.reason_code,
        "manual_handling_id": manual_handling_id,
    }
    if existing is not None:
        for key, value in values.items():
            setattr(existing, key, value)
        session.flush()
        return existing
    record = GmailMessageRecord(
        owner_user_id=owner_user_id,
        connection_id=connection.connection_id,
        provider_message_reference=_safe_reference(message.provider_message_reference),
        **values,
    )
    session.add(record)
    session.flush()
    return record


def _require_gmail_connection(
    session: Session,
    *,
    owner_user_id: str,
    connection_id: str,
) -> ConnectorConnection:
    connection = session.get(ConnectorConnection, connection_id)
    if connection is None or connection.owner_user_id != owner_user_id:
        raise ApiError(404, "connection_not_found", "Connection was not found.")
    if connection.connector_type != "gmail":
        raise ApiError(
            422,
            "gmail_connection_required",
            "Gmail connection is required.",
        )
    if connection.status != "connected":
        raise ApiError(409, "connector_not_connected", "Connector is not connected.")
    if GMAIL_SCOPE_MODIFY not in connection.granted_scopes:
        raise ApiError(403, "connector_scope_missing", "Connector scope is missing.")
    return connection


def _validated_suppression_decision(
    decision: SuppressionDecision,
) -> SuppressionDecision:
    if not isinstance(decision.is_suppressed, bool):
        return _fail_closed_suppression()
    if decision.is_suppressed:
        if decision.reason_category not in {"Clinical", "ProtectedHealthInformation"}:
            return _fail_closed_suppression()
        if decision.sensitivity_classification != "restricted":
            return _fail_closed_suppression()
        if decision.reason_code not in {
            SUPPRESSION_REASON_CLINICAL,
            SUPPRESSION_REASON_PHI,
            SUPPRESSION_REASON_DETECTOR_INVALID,
        }:
            return _fail_closed_suppression()
        return decision
    if (
        decision.reason_category is not None
        or decision.reason_code is not None
        or decision.sensitivity_classification != "standard"
    ):
        return _fail_closed_suppression()
    return decision


def _fail_closed_suppression() -> SuppressionDecision:
    return SuppressionDecision(
        is_suppressed=True,
        reason_category="ProtectedHealthInformation",
        sensitivity_classification="restricted",
        reason_code=SUPPRESSION_REASON_DETECTOR_INVALID,
    )


def _message_payload_values(
    message: FakeGmailMessage,
    *,
    eligibility_reason: str,
    classification: ClassificationResult,
    suppression: SuppressionDecision,
) -> dict[str, Any]:
    suppressed = suppression.is_suppressed
    return {
        "provider_thread_reference": _safe_reference(
            message.provider_thread_reference
        ),
        "sender_address": (
            "suppressed@example.invalid"
            if suppressed
            else _safe_email(message.sender_address)
        ),
        "sender_domain": (
            "suppressed.invalid"
            if suppressed
            else _sender_domain(message.sender_address)
        ),
        "subject_preview": (
            SUPPRESSED_VALUE if suppressed else _preview(message.subject)
        ),
        "content_excerpt_hash": (
            _hash(f"suppressed:{message.provider_message_reference}")
            if suppressed
            else _hash(message.snippet)
        ),
        "attachment_metadata": [
            _attachment_payload(item, suppressed=suppressed)
            for item in message.attachments
        ],
        "label_names": (
            ["SUPPRESSED"]
            if suppressed
            else [_preview(label, limit=80) for label in message.label_names]
        ),
        "received_at": _normalized_datetime(message.received_at),
        "eligibility_reason": eligibility_reason,
        "classification_category": classification.category,
        "classification_confidence": classification.confidence,
        "classification_status": classification.status,
        "review_reason_code": classification.review_reason_code,
        "source_integrity_hash": _source_integrity_hash(message, suppressed=suppressed),
    }


def _emit_suppression_events(
    session: Session,
    *,
    manual_handling_id: str,
    reason_category: str,
    sensitivity_classification: str,
    actor_id: str,
    correlation_id: str | None,
    webhook_context: GmailSuppressionWebhookContext | None,
) -> None:
    event = message_held_for_manual_handling_event(
        manual_handling_id=manual_handling_id,
        status="pending",
        reason_category=reason_category,
        sensitivity_classification=sensitivity_classification,
    )
    record_audit_event(
        session,
        AuditEventInput(
            event_type="gmail.message_suppressed",
            actor_type="service",
            actor_id=actor_id,
            channel="service",
            action="suppress",
            resource_type="manual_handling",
            resource_id=manual_handling_id,
            result="succeeded",
            reason_code=reason_category,
            correlation_id=correlation_id,
            metadata=event.payload,
        ),
    )
    if webhook_context is None:
        return
    def audit_webhook_delivery(webhook_event: Any) -> None:
        record_webhook_audit_event(
            session,
            webhook_event,
            correlation_id=webhook_context.correlation_id,
        )

    enqueue_platform_webhook_event(
        session,
        event,
        correlation_id=webhook_context.correlation_id,
        now=webhook_context.now or utc_now(),
        settings=webhook_context.settings,
        audit_hook=audit_webhook_delivery,
    )


def _validate_policy(policy: GmailRetrievalPolicy) -> None:
    if not policy.eligibility_query.strip() or len(policy.eligibility_query) > 240:
        raise ApiError(422, "gmail_eligibility_query_invalid", "Query is invalid.")
    if policy.max_messages < 1 or policy.max_messages > 50:
        raise ApiError(422, "gmail_max_messages_invalid", "Max messages is invalid.")


def _validated_classification(
    *,
    category: str,
    confidence: int,
) -> ClassificationResult:
    if category not in GMAIL_CLASSIFICATION_CATEGORIES:
        return ClassificationResult(
            category="Review Required",
            confidence=0,
            status="review_required",
            review_reason_code="classification_category_invalid",
        )
    if confidence < 0 or confidence > 100:
        return ClassificationResult(
            category="Review Required",
            confidence=0,
            status="review_required",
            review_reason_code="classification_confidence_invalid",
        )
    return ClassificationResult(
        category=category,
        confidence=confidence,
        status="classified",
        review_reason_code=None,
    )


def _attachment_payload(
    attachment: FakeGmailAttachment,
    *,
    suppressed: bool = False,
) -> dict[str, Any]:
    return {
        "provider_attachment_reference": _safe_reference(
            attachment.provider_attachment_reference
        ),
        "filename": (
            SUPPRESSED_VALUE
            if suppressed
            else _preview(attachment.filename, limit=160)
        ),
        "mime_type": _preview(attachment.mime_type, limit=120),
        "size_bytes": attachment.size_bytes,
    }


def _safe_reference(value: str) -> str:
    return _preview(value, limit=160)


def _safe_email(value: str) -> str:
    if len(value) > 320 or "@" not in value or any(char.isspace() for char in value):
        return "unknown@example.invalid"
    return value


def _sender_domain(sender_address: str) -> str:
    try:
        domain = sender_address.rsplit("@", maxsplit=1)[1].lower()
    except IndexError:
        return "unknown"
    return _preview(domain, limit=160)


def _preview(value: str, *, limit: int = MAX_SUBJECT_PREVIEW_LENGTH) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _source_integrity_hash(
    message: FakeGmailMessage,
    *,
    suppressed: bool = False,
) -> str:
    attachment_refs = ",".join(
        attachment.provider_attachment_reference for attachment in message.attachments
    )
    if suppressed:
        return _hash(
            "|".join(
                [
                    message.provider_message_reference,
                    message.provider_thread_reference,
                    attachment_refs,
                    "suppressed",
                ]
            )
        )
    return _hash(
        "|".join(
            [
                message.provider_message_reference,
                message.provider_thread_reference,
                message.sender_address,
                message.subject,
                message.snippet,
                ",".join(message.label_names),
                attachment_refs,
            ]
        )
    )


def _normalized_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
