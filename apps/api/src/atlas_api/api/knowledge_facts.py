from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Annotated, cast

from fastapi import APIRouter, Depends, Header, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from atlas_api.core.auth import ExternalClientPrincipal, verify_external_client
from atlas_api.core.authorization import (
    ActorKind,
    AuthorizationContext,
    Channel,
    authorize,
)
from atlas_api.core.contracts import (
    PaginationParameters,
    success_payload,
    validate_idempotency_key,
)
from atlas_api.core.correlation import get_correlation_id
from atlas_api.core.errors import ApiError
from atlas_api.models.knowledge import KnowledgeFact, KnowledgeFactRevision
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.knowledge_facts import (
    begin_idempotent_operation,
    complete_idempotent_operation,
    confirm_fact,
    create_fact,
    get_fact,
    list_facts,
    resolve_owner_user_id,
    soft_delete_fact,
    update_fact,
)

router = APIRouter(prefix="/api/v1/knowledge/facts", tags=["knowledge"])

ExternalClientDependency = Annotated[
    ExternalClientPrincipal,
    Depends(verify_external_client),
]


class KnowledgeFactMutationPayload(BaseModel):
    display_value: str = Field(min_length=1, max_length=4000)
    source_type: str = Field(min_length=1, max_length=80)
    source_reference: str | None = Field(default=None, max_length=240)
    provenance_summary: str = Field(min_length=1, max_length=1000)
    is_volatile: bool = False
    confirmed: bool = False


class KnowledgeFactCreatePayload(KnowledgeFactMutationPayload):
    fact_key: str = Field(min_length=1, max_length=160)
    classification: str = Field(default="internal", min_length=1, max_length=40)


class KnowledgeFactRevisionPayload(BaseModel):
    knowledge_fact_revision_id: str
    revision_number: int
    display_value: str
    content_hash: str
    source_type: str
    source_reference: str | None
    provenance_summary: str
    is_volatile: bool
    confirmed_at: datetime | None
    created_at: datetime


class KnowledgeFactPayload(BaseModel):
    knowledge_fact_id: str
    fact_key: str
    status: str
    classification: str
    current_revision_id: str
    last_confirmed_at: datetime | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    current_revision: KnowledgeFactRevisionPayload


class KnowledgeFactListMeta(BaseModel):
    correlation_id: str | None
    next_cursor: str | None = None


class KnowledgeFactResponse(BaseModel):
    data: KnowledgeFactPayload
    meta: KnowledgeFactListMeta


class KnowledgeFactListResponse(BaseModel):
    data: list[KnowledgeFactPayload]
    meta: KnowledgeFactListMeta


