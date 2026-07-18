from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from atlas_api.core.auth import ExternalClientPrincipal, verify_external_client
from atlas_api.core.authorization import (
    ActorKind,
    AuthorizationContext,
    Channel,
    authorize,
)
from atlas_api.core.contracts import PaginationParameters, success_payload
from atlas_api.core.correlation import get_correlation_id
from atlas_api.core.errors import ApiError
from atlas_api.models.agent import AgentRegistration
from atlas_api.services.agent_registry import (
    get_agent_registration,
    list_agent_registrations,
)
from atlas_api.services.audit import AuditEventInput, record_audit_event

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


class AgentDescriptorPayload(BaseModel):
    agent_id: str
    slug: str
    display_name: str
    description: str
    version: str
    descriptor_version: int
    status: str
    risk_level: str
    capabilities: list[str]
    allowed_tools: list[str]
    required_connectors: list[str]
    configuration_schema_ref: str | None
    configuration_schema: dict[str, Any]
    supports_manual_run: bool
    supports_scheduled_run: bool
    created_at: datetime
    updated_at: datetime


class AgentStatusPayload(BaseModel):
    agent_id: str
    status: str
    health_status: str
    updated_at: datetime


class AgentHealthPayload(BaseModel):
    agent_id: str
    health_status: str
    health_checked_at: datetime | None
    last_error_code: str | None


class AgentRegistryMeta(BaseModel):
    correlation_id: str | None
    next_cursor: str | None = None


class AgentListResponse(BaseModel):
    data: list[AgentDescriptorPayload]
    meta: AgentRegistryMeta


class AgentDescriptorResponse(BaseModel):
    data: AgentDescriptorPayload
    meta: AgentRegistryMeta


class AgentStatusResponse(BaseModel):
    data: AgentStatusPayload
    meta: AgentRegistryMeta


class AgentHealthResponse(BaseModel):
    data: AgentHealthPayload
    meta: AgentRegistryMeta


ExternalClientDependency = Annotated[
    ExternalClientPrincipal,
    Depends(verify_external_client),
]


def _session_factory_from_request(request: Request) -> Callable[[], Session] | None:
    return cast("Callable[[], Session] | None", request.app.state.session_factory)


@router.get(
    "",
    response_model=AgentListResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def list_agents(
    request: Request,
    principal: ExternalClientDependency,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str | None, Query(min_length=1, max_length=40)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_agent_registry(session, principal, action="list")
        page = list_agent_registrations(
            session,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status=status,
        )
        _record_agent_registry_audit(
            session,
            principal,
            action="list",
            result="succeeded",
            resource_id=None,
            metadata={"count": len(page.agents), "status": status},
        )
        session.commit()
        return success_payload(
            [_descriptor(agent) for agent in page.agents],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@router.get(
    "/{agent_id}",
    response_model=AgentDescriptorResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_agent(
    agent_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_agent_registry(session, principal, action="read")
        agent = get_agent_registration(session, agent_id)
        _record_agent_registry_audit(
            session,
            principal,
            action="read",
            result="succeeded",
            resource_id=agent.agent_id,
        )
        session.commit()
        return success_payload(
            _descriptor(agent),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get(
    "/{agent_id}/status",
    response_model=AgentStatusResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_agent_status(
    agent_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_agent_registry(session, principal, action="read_status")
        agent = get_agent_registration(session, agent_id)
        _record_agent_registry_audit(
            session,
            principal,
            action="read_status",
            result="succeeded",
            resource_id=agent.agent_id,
        )
        session.commit()
        return success_payload(
            {
                "agent_id": agent.agent_id,
                "status": agent.status,
                "health_status": agent.health_status,
                "updated_at": agent.updated_at,
            },
            meta={"correlation_id": get_correlation_id()},
        )


@router.get(
    "/{agent_id}/health",
    response_model=AgentHealthResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_agent_health(
    agent_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_agent_registry(session, principal, action="read_health")
        agent = get_agent_registration(session, agent_id)
        _record_agent_registry_audit(
            session,
            principal,
            action="read_health",
            result="succeeded",
            resource_id=agent.agent_id,
        )
        session.commit()
        return success_payload(
            {
                "agent_id": agent.agent_id,
                "health_status": agent.health_status,
                "health_checked_at": agent.health_checked_at,
                "last_error_code": agent.last_error_code,
            },
            meta={"correlation_id": get_correlation_id()},
        )


def _require_session_factory(request: Request) -> Callable[[], Session]:
    session_factory = _session_factory_from_request(request)
    if session_factory is None:
        raise ApiError(
            status_code=503,
            code="agent_registry_store_not_configured",
            message="Agent registry storage is not configured.",
        )
    return session_factory


def _authorize_agent_registry(
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
            resource="agent_registry",
            action=action,
            risk_level="low",
        )
    )
    if decision.allowed:
        return
    _record_agent_registry_audit(
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
        message="External client is not authorized for agent registry access.",
    )


def _record_agent_registry_audit(
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
            event_type=f"agent_registry.{action}",
            actor_type="external_client",
            actor_id=principal.external_client_id,
            channel="external_product_client",
            action=action,
            resource_type="agent_registration",
            resource_id=resource_id,
            result=result,
            reason_code=reason_code,
            correlation_id=get_correlation_id(),
            metadata=metadata,
        ),
    )


def _descriptor(agent: AgentRegistration) -> dict[str, object]:
    return {
        "agent_id": agent.agent_id,
        "slug": agent.slug,
        "display_name": agent.display_name,
        "description": agent.description,
        "version": agent.version,
        "descriptor_version": agent.descriptor_version,
        "status": agent.status,
        "risk_level": agent.risk_level,
        "capabilities": agent.capabilities,
        "allowed_tools": agent.allowed_tools,
        "required_connectors": agent.required_connectors,
        "configuration_schema_ref": agent.configuration_schema_ref,
        "configuration_schema": agent.configuration_schema,
        "supports_manual_run": agent.supports_manual_run,
        "supports_scheduled_run": agent.supports_scheduled_run,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at,
    }
