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
from atlas_api.models.run import AgentRun
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.knowledge_facts import resolve_owner_user_id
from atlas_api.services.runs import cancel_run, create_manual_run, get_run, list_runs

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])

ExternalClientDependency = Annotated[
    ExternalClientPrincipal,
    Depends(verify_external_client),
]


class RunCreatePayload(BaseModel):
    agent_id: str = Field(min_length=1, max_length=64)
    timeout_seconds: int = Field(default=300, ge=30, le=3600)


class RunPayload(BaseModel):
    run_id: str
    agent_id: str
    status: str
    trigger_source: str
    correlation_id: str
    queue_job_id: str | None
    timeout_seconds: int
    retry_count: int
    failure_reason_code: str | None
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PageMeta(BaseModel):
    correlation_id: str | None
    next_cursor: str | None = None


class RunResponse(BaseModel):
    data: RunPayload
    meta: PageMeta


class RunListResponse(BaseModel):
    data: list[RunPayload]
    meta: PageMeta


@router.post(
    "",
    response_model=RunResponse,
    status_code=201,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def create_run(
    payload: RunCreatePayload,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(session, principal, action="create")
        run = create_manual_run(
            session,
            owner_user_id=owner_user_id,
            agent_id=payload.agent_id,
            idempotency_key=key,
            correlation_id=get_correlation_id() or "correlation_unavailable",
            timeout_seconds=payload.timeout_seconds,
        )
        _audit(
            session,
            principal,
            action="create",
            result="succeeded",
            resource_id=run.run_id,
            metadata={"agent_id": run.agent_id, "status": run.status},
        )
        session.commit()
        return success_payload(
            _run_payload(run),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get(
    "",
    response_model=RunListResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def list_agent_runs(
    request: Request,
    principal: ExternalClientDependency,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str | None, Query(min_length=1, max_length=40)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(session, principal, action="list")
        page = list_runs(
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
            metadata={"count": len(page.runs), "status": status},
        )
        session.commit()
        return success_payload(
            [_run_payload(run) for run in page.runs],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@router.get(
    "/{run_id}",
    response_model=RunResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_run(
    run_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(session, principal, action="read")
        run = get_run(session, owner_user_id=owner_user_id, run_id=run_id)
        _audit(
            session,
            principal,
            action="read",
            result="succeeded",
            resource_id=run.run_id,
        )
        session.commit()
        return success_payload(
            _run_payload(run),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post(
    "/{run_id}/cancel",
    response_model=RunResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def cancel_agent_run(
    run_id: str,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(session, principal, action="cancel")
        run = cancel_run(session, owner_user_id=owner_user_id, run_id=run_id)
        _audit(
            session,
            principal,
            action="cancel",
            result="succeeded",
            resource_id=run.run_id,
        )
        session.commit()
        return success_payload(
            _run_payload(run),
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
            "run_store_not_configured",
            "Run storage is not configured.",
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
            resource="agent_run",
            action=action,
            risk_level="medium" if action in {"create", "cancel"} else "low",
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
            event_type=f"agent_run.{action}",
            actor_type="external_client",
            actor_id=principal.external_client_id,
            channel="external_product_client",
            action=action,
            resource_type="agent_run",
            resource_id=resource_id,
            result=result,
            correlation_id=get_correlation_id(),
            metadata=metadata,
        ),
    )


def _run_payload(run: AgentRun) -> dict[str, object]:
    return {
        "run_id": run.run_id,
        "agent_id": run.agent_id,
        "status": run.status,
        "trigger_source": run.trigger_source,
        "correlation_id": run.correlation_id,
        "queue_job_id": run.queue_job_id,
        "timeout_seconds": run.timeout_seconds,
        "retry_count": run.retry_count,
        "failure_reason_code": run.failure_reason_code,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "cancelled_at": run.cancelled_at,
        "created_at": run.created_at,
        "updated_at": run.updated_at,
    }
