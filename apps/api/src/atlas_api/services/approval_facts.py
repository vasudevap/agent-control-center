from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from sqlalchemy.orm import Session

from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.approval import ApprovalRequest
from atlas_api.models.knowledge import KnowledgeFact, KnowledgeFactRevision
from atlas_api.services.knowledge_facts import STALE_VOLATILE_AFTER, get_fact

FACTS_USED_EVIDENCE_KEY = "facts_used"
FACT_REVISION_BINDINGS_KEY = "fact_revision_bindings"

FactsRevalidationStatus = Literal["passed", "failed"]


@dataclass(frozen=True)
class FactRevalidationFailure:
    knowledge_fact_id: str
    reason_code: str


@dataclass(frozen=True)
class FactsRevalidationResult:
    approval_id: str
    status: FactsRevalidationStatus
    continuation_status: str
    facts_checked: int
    failure_reason_code: str | None
    failures: list[FactRevalidationFailure]


def attach_facts_used_evidence(
    session: Session,
    approval: ApprovalRequest,
    *,
    owner_user_id: str,
    knowledge_fact_ids: list[str],
    bound_at: datetime | None = None,
) -> ApprovalRequest:
    facts_used = [
        _fact_used_evidence_item(
            fact,
            revision,
            bound_at=bound_at or utc_now(),
        )
        for fact, revision in (
            get_fact(
                session,
                owner_user_id=owner_user_id,
                knowledge_fact_id=knowledge_fact_id,
            )
            for knowledge_fact_id in knowledge_fact_ids
        )
    ]
    bindings = [_binding_from_evidence(item) for item in facts_used]
    approval.evidence_summary = {
        **approval.evidence_summary,
        FACTS_USED_EVIDENCE_KEY: facts_used,
    }
    approval.decision_context_manifest = {
        **approval.decision_context_manifest,
        FACT_REVISION_BINDINGS_KEY: bindings,
    }
    approval.revision += 1
    session.flush()
    return approval


def revalidate_approval_facts(
    session: Session,
    approval: ApprovalRequest,
    *,
    now: datetime | None = None,
) -> FactsRevalidationResult:
    if approval.status != "approved":
        raise ApiError(
            409,
            "approval_not_approved_for_revalidation",
            "Only approved approvals can be revalidated for continuation.",
        )
    bindings = _bindings(approval)
    failures = [
        failure
        for binding in bindings
        if (
            failure := _validate_binding(
                session,
                owner_user_id=approval.owner_user_id,
                binding=binding,
                now=now or utc_now(),
            )
        )
        is not None
    ]
    if failures:
        approval.continuation_status = "blocked"
        status: FactsRevalidationStatus = "failed"
        reason_code = failures[0].reason_code
    else:
        approval.continuation_status = "ready"
        status = "passed"
        reason_code = None
    session.flush()
    return FactsRevalidationResult(
        approval_id=approval.approval_id,
        status=status,
        continuation_status=approval.continuation_status,
        facts_checked=len(bindings),
        failure_reason_code=reason_code,
        failures=failures,
    )


def _fact_used_evidence_item(
    fact: KnowledgeFact,
    revision: KnowledgeFactRevision,
    *,
    bound_at: datetime,
) -> dict[str, str | int | bool | None]:
    if fact.status != "active":
        raise ApiError(409, "knowledge_fact_not_active", "Fact is not active.")
    if revision.prohibited_content_reason is not None:
        raise ApiError(
            422,
            "knowledge_fact_prohibited_content",
            "Fact revision contains prohibited content.",
        )
    return {
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


def _binding_from_evidence(
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


def _validate_binding(
    session: Session,
    *,
    owner_user_id: str,
    binding: dict[str, Any],
    now: datetime,
) -> FactRevalidationFailure | None:
    fact_id = _required_string(binding, "knowledge_fact_id")
    revision_id = _required_string(binding, "knowledge_fact_revision_id")
    content_hash = _required_string(binding, "content_hash")
    fact = session.get(KnowledgeFact, fact_id)
    if fact is None or fact.owner_user_id != owner_user_id:
        return FactRevalidationFailure(fact_id, "fact_missing")
    if fact.status != "active" or fact.deleted_at is not None:
        return FactRevalidationFailure(fact_id, "fact_deleted")
    if fact.current_revision_id != revision_id:
        return FactRevalidationFailure(fact_id, "fact_revision_changed")
    revision = session.get(KnowledgeFactRevision, revision_id)
    if revision is None:
        return FactRevalidationFailure(fact_id, "fact_revision_missing")
    if revision.content_hash != content_hash:
        return FactRevalidationFailure(fact_id, "fact_integrity_changed")
    if revision.prohibited_content_reason is not None:
        return FactRevalidationFailure(fact_id, "fact_prohibited_content")
    if _is_stale_volatile(revision, now=now):
        return FactRevalidationFailure(fact_id, "fact_stale_volatile")
    return None


def _bindings(approval: ApprovalRequest) -> list[dict[str, Any]]:
    raw_bindings = approval.decision_context_manifest.get(FACT_REVISION_BINDINGS_KEY)
    if raw_bindings is None:
        return []
    if not isinstance(raw_bindings, list):
        raise ApiError(
            422,
            "fact_revision_bindings_invalid",
            "Fact revision bindings are invalid.",
        )
    return [
        binding
        for binding in raw_bindings
        if isinstance(binding, dict)
    ]


def _required_string(binding: dict[str, Any], key: str) -> str:
    value = binding.get(key)
    if not isinstance(value, str) or not value:
        raise ApiError(
            422,
            "fact_revision_binding_invalid",
            "Fact revision binding is invalid.",
        )
    return value


def _is_stale_volatile(
    revision: KnowledgeFactRevision,
    *,
    now: datetime,
) -> bool:
    if not revision.is_volatile:
        return False
    if revision.confirmed_at is None:
        return True
    comparable = revision.confirmed_at
    if comparable.tzinfo is None:
        comparable = comparable.replace(tzinfo=UTC)
    return comparable <= now - STALE_VOLATILE_AFTER


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()
