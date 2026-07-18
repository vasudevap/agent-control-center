from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.gmail_message import GmailDraftRecord, GmailMessageRecord
from atlas_api.models.knowledge import KnowledgeFact, KnowledgeFactRevision
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.connectors import authorize_connector_operation
from atlas_api.services.gmail_knowledge import prepare_gmail_knowledge_context
from atlas_api.services.gmail_messages import (
    GMAIL_AGENT_ID,
    ensure_gmail_message_allowed_for_downstream_use,
)
from atlas_api.services.knowledge_facts import (
    begin_idempotent_operation,
    complete_idempotent_operation,
)

MAX_DRAFT_SUBJECT_LENGTH = 240
MAX_DRAFT_BODY_LENGTH = 8000
PROHIBITED_DRAFT_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{12,}"),
    re.compile(r"BEGIN PRIVATE KEY"),
    re.compile(r"(access|refresh)[_-]?token", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"clinical|protected health|\bphi\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class GeneratedDraftOutput:
    subject: str
    body: str


@dataclass(frozen=True)
class GmailDraftCreationResult:
    draft: GmailDraftRecord
    replayed: bool


class DraftProviderError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class FakeDraftGenerator:
    def __init__(self, output: GeneratedDraftOutput) -> None:
        self.output = output
        self.calls: list[dict[str, Any]] = []

    def generate(self, input_payload: dict[str, Any]) -> GeneratedDraftOutput:
        self.calls.append(input_payload)
        return self.output


class FakeGmailDraftProvider:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.created_drafts: list[dict[str, str]] = []
        self.sent_messages: list[dict[str, str]] = []

    def create_draft(
        self,
        *,
        provider_message_reference: str,
        subject: str,
        body: str,
    ) -> str:
        if self.fail:
            raise DraftProviderError("gmail.create_draft.provider_failed")
        provider_draft_reference = "draft:" + _hash_text(
            "|".join([provider_message_reference, subject, body])
        )[:32]
        self.created_drafts.append(
            {
                "provider_message_reference": provider_message_reference,
                "provider_draft_reference": provider_draft_reference,
                "subject": subject,
                "body_hash": _hash_text(body),
            }
        )
        return provider_draft_reference


def create_gmail_draft(
    session: Session,
    *,
    owner_user_id: str,
    gmail_message_record_id: str,
    scenario: str,
    generator: FakeDraftGenerator,
    provider: FakeGmailDraftProvider,
    idempotency_key: str,
    correlation_id: str,
    actor_id: str = GMAIL_AGENT_ID,
) -> GmailDraftCreationResult:
    _validate_idempotency_key(idempotency_key)
    message = ensure_gmail_message_allowed_for_downstream_use(
        session,
        owner_user_id=owner_user_id,
        gmail_message_record_id=gmail_message_record_id,
        downstream_use="draft",
    )
    knowledge_context = prepare_gmail_knowledge_context(
        session,
        owner_user_id=owner_user_id,
        gmail_message_record_id=gmail_message_record_id,
        scenario=scenario,
        correlation_id=correlation_id,
        actor_id=actor_id,
    )
    if knowledge_context.status != "ready":
        _audit_draft_attempt(
            session,
            actor_id=actor_id,
            result="denied",
            reason_code="gmail_required_facts_missing",
            resource_id=gmail_message_record_id,
            correlation_id=correlation_id,
        )
        raise ApiError(
            409,
            "gmail_required_facts_missing",
            "Required governed facts are missing or stale.",
        )
    idem = begin_idempotent_operation(
        session,
        actor_id=actor_id,
        operation="gmail.create_draft",
        idempotency_key=idempotency_key,
        payload={
            "gmail_message_record_id": gmail_message_record_id,
            "scenario": scenario,
            "fact_revision_ids": knowledge_context.fact_revision_ids,
        },
        resource_type="gmail_draft",
    )
    if idem.replayed and idem.record.resource_id is not None:
        draft = session.get(GmailDraftRecord, idem.record.resource_id)
        if draft is None:
            raise ApiError(
                409,
                "gmail_draft_idempotency_record_missing",
                "Gmail draft idempotency record is missing.",
            )
        return GmailDraftCreationResult(draft=draft, replayed=True)
    authorization = authorize_connector_operation(
        session,
        owner_user_id=owner_user_id,
        connection_id=message.connection_id,
        operation_id="gmail.create_draft",
        actor_id=actor_id,
        correlation_id=correlation_id,
    )
    if not authorization.allowed:
        _audit_draft_attempt(
            session,
            actor_id=actor_id,
            result="denied",
            reason_code=authorization.reason_code,
            resource_id=gmail_message_record_id,
            correlation_id=correlation_id,
        )
        raise ApiError(403, authorization.reason_code, "Connector operation denied.")
    facts_used = _facts_used(
        session,
        owner_user_id=owner_user_id,
        fact_revision_ids=knowledge_context.fact_revision_ids,
        bound_at=utc_now(),
    )
    generated = generator.generate(
        _draft_input_payload(
            message,
            scenario=scenario,
            fact_revision_ids=knowledge_context.fact_revision_ids,
        )
    )
    _validate_generated_draft(generated)
    try:
        provider_draft_reference = provider.create_draft(
            provider_message_reference=message.provider_message_reference,
            subject=generated.subject,
            body=generated.body,
        )
    except DraftProviderError as exc:
        _audit_draft_attempt(
            session,
            actor_id=actor_id,
            result="failed",
            reason_code=exc.code,
            resource_id=gmail_message_record_id,
            correlation_id=correlation_id,
        )
        raise ApiError(502, exc.code, "Gmail draft provider failed.") from exc
    body_hash = _hash_text(generated.body)
    evidence_summary = {
        "draft_provider_reference": provider_draft_reference,
        "body_hash": body_hash,
        "subject_preview": _preview(generated.subject),
        "facts_used": facts_used,
    }
    decision_context_manifest = {
        "action_identity": f"gmail_draft:{provider_draft_reference}",
        "provider_message_reference": message.provider_message_reference,
        "draft_body_hash": body_hash,
        "fact_revision_bindings": [_binding(item) for item in facts_used],
    }
    draft = GmailDraftRecord(
        owner_user_id=owner_user_id,
        gmail_message_record_id=message.gmail_message_record_id,
        connection_id=message.connection_id,
        provider_message_reference=message.provider_message_reference,
        provider_draft_reference=provider_draft_reference,
        scenario=scenario,
        status="created",
        idempotency_key=idempotency_key,
        subject_preview=_preview(generated.subject),
        body_hash=body_hash,
        facts_used=facts_used,
        evidence_summary=evidence_summary,
        decision_context_manifest=decision_context_manifest,
    )
    session.add(draft)
    session.flush()
    complete_idempotent_operation(
        idem.record,
        resource_id=draft.gmail_draft_record_id,
    )
    _audit_draft_attempt(
        session,
        actor_id=actor_id,
        result="succeeded",
        reason_code=None,
        resource_id=draft.gmail_draft_record_id,
        correlation_id=correlation_id,
    )
    session.flush()
    return GmailDraftCreationResult(draft=draft, replayed=False)


def _facts_used(
    session: Session,
    *,
    owner_user_id: str,
    fact_revision_ids: list[str],
    bound_at: datetime,
) -> list[dict[str, str | int | bool | None]]:
    items: list[dict[str, str | int | bool | None]] = []
    for revision_id in fact_revision_ids:
        revision = session.get(KnowledgeFactRevision, revision_id)
        if revision is None:
            raise ApiError(
                409,
                "knowledge_fact_revision_missing",
                "Knowledge fact revision is missing.",
            )
        fact = session.get(KnowledgeFact, revision.knowledge_fact_id)
        if fact is None or fact.owner_user_id != owner_user_id:
            raise ApiError(404, "knowledge_fact_not_found", "Knowledge fact not found.")
        if fact.current_revision_id != revision.knowledge_fact_revision_id:
            raise ApiError(
                409,
                "knowledge_fact_revision_changed",
                "Knowledge fact revision changed.",
            )
        if revision.prohibited_content_reason is not None:
            raise ApiError(
                422,
                "knowledge_fact_prohibited_content",
                "Knowledge fact revision contains prohibited content.",
            )
        items.append(
            {
                "type": "knowledge_fact_revision",
                "knowledge_fact_id": fact.knowledge_fact_id,
                "fact_key": fact.fact_key,
                "knowledge_fact_revision_id": revision.knowledge_fact_revision_id,
                "revision_number": revision.revision_number,
                "content_hash": revision.content_hash,
                "source_type": revision.source_type,
                "source_reference": revision.source_reference,
                "is_volatile": revision.is_volatile,
                "confirmed_at": _isoformat(revision.confirmed_at),
                "bound_at": _isoformat(bound_at),
            }
        )
    return items


def _binding(
    item: dict[str, str | int | bool | None],
) -> dict[str, str | int | bool | None]:
    return {
        "type": item["type"],
        "knowledge_fact_id": item["knowledge_fact_id"],
        "knowledge_fact_revision_id": item["knowledge_fact_revision_id"],
        "revision_number": item["revision_number"],
        "content_hash": item["content_hash"],
        "is_volatile": item["is_volatile"],
        "confirmed_at": item["confirmed_at"],
    }


def _draft_input_payload(
    message: GmailMessageRecord,
    *,
    scenario: str,
    fact_revision_ids: list[str],
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "source": {
            "provider_message_reference": message.provider_message_reference,
            "classification_category": message.classification_category,
            "subject_preview": message.subject_preview,
        },
        "fact_revision_ids": fact_revision_ids,
    }


def _validate_generated_draft(output: GeneratedDraftOutput) -> None:
    subject = output.subject.strip()
    body = output.body.strip()
    if not subject or len(subject) > MAX_DRAFT_SUBJECT_LENGTH:
        raise ApiError(422, "gmail_draft_subject_invalid", "Draft subject is invalid.")
    if not body or len(body) > MAX_DRAFT_BODY_LENGTH:
        raise ApiError(422, "gmail_draft_body_invalid", "Draft body is invalid.")
    text = f"{subject}\n{body}"
    if any(pattern.search(text) for pattern in PROHIBITED_DRAFT_PATTERNS):
        raise ApiError(
            422,
            "gmail_draft_prohibited_content",
            "Draft output contains prohibited content.",
        )


def _audit_draft_attempt(
    session: Session,
    *,
    actor_id: str,
    result: str,
    reason_code: str | None,
    resource_id: str,
    correlation_id: str,
) -> None:
    record_audit_event(
        session,
        AuditEventInput(
            event_type="gmail.draft_generation",
            actor_type="service",
            actor_id=actor_id,
            channel="service",
            action="create_draft",
            resource_type="gmail_draft",
            resource_id=resource_id,
            result=result,
            reason_code=reason_code,
            correlation_id=correlation_id,
            metadata={
                "resource_id": resource_id,
                "resource_type": "gmail_draft",
                "outcome": result,
            },
        ),
    )


def _validate_idempotency_key(value: str) -> None:
    if len(value) < 16 or len(value) > 128 or any(char.isspace() for char in value):
        raise ApiError(
            422,
            "gmail_draft_idempotency_key_invalid",
            "Gmail draft idempotency key is invalid.",
        )


def _preview(value: str) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= MAX_DRAFT_SUBJECT_LENGTH:
        return normalized
    return normalized[: MAX_DRAFT_SUBJECT_LENGTH - 3] + "..."


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()