@router.get(
    "",
    response_model=KnowledgeFactListResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def list_knowledge_facts(
    request: Request,
    principal: ExternalClientDependency,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str | None, Query(min_length=1, max_length=40)] = None,
    classification: Annotated[str | None, Query(min_length=1, max_length=40)] = None,
    stale_volatile_only: bool = False,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _prepare_authorized_owner(session, principal, action="list")
        page = list_facts(
            session,
            owner_user_id=owner_user_id,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status=status,
            classification=classification,
            stale_volatile_only=stale_volatile_only,
        )
        _audit(
            session,
            principal,
            action="list",
            result="succeeded",
            resource_id=None,
            metadata={"count": len(page.facts), "stale_only": stale_volatile_only},
        )
        session.commit()
        return success_payload(
            [_fact_payload(fact, revision) for fact, revision in page.facts],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@router.post(
    "",
    response_model=KnowledgeFactResponse,
    status_code=201,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def create_knowledge_fact(
    payload: KnowledgeFactCreatePayload,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    payload_dict = payload.model_dump(mode="json")
    with session_factory() as session:
        owner_user_id = _prepare_authorized_owner(session, principal, action="create")
        idem = begin_idempotent_operation(
            session,
            actor_id=principal.external_client_id,
            operation="knowledge_fact.create",
            idempotency_key=key,
            payload=payload_dict,
        )
        if idem.replayed and idem.record.resource_id is not None:
            fact, revision = get_fact(
                session,
                owner_user_id=owner_user_id,
                knowledge_fact_id=idem.record.resource_id,
            )
        else:
            fact, revision = create_fact(
                session,
                owner_user_id=owner_user_id,
                fact_key=payload.fact_key,
                display_value=payload.display_value,
                classification=payload.classification,
                source_type=payload.source_type,
                source_reference=payload.source_reference,
                provenance_summary=payload.provenance_summary,
                is_volatile=payload.is_volatile,
                confirmed=payload.confirmed,
            )
            complete_idempotent_operation(
                idem.record,
                resource_id=fact.knowledge_fact_id,
            )
        _audit(
            session,
            principal,
            action="create",
            result="succeeded",
            resource_id=fact.knowledge_fact_id,
            metadata={"idempotent_replay": idem.replayed},
        )
        session.commit()
        return success_payload(
            _fact_payload(fact, revision),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get(
    "/{knowledge_fact_id}",
    response_model=KnowledgeFactResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_knowledge_fact(
    knowledge_fact_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _prepare_authorized_owner(session, principal, action="read")
        fact, revision = get_fact(
            session,
            owner_user_id=owner_user_id,
            knowledge_fact_id=knowledge_fact_id,
        )
        _audit(
            session,
            principal,
            action="read",
            result="succeeded",
            resource_id=fact.knowledge_fact_id,
        )
        session.commit()
        return success_payload(
            _fact_payload(fact, revision),
            meta={"correlation_id": get_correlation_id()},
        )


@router.patch(
    "/{knowledge_fact_id}",
    response_model=KnowledgeFactResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def update_knowledge_fact(
    knowledge_fact_id: str,
    payload: KnowledgeFactMutationPayload,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    payload_dict = {
        "knowledge_fact_id": knowledge_fact_id,
        **payload.model_dump(mode="json"),
    }
    with session_factory() as session:
        owner_user_id = _prepare_authorized_owner(session, principal, action="update")
        idem = begin_idempotent_operation(
            session,
            actor_id=principal.external_client_id,
            operation="knowledge_fact.update",
            idempotency_key=key,
            payload=payload_dict,
        )
        if idem.replayed and idem.record.resource_id is not None:
            fact, revision = get_fact(
                session,
                owner_user_id=owner_user_id,
                knowledge_fact_id=idem.record.resource_id,
            )
        else:
            fact, revision = update_fact(
                session,
                owner_user_id=owner_user_id,
                knowledge_fact_id=knowledge_fact_id,
                display_value=payload.display_value,
                source_type=payload.source_type,
                source_reference=payload.source_reference,
                provenance_summary=payload.provenance_summary,
                is_volatile=payload.is_volatile,
                confirmed=payload.confirmed,
            )
            complete_idempotent_operation(
                idem.record,
                resource_id=fact.knowledge_fact_id,
            )
        _audit(
            session,
            principal,
            action="update",
            result="succeeded",
            resource_id=fact.knowledge_fact_id,
            metadata={"idempotent_replay": idem.replayed},
        )
        session.commit()
        return success_payload(
            _fact_payload(fact, revision),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post(
    "/{knowledge_fact_id}/confirm",
    response_model=KnowledgeFactResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def confirm_knowledge_fact(
    knowledge_fact_id: str,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _prepare_authorized_owner(session, principal, action="confirm")
        idem = begin_idempotent_operation(
            session,
            actor_id=principal.external_client_id,
            operation="knowledge_fact.confirm",
            idempotency_key=key,
            payload={"knowledge_fact_id": knowledge_fact_id},
        )
        if idem.replayed and idem.record.resource_id is not None:
            fact, revision = get_fact(
                session,
                owner_user_id=owner_user_id,
                knowledge_fact_id=idem.record.resource_id,
            )
        else:
            fact, revision = confirm_fact(
                session,
                owner_user_id=owner_user_id,
                knowledge_fact_id=knowledge_fact_id,
            )
            complete_idempotent_operation(
                idem.record,
                resource_id=fact.knowledge_fact_id,
            )
        _audit(
            session,
            principal,
            action="confirm",
            result="succeeded",
            resource_id=fact.knowledge_fact_id,
            metadata={"idempotent_replay": idem.replayed},
        )
        session.commit()
        return success_payload(
            _fact_payload(fact, revision),
            meta={"correlation_id": get_correlation_id()},
        )


@router.delete(
    "/{knowledge_fact_id}",
    response_model=KnowledgeFactResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def delete_knowledge_fact(
    knowledge_fact_id: str,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _prepare_authorized_owner(session, principal, action="delete")
        idem = begin_idempotent_operation(
            session,
            actor_id=principal.external_client_id,
            operation="knowledge_fact.delete",
            idempotency_key=key,
            payload={"knowledge_fact_id": knowledge_fact_id},
        )
        if idem.replayed and idem.record.resource_id is not None:
            fact, revision = get_fact(
                session,
                owner_user_id=owner_user_id,
                knowledge_fact_id=idem.record.resource_id,
            )
        else:
            fact = soft_delete_fact(
                session,
                owner_user_id=owner_user_id,
                knowledge_fact_id=knowledge_fact_id,
            )
            revision = get_fact(
                session,
                owner_user_id=owner_user_id,
                knowledge_fact_id=knowledge_fact_id,
            )[1]
            complete_idempotent_operation(
                idem.record,
                resource_id=fact.knowledge_fact_id,
            )
        _audit(
            session,
            principal,
            action="delete",
            result="succeeded",
            resource_id=fact.knowledge_fact_id,
            metadata={"idempotent_replay": idem.replayed},
        )
        session.commit()
        return success_payload(
            _fact_payload(fact, revision),
            meta={"correlation_id": get_correlation_id()},
        )


def _require_session_factory(request: Request) -> Callable[[], Session]:
    session_factory = cast(
        "Callable[[], Session] | None",
        request.app.state.session_factory,
    )
    if session_factory is None:
        raise ApiError(
            status_code=503,
            code="knowledge_fact_store_not_configured",
            message="Knowledge fact storage is not configured.",
        )
    return session_factory


def _prepare_authorized_owner(
    session: Session,
    principal: ExternalClientPrincipal,
    *,
    action: str,
) -> str:
    _authorize(session, principal, action=action)
    return resolve_owner_user_id(session, principal.external_client_id)


def _authorize(
    session: Session,
    principal: ExternalClientPrincipal,
    *,
    action: str,
) -> None:
    decision = authorize(
        AuthorizationContext(
            actor_kind=ActorKind.EXTERNAL_CLIENT,
            actor_id=principal.external_client_id,
            channel=Channel.EXTERNAL_PRODUCT_CLIENT,
            resource="knowledge_fact",
            action=action,
            risk_level=(
                "medium"
                if action in {"create", "update", "confirm", "delete"}
                else "low"
            ),
        )
    )
    if decision.allowed:
        return
    _audit(
        session,
        principal,
        action=action,
        result="denied",
        resource_id=None,
        reason_code=decision.reason_code,
    )
    session.commit()
    raise ApiError(
        status_code=403,
        code="authorization_denied",
        message="External client is not authorized for knowledge fact access.",
    )


def _audit(
    session: Session,
    principal: ExternalClientPrincipal,
    *,
    action: str,
    result: str,
    resource_id: str | None,
    reason_code: str | None = None,
    metadata: dict[str, object | None] | None = None,
) -> None:
    record_audit_event(
        session,
        AuditEventInput(
            event_type=f"knowledge_fact.{action}",
            actor_type="external_client",
            actor_id=principal.external_client_id,
            channel="external_product_client",
            action=action,
            resource_type="knowledge_fact",
            resource_id=resource_id,
            result=result,
            reason_code=reason_code,
            correlation_id=get_correlation_id(),
            metadata=metadata,
        ),
    )


def _fact_payload(
    fact: KnowledgeFact,
    revision: KnowledgeFactRevision,
) -> dict[str, object]:
    current_revision_id = fact.current_revision_id
    if current_revision_id is None:
        raise ApiError(
            500,
            "knowledge_fact_revision_missing",
            "Knowledge fact revision is missing.",
        )
    return {
        "knowledge_fact_id": fact.knowledge_fact_id,
        "fact_key": fact.fact_key,
        "status": fact.status,
        "classification": fact.classification,
        "current_revision_id": current_revision_id,
        "last_confirmed_at": fact.last_confirmed_at,
        "deleted_at": fact.deleted_at,
        "created_at": fact.created_at,
        "updated_at": fact.updated_at,
        "current_revision": {
            "knowledge_fact_revision_id": revision.knowledge_fact_revision_id,
            "revision_number": revision.revision_number,
            "display_value": revision.display_value,
            "content_hash": revision.content_hash,
            "source_type": revision.source_type,
            "source_reference": revision.source_reference,
            "provenance_summary": revision.provenance_summary,
            "is_volatile": revision.is_volatile,
            "confirmed_at": revision.confirmed_at,
            "created_at": revision.created_at,
        },
    }
