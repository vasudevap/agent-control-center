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
from atlas_api.models.knowledge import KnowledgeAnswer, KnowledgeQuestion
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.knowledge_facts import (
    begin_idempotent_operation,
    complete_idempotent_operation,
    resolve_owner_user_id,
)
from atlas_api.services.knowledge_questions import (
    cancel_question,
    create_question,
    get_question,
    list_questions,
    submit_answer,
)

router = APIRouter(prefix="/api/v1/knowledge/questions", tags=["knowledge"])

ExternalClientDependency = Annotated[
    ExternalClientPrincipal,
    Depends(verify_external_client),
]


class QuestionCreatePayload(BaseModel):
    required_fact_key: str = Field(min_length=1, max_length=160)
    question_text: str = Field(min_length=1, max_length=1000)
    agent_id: str | None = Field(default=None, max_length=64)
    source_reference: str | None = Field(default=None, max_length=240)
    expires_at: datetime | None = None


class AnswerCreatePayload(BaseModel):
    answer_text: str = Field(min_length=1, max_length=4000)
    source_reference: str | None = Field(default=None, max_length=240)


class QuestionPayload(BaseModel):
    knowledge_question_id: str
    status: str
    required_fact_key: str
    question_text: str
    agent_id: str | None
    source_reference: str | None
    correlation_id: str
    expires_at: datetime | None
    answered_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AnswerPayload(BaseModel):
    knowledge_answer_id: str
    knowledge_question_id: str
    validation_status: str
    created_fact_revision_id: str | None
    created_at: datetime


class PageMeta(BaseModel):
    correlation_id: str | None
    next_cursor: str | None = None


class QuestionResponse(BaseModel):
    data: QuestionPayload
    meta: PageMeta


class QuestionListResponse(BaseModel):
    data: list[QuestionPayload]
    meta: PageMeta


