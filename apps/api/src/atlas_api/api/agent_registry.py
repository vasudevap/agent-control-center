from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Header, Query, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from atlas_api.core.auth import ExternalClientPrincipal, verify_external_client
from atlas_api.core.authorization import (
    ActorKind,
    AuthorizationContext,
    Channel,
    authorize,
)
from atlas_api.core.config import Settings
from atlas_api.core.contracts import PaginationParameters, success_payload
from atlas_api.core.correlation import get_correlation_id
from atlas_api.core.errors import ApiError
from atlas_api.models.agent import AgentRegistration
from atlas_api.services.agent_alerts import record_security_ingestion_alert
from atlas_api.services.agent_credentials import verify_agent_token
from atlas_api.services.agent_registry import (
    get_agent_registration,
    list_agent_registrations,
)
from atlas_api.services.agent_telemetry import (
    MAX_TELEMETRY_BODY_BYTES,
    accept_execution,
    accept_heartbeat,
    require_credential_for_agent,
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


class HeartbeatCheckPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=80)
    status: str = Field(pattern="^(healthy|degraded|unhealthy)$")
    error_code: str | None = Field(default=None, max_length=120)


class AgentHeartbeatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1, max_length=120)
    contract_version: str = Field(min_length=1, max_length=40)
    sent_at: datetime
    environment: str = Field(min_length=1, max_length=80)
    status: str = Field(pattern="^(healthy|degraded|unhealthy)$")
    checks: list[HeartbeatCheckPayload] = Field(default_factory=list, max_length=20)
    agent_version: str | None = Field(default=None, max_length=80)
    build_sha: str | None = Field(default=None, max_length=80)


class AgentExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str = Field(min_length=1, max_length=40)
    representation_hash: str = Field(min_length=1, max_length=128)
    status: str = Field(
        pattern="^(accepted|running|succeeded|failed|cancelled|timed_out)$"
    )
    trigger: str = Field(min_length=1, max_length=80)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    summary: str | None = Field(default=None, max_length=500)
    error_code: str | None = Field(default=None, max_length=120)
    correlation_id: str | None = Field(default=None, max_length=160)
    agent_version: str | None = Field(default=None, max_length=80)
    build_sha: str | None = Field(default=None, max_length=80)


def _settings_from_request(request: Request) -> Settings:
    return cast("Settings", request.app.state.settings)


SettingsDependency = Annotated[Settings, Depends(_settings_from_request)]


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


@router.post("/{agent_id}/heartbeats", status_code=202)
def ingest_agent_heartbeat(
    agent_id: str,
    payload: AgentHeartbeatRequest,
    request: Request,
    settings: SettingsDependency,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict[str, object]:
    _enforce_body_size(request)
    token = _bearer_token(authorization)
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        credential = verify_agent_token(session, token=token, settings=settings)
        credential, agent = require_credential_for_agent(
            session,
            credential=credential,
            agent_id=agent_id,
        )
        try:
            accepted = accept_heartbeat(
                session,
                agent=agent,
                credential=credential,
                event_id=payload.event_id,
                contract_version=payload.contract_version,
                sent_at=payload.sent_at,
                environment=payload.environment,
                reported_status=cast(Any, payload.status),
                checks=[item.model_dump(mode="json") for item in payload.checks],
                agent_version=payload.agent_version,
                build_sha=payload.build_sha,
                payload=payload.model_dump(mode="json"),
            )
        except ApiError as error:
            _persist_security_ingestion_rejection(
                session,
                agent=agent,
                error=error,
            )
            raise
        session.commit()
        return success_payload(
            {
                "heartbeat_id": accepted.heartbeat.heartbeat_id,
                "agent_id": accepted.heartbeat.agent_id,
                "event_id": accepted.heartbeat.event_id,
                "received_at": accepted.heartbeat.received_at,
                "replayed": accepted.replayed,
            },
            meta={"correlation_id": get_correlation_id()},
        )


@router.put("/{agent_id}/executions/{execution_id}")
def ingest_agent_execution(
    agent_id: str,
    execution_id: str,
    payload: AgentExecutionRequest,
    request: Request,
    response: Response,
    settings: SettingsDependency,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict[str, object]:
    _enforce_body_size(request)
    token = _bearer_token(authorization)
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        credential = verify_agent_token(session, token=token, settings=settings)
        credential, agent = require_credential_for_agent(
            session,
            credential=credential,
            agent_id=agent_id,
        )
        try:
            accepted = accept_execution(
                session,
                agent=agent,
                credential=credential,
                external_execution_id=execution_id,
                contract_version=payload.contract_version,
                representation_hash=payload.representation_hash,
                status=payload.status,
                trigger=payload.trigger,
                started_at=payload.started_at,
                finished_at=payload.finished_at,
                duration_ms=payload.duration_ms,
                summary=payload.summary,
                error_code=payload.error_code,
                correlation_id=payload.correlation_id,
                agent_version=payload.agent_version,
                build_sha=payload.build_sha,
                payload=payload.model_dump(mode="json"),
            )
        except ApiError as error:
            _persist_security_ingestion_rejection(
                session,
                agent=agent,
                error=error,
            )
            raise
        response.status_code = 201 if accepted.created else 200
        session.commit()
        return success_payload(
            {
                "agent_execution_id": accepted.execution.agent_execution_id,
                "agent_id": accepted.execution.agent_id,
                "external_execution_id": accepted.execution.external_execution_id,
                "status": accepted.execution.status,
                "created": accepted.created,
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


def _bearer_token(authorization: str | None) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise ApiError(401, "agent_credential_missing", "Agent credential missing.")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise ApiError(401, "agent_credential_missing", "Agent credential missing.")
    return token


def _enforce_body_size(request: Request) -> None:
    content_length = request.headers.get("content-length")
    if content_length is None:
        return
    try:
        size = int(content_length)
    except ValueError:
        raise ApiError(
            422,
            "agent_telemetry_content_length_invalid",
            "Content length is invalid.",
        ) from None
    if size > MAX_TELEMETRY_BODY_BYTES:
        raise ApiError(
            413,
            "agent_telemetry_payload_too_large",
            "Telemetry payload is too large.",
        )


def _persist_security_ingestion_rejection(
    session: Session,
    *,
    agent: AgentRegistration,
    error: ApiError,
) -> None:
    categories = {
        "agent_contract_version_unsupported": "contract_version",
        "agent_telemetry_secret_rejected": "secret_pattern",
    }
    category = categories.get(error.code)
    if category is None:
        return
    record_security_ingestion_alert(
        session,
        agent_id=agent.agent_id,
        category=category,
        reason_code=error.code,
    )
    session.commit()


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
