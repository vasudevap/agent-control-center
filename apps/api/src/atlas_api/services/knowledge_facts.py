from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.contracts import (
    PaginationParameters,
    decode_cursor,
    encode_cursor,
)
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.external_client import ExternalProductClient
from atlas_api.models.idempotency import ApiIdempotencyRecord
from atlas_api.models.knowledge import KnowledgeFact, KnowledgeFactRevision

ALLOWED_CLASSIFICATIONS = frozenset({"internal", "confidential"})
ALLOWED_FACT_STATUSES = frozenset({"active", "deleted"})
ALLOWED_SOURCE_TYPES = frozenset({"human", "manual_import", "system_seed"})
STALE_VOLATILE_AFTER = timedelta(days=30)
_FACT_KEY_PATTERN = re.compile(r"[a-z0-9][a-z0-9_.:-]{0,158}[a-z0-9]")
_PROHIBITED_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{12,}"),
    re.compile(r"BEGIN PRIVATE KEY"),
    re.compile(r"(access|refresh)[_-]?token", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"clinical|protected health|\bphi\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class KnowledgeFactPage:
    facts: list[tuple[KnowledgeFact, KnowledgeFactRevision]]
    next_cursor: str | None


@dataclass(frozen=True)
class IdempotencyResult:
    record: ApiIdempotencyRecord
    replayed: bool


def resolve_owner_user_id(session: Session, external_client_id: str) -> str:
    client = session.get(ExternalProductClient, external_client_id)
    if (
        client is None
        or client.status != "active"
        or client.human_owner_user_id is None
    ):
        raise ApiError(
            status_code=403,
            code="knowledge_owner_unavailable",
            message="External client is not linked to an active human owner.",
        )
    return client.human_owner_user_id


def list_facts(
    session: Session,
    *,
    owner_user_id: str,
    pagination: PaginationParameters,
    status: str | None = None,
    classification: str | None = None,
    stale_volatile_only: bool = False,
    now: datetime | None = None,
) -> KnowledgeFactPage:
    if status is not None and status not in ALLOWED_FACT_STATUSES:
        raise ApiError(422, "knowledge_fact_status_invalid", "Status is invalid.")
    if classification is not None and classification not in ALLOWED_CLASSIFICATIONS:
        raise ApiError(
            422,
            "knowledge_fact_classification_invalid",
            "Classification is invalid.",
        )
    query = select(KnowledgeFact).where(KnowledgeFact.owner_user_id == owner_user_id)
    if status is not None:
        query = query.where(KnowledgeFact.status == status)
    if classification is not None:
        query = query.where(KnowledgeFact.classification == classification)
    query = _apply_cursor(query, pagination.cursor)
    query = query.order_by(KnowledgeFact.created_at, KnowledgeFact.knowledge_fact_id)
    rows = list(session.scalars(query.limit(pagination.limit + 1)))
    pairs = [(fact, _current_revision(session, fact)) for fact in rows]
    if stale_volatile_only:
        current = now or utc_now()
        pairs = [
            pair
            for pair in pairs
            if _is_stale_volatile(pair[1], now=current)
            and pair[0].status == "active"
        ]
    next_cursor = None
    if len(pairs) > pagination.limit:
        pairs = pairs[: pagination.limit]
        last = pairs[-1][0]
        next_cursor = encode_cursor(
            {
                "created_at": last.created_at.isoformat(),
                "knowledge_fact_id": last.knowledge_fact_id,
            }
        )
    return KnowledgeFactPage(facts=pairs, next_cursor=next_cursor)


def get_fact(
    session: Session,
    *,
    owner_user_id: str,
    knowledge_fact_id: str,
) -> tuple[KnowledgeFact, KnowledgeFactRevision]:
    fact = session.get(KnowledgeFact, knowledge_fact_id)
    if fact is None or fact.owner_user_id != owner_user_id:
        raise ApiError(404, "knowledge_fact_not_found", "Knowledge fact was not found.")
    return fact, _current_revision(session, fact)


def create_fact(
    session: Session,
    *,
    owner_user_id: str,
    fact_key: str,
    display_value: str,
    classification: str,
    source_type: str,
    source_reference: str | None,
    provenance_summary: str,
    is_volatile: bool,
    confirmed: bool,
) -> tuple[KnowledgeFact, KnowledgeFactRevision]:
    _validate_fact_key(fact_key)
    _validate_fact_payload(
        display_value=display_value,
        classification=classification,
        source_type=source_type,
        provenance_summary=provenance_summary,
    )
    existing = session.scalar(
        select(KnowledgeFact).where(
            KnowledgeFact.owner_user_id == owner_user_id,
            KnowledgeFact.fact_key == fact_key,
            KnowledgeFact.status == "active",
        )
    )
    if existing is not None:
        raise ApiError(
            409,
            "knowledge_fact_key_conflict",
            "An active fact already uses this fact key.",
        )
    confirmed_at = utc_now() if confirmed else None
    fact = KnowledgeFact(
        owner_user_id=owner_user_id,
        fact_key=fact_key,
        classification=classification,
        status="active",
        last_confirmed_at=confirmed_at,
    )
    session.add(fact)
    session.flush()
    revision = _create_revision(
        session,
        fact=fact,
        display_value=display_value,
        source_type=source_type,
        source_reference=source_reference,
        provenance_summary=provenance_summary,
        is_volatile=is_volatile,
        confirmed_at=confirmed_at,
    )
    session.flush()
    return fact, revision


def update_fact(
    session: Session,
    *,
    owner_user_id: str,
    knowledge_fact_id: str,
    display_value: str,
    source_type: str,
    source_reference: str | None,
    provenance_summary: str,
    is_volatile: bool,
    confirmed: bool,
) -> tuple[KnowledgeFact, KnowledgeFactRevision]:
    fact, _previous = get_fact(
        session,
        owner_user_id=owner_user_id,
        knowledge_fact_id=knowledge_fact_id,
    )
    if fact.status != "active":
        raise ApiError(409, "knowledge_fact_not_active", "Fact is not active.")
    _validate_fact_payload(
        display_value=display_value,
        classification=fact.classification,
        source_type=source_type,
        provenance_summary=provenance_summary,
    )
    confirmed_at = utc_now() if confirmed else None
    if confirmed_at is not None:
        fact.last_confirmed_at = confirmed_at
    revision = _create_revision(
        session,
        fact=fact,
        display_value=display_value,
        source_type=source_type,
        source_reference=source_reference,
        provenance_summary=provenance_summary,
        is_volatile=is_volatile,
        confirmed_at=confirmed_at,
    )
    session.flush()
    return fact, revision


def confirm_fact(
    session: Session,
    *,
    owner_user_id: str,
    knowledge_fact_id: str,
) -> tuple[KnowledgeFact, KnowledgeFactRevision]:
    fact, current = get_fact(
        session,
        owner_user_id=owner_user_id,
        knowledge_fact_id=knowledge_fact_id,
    )
    if fact.status != "active":
        raise ApiError(409, "knowledge_fact_not_active", "Fact is not active.")
    confirmed_at = utc_now()
    fact.last_confirmed_at = confirmed_at
    revision = _create_revision(
        session,
        fact=fact,
        display_value=current.display_value,
        source_type="human",
        source_reference=current.source_reference,
        provenance_summary="Human owner reconfirmed the current fact value.",
        is_volatile=current.is_volatile,
        confirmed_at=confirmed_at,
    )
    session.flush()
    return fact, revision


def soft_delete_fact(
    session: Session,
    *,
    owner_user_id: str,
    knowledge_fact_id: str,
) -> KnowledgeFact:
    fact, _revision = get_fact(
        session,
        owner_user_id=owner_user_id,
        knowledge_fact_id=knowledge_fact_id,
    )
    if fact.status != "deleted":
        fact.status = "deleted"
        fact.deleted_at = utc_now()
    session.flush()
    return fact


def begin_idempotent_operation(
    session: Session,
    *,
    actor_id: str,
    operation: str,
    idempotency_key: str,
    payload: dict[str, Any],
    resource_type: str = "knowledge_fact",
) -> IdempotencyResult:
    request_hash = _payload_hash(payload)
    existing = session.scalar(
        select(ApiIdempotencyRecord).where(
            ApiIdempotencyRecord.actor_id == actor_id,
            ApiIdempotencyRecord.operation == operation,
            ApiIdempotencyRecord.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        if existing.request_hash != request_hash:
            raise ApiError(
                409,
                "idempotency_key_conflict",
                "Idempotency-Key was already used with a different request.",
            )
        return IdempotencyResult(record=existing, replayed=True)
    record = ApiIdempotencyRecord(
        actor_id=actor_id,
        operation=operation,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        resource_type=resource_type,
    )
    session.add(record)
    session.flush()
    return IdempotencyResult(record=record, replayed=False)


def complete_idempotent_operation(
    record: ApiIdempotencyRecord,
    *,
    resource_id: str,
) -> None:
    record.resource_id = resource_id


def _apply_cursor(
    query: Any,
    cursor: str | None,
) -> Any:
    if cursor is None:
        return query
    values = decode_cursor(cursor)
    try:
        created_at = datetime.fromisoformat(values["created_at"])
        fact_id = values["knowledge_fact_id"]
    except (KeyError, ValueError) as exc:
        raise ApiError(
            status_code=422,
            code="pagination_cursor_invalid",
            message="Pagination cursor is invalid.",
        ) from exc
    return query.where(
        (KnowledgeFact.created_at > created_at)
        | (
            (KnowledgeFact.created_at == created_at)
            & (KnowledgeFact.knowledge_fact_id > fact_id)
        )
    )


def _current_revision(
    session: Session,
    fact: KnowledgeFact,
) -> KnowledgeFactRevision:
    if fact.current_revision_id is None:
        raise ApiError(
            500,
            "knowledge_fact_revision_missing",
            "Knowledge fact revision is missing.",
        )
    revision = session.get(KnowledgeFactRevision, fact.current_revision_id)
    if revision is None:
        raise ApiError(
            500,
            "knowledge_fact_revision_missing",
            "Knowledge fact revision is missing.",
        )
    return revision


def _create_revision(
    session: Session,
    *,
    fact: KnowledgeFact,
    display_value: str,
    source_type: str,
    source_reference: str | None,
    provenance_summary: str,
    is_volatile: bool,
    confirmed_at: datetime | None,
) -> KnowledgeFactRevision:
    current_number = len(fact.revisions)
    revision = KnowledgeFactRevision(
        knowledge_fact_id=fact.knowledge_fact_id,
        revision_number=current_number + 1,
        display_value=display_value,
        content_hash=hashlib.sha256(display_value.encode()).hexdigest(),
        source_type=source_type,
        source_reference=source_reference,
        provenance_summary=provenance_summary,
        is_volatile=is_volatile,
        confirmed_at=confirmed_at,
    )
    session.add(revision)
    session.flush()
    fact.current_revision_id = revision.knowledge_fact_revision_id
    return revision


def _validate_fact_key(fact_key: str) -> None:
    if _FACT_KEY_PATTERN.fullmatch(fact_key) is None:
        raise ApiError(422, "knowledge_fact_key_invalid", "Fact key is invalid.")


def _validate_fact_payload(
    *,
    display_value: str,
    classification: str,
    source_type: str,
    provenance_summary: str,
) -> None:
    if classification not in ALLOWED_CLASSIFICATIONS:
        raise ApiError(
            422,
            "knowledge_fact_classification_invalid",
            "Classification is invalid.",
        )
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ApiError(422, "knowledge_fact_source_invalid", "Source is invalid.")
    if not display_value.strip() or len(display_value) > 4000:
        raise ApiError(422, "knowledge_fact_value_invalid", "Fact value is invalid.")
    if not provenance_summary.strip() or len(provenance_summary) > 1000:
        raise ApiError(
            422,
            "knowledge_fact_provenance_invalid",
            "Fact provenance is invalid.",
        )
    if any(pattern.search(display_value) for pattern in _PROHIBITED_PATTERNS):
        raise ApiError(
            422,
            "knowledge_fact_prohibited_content",
            "Fact value contains prohibited content.",
        )
    if any(pattern.search(provenance_summary) for pattern in _PROHIBITED_PATTERNS):
        raise ApiError(
            422,
            "knowledge_fact_prohibited_content",
            "Fact provenance contains prohibited content.",
        )


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


def _payload_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(serialized.encode()).hexdigest()