class AnswerResponse(BaseModel):
    data: AnswerPayload
    meta: PageMeta


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=201,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def create_knowledge_question(
    payload: QuestionCreatePayload,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    payload_dict = payload.model_dump(mode="json")
    with session_factory() as session:
        owner_user_id = _authorized_owner(session, principal, action="create")
        idem = begin_idempotent_operation(
            session,
            actor_id=principal.external_client_id,
            operation="knowledge_question.create",
            idempotency_key=key,
            payload=payload_dict,
            resource_type="knowledge_question",
        )
        if idem.replayed and idem.record.resource_id is not None:
            question = get_question(
                session,
                owner_user_id=owner_user_id,
                question_id=idem.record.resource_id,
            )
        else:
            question = create_question(
                session,
                owner_user_id=owner_user_id,
                required_fact_key=payload.required_fact_key,
                question_text=payload.question_text,
                agent_id=payload.agent_id,
                source_reference=payload.source_reference,
                expires_at=payload.expires_at,
                correlation_id=get_correlation_id() or "correlation_unavailable",
            )
            complete_idempotent_operation(
                idem.record,
                resource_id=question.knowledge_question_id,
            )
        _audit(
            session,
            principal,
            action="create",
            result="succeeded",
            resource_id=question.knowledge_question_id,
            metadata={"idempotent_replay": idem.replayed},
        )
        session.commit()
        return success_payload(
            _question_payload(question),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get(
    "",
    response_model=QuestionListResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def list_knowledge_questions(
    request: Request,
    principal: ExternalClientDependency,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str, Query(min_length=1, max_length=40)] = "pending",
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(session, principal, action="list")
        page = list_questions(
            session,
            owner_user_id=owner_user_id,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status=status,
        )
        _audit(
            session,
            principal,
            action="list",
            result="succeeded",
            resource_id=None,
            metadata={"count": len(page.questions), "status": status},
        )
        session.commit()
        return success_payload(
            [_question_payload(question) for question in page.questions],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_knowledge_question(
    question_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(session, principal, action="read")
        question = get_question(
            session,
            owner_user_id=owner_user_id,
            question_id=question_id,
        )
        _audit(
            session,
            principal,
            action="read",
            result="succeeded",
            resource_id=question.knowledge_question_id,
        )
        session.commit()
        return success_payload(
            _question_payload(question),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post(
    "/{question_id}/cancel",
    response_model=QuestionResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def cancel_knowledge_question(
    question_id: str,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(session, principal, action="cancel")
        question = cancel_question(
            session,
            owner_user_id=owner_user_id,
            question_id=question_id,
        )
        _audit(
            session,
            principal,
            action="cancel",
            result="succeeded",
            resource_id=question.knowledge_question_id,
        )
        session.commit()
        return success_payload(
            _question_payload(question),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post(
    "/{question_id}/answers",
    response_model=AnswerResponse,
    status_code=201,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def answer_knowledge_question(
    question_id: str,
    payload: AnswerCreatePayload,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    payload_dict = {"question_id": question_id, **payload.model_dump(mode="json")}
    with session_factory() as session:
        owner_user_id = _authorized_owner(session, principal, action="answer")
        idem = begin_idempotent_operation(
            session,
            actor_id=principal.external_client_id,
            operation="knowledge_question.answer",
            idempotency_key=key,
            payload=payload_dict,
            resource_type="knowledge_answer",
        )
        if idem.replayed and idem.record.resource_id is not None:
            _question = get_question(
                session,
                owner_user_id=owner_user_id,
                question_id=question_id,
            )
            answer = session.get(KnowledgeAnswer, idem.record.resource_id)
            if answer is None:
                raise ApiError(
                    500,
                    "knowledge_answer_missing",
                    "Knowledge answer is missing.",
                )
        else:
            _question, answer = submit_answer(
                session,
                owner_user_id=owner_user_id,
                question_id=question_id,
                answer_text=payload.answer_text,
                source_reference=payload.source_reference,
            )
            complete_idempotent_operation(
                idem.record,
                resource_id=answer.knowledge_answer_id,
            )
        _audit(
            session,
            principal,
            action="answer",
            result="succeeded",
            resource_id=question_id,
            metadata={"idempotent_replay": idem.replayed},
        )
        session.commit()
        return success_payload(
            _answer_payload(answer),
            meta={"correlation_id": get_correlation_id()},
        )


def _require_session_factory(request: Request) -> Callable[[], Session]:
    session_factory = cast(
        "Callable[[], Session] | None",
        request.app.state.session_factory,
    )
    if session_factory is None:
        raise ApiError(
            503,
            "knowledge_question_store_not_configured",
            "Knowledge question storage is not configured.",
        )
    return session_factory


def _authorized_owner(
    session: Session,
    principal: ExternalClientPrincipal,
    *,
    action: str,
) -> str:
    decision = authorize(
        AuthorizationContext(
            actor_kind=ActorKind.EXTERNAL_CLIENT,
            actor_id=principal.external_client_id,
            channel=Channel.EXTERNAL_PRODUCT_CLIENT,
            resource="knowledge_question",
            action=action,
            risk_level=(
                "medium" if action in {"create", "answer", "cancel"} else "low"
            ),
        )
    )
    if not decision.allowed:
        raise ApiError(403, "authorization_denied", "Request is not authorized.")
    return resolve_owner_user_id(session, principal.external_client_id)


def _audit(
    session: Session,
    principal: ExternalClientPrincipal,
    *,
    action: str,
    result: str,
    resource_id: str | None,
    metadata: dict[str, object | None] | None = None,
) -> None:
    record_audit_event(
        session,
        AuditEventInput(
            event_type=f"knowledge_question.{action}",
            actor_type="external_client",
            actor_id=principal.external_client_id,
            channel="external_product_client",
            action=action,
            resource_type="knowledge_question",
            resource_id=resource_id,
            result=result,
            correlation_id=get_correlation_id(),
            metadata=metadata,
        ),
    )


def _question_payload(question: KnowledgeQuestion) -> dict[str, object]:
    return {
        "knowledge_question_id": question.knowledge_question_id,
        "status": question.status,
        "required_fact_key": question.required_fact_key,
        "question_text": question.question_text,
        "agent_id": question.agent_id,
        "source_reference": question.source_reference,
        "correlation_id": question.correlation_id,
        "expires_at": question.expires_at,
        "answered_at": question.answered_at,
        "cancelled_at": question.cancelled_at,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
    }


def _answer_payload(answer: KnowledgeAnswer) -> dict[str, object]:
    return {
        "knowledge_answer_id": answer.knowledge_answer_id,
        "knowledge_question_id": answer.knowledge_question_id,
        "validation_status": answer.validation_status,
        "created_fact_revision_id": answer.created_fact_revision_id,
        "created_at": answer.created_at,
    }
