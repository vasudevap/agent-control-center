from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated, Any, Literal, cast

from fastapi import APIRouter, Cookie, Depends, Header, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.authorization import (
    ActorKind,
    AuthorizationContext,
    Channel,
    authorize,
)
from atlas_api.core.config import Settings
from atlas_api.core.contracts import (
    PaginationParameters,
    success_payload,
    validate_idempotency_key,
)
from atlas_api.core.correlation import get_correlation_id
from atlas_api.core.errors import ApiError
from atlas_api.core.owner_sessions import (
    SESSION_COOKIE_NAME,
    OwnerSessionError,
    OwnerSessionPrincipal,
    clear_owner_session_cookies,
    revoke_owner_session,
    rotate_owner_session_csrf,
    validate_owner_session,
)
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_client import User
from atlas_api.models.idempotency import ApiIdempotencyRecord
from atlas_api.services.agent_registry import (
    enroll_owner_agent,
    get_owner_agent_registration,
    list_agent_registrations,
    update_owner_agent_metadata,
)
from atlas_api.services.approval_contracts import get_approval, list_approvals
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.connectors import (
    check_connection_health,
    list_connections,
    list_connector_types,
    start_oauth_connection,
)
from atlas_api.services.runs import get_run, list_runs
from atlas_api.services.smoke_seed import (
    RuntimeSmokeSeedResult,
    seed_hosted_runtime_smoke,
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


class ConnectorOAuthStartRequest(BaseModel):
    connector_type: str = Field(min_length=1, max_length=80)
    requested_scopes: list[str] = Field(min_length=1, max_length=8)
    redirect_uri: str = Field(min_length=8, max_length=500)


class RuntimeSmokeSeedRequest(BaseModel):
    scope: Literal["hosted_mvp_smoke"] = "hosted_mvp_smoke"


class AgentEnrollmentRequest(BaseModel):
    slug: str = Field(min_length=3, max_length=120)
    display_name: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=500)
    environment: str = Field(min_length=1, max_length=80)
    monitoring_mode: Literal["heartbeat", "activity_only"] = "heartbeat"
    heartbeat_interval_seconds: int | None = Field(default=60, ge=30, le=3600)
    tags: list[str] = Field(default_factory=list, max_length=12)
    repository_url: str | None = Field(default=None, max_length=500)
    deployment_url: str | None = Field(default=None, max_length=500)
    expected_version: str | None = Field(default=None, max_length=80)


class AgentMetadataUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    environment: str | None = Field(default=None, min_length=1, max_length=80)
    tags: list[str] | None = Field(default=None, max_length=12)
    repository_url: str | None = Field(default=None, max_length=500)
    deployment_url: str | None = Field(default=None, max_length=500)
    expected_version: str | None = Field(default=None, max_length=80)


def _settings_from_request(request: Request) -> Settings:
    return cast("Settings", request.app.state.settings)


def _session_factory_from_request(request: Request) -> Callable[[], Session] | None:
    return cast("Callable[[], Session] | None", request.app.state.session_factory)


SettingsDependency = Annotated[Settings, Depends(_settings_from_request)]


@router.get("/session")
def read_dashboard_session(
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _owner_principal(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
        )
        user = _active_user(session, principal.user_id)
        csrf_token = rotate_owner_session_csrf(session, principal=principal)
        _audit_dashboard(
            session,
            principal,
            action="read_session",
            result="succeeded",
            resource_type="owner_session",
            resource_id=principal.owner_session_id,
        )
        session.commit()
        return success_payload(
            {
                "authenticated": True,
                "user": _user_payload(user),
                "csrf_token": csrf_token,
            },
            meta={"correlation_id": get_correlation_id()},
        )


@router.post("/session/logout")
def logout_dashboard_session(
    response: Response,
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    csrf_token: Annotated[str | None, Header(alias="X-Atlas-CSRF-Token")] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _owner_principal(
            session,
            session_token=session_token,
            csrf_token=csrf_token,
            require_csrf=True,
        )
        revoke_owner_session(
            session,
            session_token=session_token,
            now=datetime.now(UTC),
        )
        _audit_dashboard(
            session,
            principal,
            action="logout",
            result="succeeded",
            resource_type="owner_session",
            resource_id=principal.owner_session_id,
        )
        session.commit()
    clear_owner_session_cookies(response)
    return success_payload(
        {"authenticated": False},
        meta={"correlation_id": get_correlation_id()},
    )


@router.get("/connectors")
def read_dashboard_connectors(
    request: Request,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="connector",
            action="list",
            risk_level="low",
        )
        descriptors = list_connector_types(
            session,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status="active",
        )
        connections = list_connections(
            session,
            owner_user_id=principal.user_id,
            pagination=PaginationParameters(cursor=None, limit=100),
        )
        _audit_dashboard(
            session,
            principal,
            action="list_connectors",
            result="succeeded",
            resource_type="connector",
            resource_id=None,
            metadata={
                "descriptor_count": len(descriptors.connectors),
                "connection_count": len(connections.connections),
            },
        )
        session.commit()
        return success_payload(
            {
                "descriptors": [
                    _connector_payload(item) for item in descriptors.connectors
                ],
                "connections": [
                    _connection_payload(item) for item in connections.connections
                ],
            },
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": descriptors.next_cursor,
            },
        )


@router.get("/agents")
def read_dashboard_agents(
    request: Request,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str | None, Query(min_length=1, max_length=40)] = "active",
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="agent",
            action="list",
            risk_level="low",
        )
        page = list_agent_registrations(
            session,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status=status,
            active_surface_only=True,
            owner_user_id=principal.user_id,
        )
        _audit_dashboard(
            session,
            principal,
            action="list_agents",
            result="succeeded",
            resource_type="agent",
            resource_id=None,
            metadata={"agent_count": len(page.agents)},
        )
        session.commit()
        return success_payload(
            [_agent_payload(item) for item in page.agents],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@router.post("/agents")
def enroll_dashboard_agent(
    payload: AgentEnrollmentRequest,
    request: Request,
    settings: SettingsDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    csrf_token: Annotated[str | None, Header(alias="X-Atlas-CSRF-Token")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=csrf_token,
            require_csrf=True,
            resource="agent",
            action="create",
            risk_level="medium",
        )
        _record_enrollment_idempotency(
            session,
            owner_user_id=principal.user_id,
            idempotency_key=key,
            payload=payload.model_dump(mode="json"),
        )
        result = enroll_owner_agent(
            session,
            owner_user_id=principal.user_id,
            settings=settings,
            slug=payload.slug,
            display_name=payload.display_name,
            description=payload.description,
            environment=payload.environment,
            monitoring_mode=payload.monitoring_mode,
            heartbeat_interval_seconds=payload.heartbeat_interval_seconds,
            tags=payload.tags,
            repository_url=payload.repository_url,
            deployment_url=payload.deployment_url,
            expected_version=payload.expected_version,
        )
        _audit_dashboard(
            session,
            principal,
            action="enroll_agent",
            result="succeeded",
            resource_type="agent",
            resource_id=result.agent.agent_id,
            metadata={
                "idempotency_key": key,
                "credential_id": result.issued_credential.credential.credential_id,
            },
        )
        session.commit()
        return success_payload(
            {
                "agent": _agent_payload(result.agent),
                "credential": {
                    "credential_id": (
                        result.issued_credential.credential.credential_id
                    ),
                    "credential_lookup_id": (
                        result.issued_credential.credential.credential_lookup_id
                    ),
                    "scope": result.issued_credential.credential.scope,
                    "plaintext_token": result.issued_credential.plaintext_token,
                },
            },
            meta={"correlation_id": get_correlation_id()},
        )


@router.get("/agents/{agent_id}")
def read_dashboard_agent(
    agent_id: str,
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="agent",
            action="read",
            risk_level="low",
        )
        agent = get_owner_agent_registration(
            session,
            owner_user_id=principal.user_id,
            agent_id=agent_id,
        )
        session.commit()
        return success_payload(
            _agent_payload(agent),
            meta={"correlation_id": get_correlation_id()},
        )


@router.patch("/agents/{agent_id}")
def update_dashboard_agent(
    agent_id: str,
    payload: AgentMetadataUpdateRequest,
    request: Request,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    csrf_token: Annotated[str | None, Header(alias="X-Atlas-CSRF-Token")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=csrf_token,
            require_csrf=True,
            resource="agent",
            action="update",
            risk_level="medium",
        )
        agent = update_owner_agent_metadata(
            session,
            owner_user_id=principal.user_id,
            agent_id=agent_id,
            **payload.model_dump(exclude_unset=True),
        )
        _audit_dashboard(
            session,
            principal,
            action="update_agent",
            result="succeeded",
            resource_type="agent",
            resource_id=agent.agent_id,
            metadata={"idempotency_key": key},
        )
        session.commit()
        return success_payload(
            _agent_payload(agent),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post("/connectors/oauth/start")
def start_dashboard_connector_oauth(
    payload: ConnectorOAuthStartRequest,
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    csrf_token: Annotated[str | None, Header(alias="X-Atlas-CSRF-Token")] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    settings = _settings_from_request(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=csrf_token,
            require_csrf=True,
            resource="connector",
            action="start_oauth",
            risk_level="medium",
        )
        result = start_oauth_connection(
            session,
            owner_user_id=principal.user_id,
            connector_type=payload.connector_type,
            requested_scopes=payload.requested_scopes,
            redirect_uri=payload.redirect_uri,
            settings=settings,
        )
        _audit_dashboard(
            session,
            principal,
            action="start_connector_oauth",
            result="succeeded",
            resource_type="connector",
            resource_id=result.oauth_state_id,
            metadata={
                "connector_type": result.connector_type,
                "scope_count": len(result.requested_scopes),
            },
        )
        session.commit()
        return success_payload(
            {
                "oauth_state_id": result.oauth_state_id,
                "connector_type": result.connector_type,
                "authorization_url": result.authorization_url,
                "requested_scopes": result.requested_scopes,
                "expires_at": result.expires_at,
            },
            meta={"correlation_id": get_correlation_id()},
        )


@router.post("/connections/{connection_id}/health")
def check_dashboard_connection_health(
    connection_id: str,
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    csrf_token: Annotated[str | None, Header(alias="X-Atlas-CSRF-Token")] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=csrf_token,
            require_csrf=True,
            resource="connector",
            action="read_health",
            risk_level="low",
        )
        connection = check_connection_health(
            session,
            owner_user_id=principal.user_id,
            connection_id=connection_id,
        )
        _audit_dashboard(
            session,
            principal,
            action="check_connection_health",
            result="succeeded",
            resource_type="connector_connection",
            resource_id=connection.connection_id,
            metadata={"health_status": connection.health_status},
        )
        session.commit()
        return success_payload(
            _connection_payload(connection),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get("/runs")
def read_dashboard_runs(
    request: Request,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str | None, Query(min_length=1, max_length=40)] = None,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="agent_run",
            action="list",
            risk_level="low",
        )
        page = list_runs(
            session,
            owner_user_id=principal.user_id,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status=status,
        )
        session.commit()
        return success_payload(
            [_run_payload(item) for item in page.runs],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@router.get("/runs/{run_id}")
def read_dashboard_run(
    run_id: str,
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="agent_run",
            action="read",
            risk_level="low",
        )
        run = get_run(session, owner_user_id=principal.user_id, run_id=run_id)
        session.commit()
        return success_payload(
            _run_payload(run),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post("/smoke-seed")
def seed_dashboard_runtime_smoke(
    payload: RuntimeSmokeSeedRequest,
    request: Request,
    settings: SettingsDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    csrf_token: Annotated[str | None, Header(alias="X-Atlas-CSRF-Token")] = None,
) -> dict[str, object]:
    from atlas_api.core.contracts import validate_idempotency_key

    if not settings.enable_synthetic_smoke_seed:
        raise ApiError(
            404,
            "dashboard_smoke_seed_disabled",
            "Synthetic dashboard smoke seeding is disabled.",
        )

    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=csrf_token,
            require_csrf=True,
            resource="runtime_smoke_seed",
            action="create",
            risk_level="medium",
        )
        result = seed_hosted_runtime_smoke(
            session,
            owner_user_id=principal.user_id,
            idempotency_key=validate_idempotency_key(idempotency_key),
            correlation_id=get_correlation_id() or "correlation_unavailable",
        )
        _audit_dashboard(
            session,
            principal,
            action="seed_runtime_smoke",
            result="succeeded",
            resource_type="runtime_smoke_seed",
            resource_id=result.run.run_id,
            metadata={
                "run_id": result.run.run_id,
                "count": len(result.connections),
                "status": result.run.status,
            },
        )
        session.commit()
        return success_payload(
            _smoke_seed_payload(result),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get("/approvals")
def read_dashboard_approvals(
    request: Request,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str, Query(min_length=1, max_length=40)] = "pending",
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="approval",
            action="list",
            risk_level="low",
        )
        page = list_approvals(
            session,
            owner_user_id=principal.user_id,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status=status,
        )
        session.commit()
        return success_payload(
            [_approval_summary(item) for item in page.approvals],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@router.get("/approvals/{approval_id}")
def read_dashboard_approval(
    approval_id: str,
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="approval",
            action="read_evidence",
            risk_level="low",
        )
        approval = get_approval(
            session,
            owner_user_id=principal.user_id,
            approval_id=approval_id,
        )
        session.commit()
        return success_payload(
            _approval_evidence(approval),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get("/audit")
def read_dashboard_audit(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="audit",
            action="list",
            risk_level="low",
        )
        events = list(
            session.scalars(
                select(AuditEvent).order_by(AuditEvent.occurred_at.desc()).limit(limit)
            )
        )
        _audit_dashboard(
            session,
            principal,
            action="list_audit",
            result="succeeded",
            resource_type="audit_event",
            resource_id=None,
            metadata={"count": len(events)},
        )
        session.commit()
        return success_payload(
            [_audit_payload(event) for event in events],
            meta={"correlation_id": get_correlation_id(), "next_cursor": None},
        )


@router.get("/monitoring")
def read_dashboard_monitoring(
    request: Request,
    settings: SettingsDependency,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_dashboard_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="monitoring",
            action="read",
            risk_level="low",
        )
        problems = settings.readiness_problems()
        agent_page = list_agent_registrations(
            session,
            pagination=PaginationParameters(cursor=None, limit=100),
            status=None,
            active_surface_only=True,
            owner_user_id=principal.user_id,
        )
        session.commit()
        return success_payload(
            {
                "readiness_status": "ready" if not problems else "not_ready",
                "readiness_problem_count": len(problems),
                "agent_count": len(agent_page.agents),
                "runtime_origin": "atlas-api",
            },
            meta={"correlation_id": get_correlation_id()},
        )


def _require_session_factory(request: Request) -> Callable[[], Session]:
    session_factory = _session_factory_from_request(request)
    if session_factory is None:
        raise ApiError(
            503,
            "dashboard_store_not_configured",
            "Dashboard storage is not configured.",
        )
    return session_factory


def _owner_principal(
    session: Session,
    *,
    session_token: str | None,
    csrf_token: str | None,
    require_csrf: bool,
) -> OwnerSessionPrincipal:
    try:
        return validate_owner_session(
            session,
            session_token=session_token,
            csrf_token=csrf_token,
            require_csrf=require_csrf,
            now=datetime.now(UTC),
        )
    except OwnerSessionError as exc:
        raise ApiError(401, str(exc), "Owner session is not authorized.") from exc


def _authorized_dashboard_owner(
    session: Session,
    *,
    session_token: str | None,
    csrf_token: str | None,
    require_csrf: bool,
    resource: str,
    action: str,
    risk_level: str,
) -> OwnerSessionPrincipal:
    principal = _owner_principal(
        session,
        session_token=session_token,
        csrf_token=csrf_token,
        require_csrf=require_csrf,
    )
    decision = authorize(
        AuthorizationContext(
            actor_kind=ActorKind.HUMAN_OWNER,
            actor_id=principal.user_id,
            channel=Channel.DASHBOARD,
            resource=resource,
            action=action,
            risk_level=risk_level,
        )
    )
    if not decision.allowed:
        raise ApiError(403, decision.reason_code, "Dashboard action is not authorized.")
    return principal


def _active_user(session: Session, user_id: str) -> User:
    user = session.get(User, user_id)
    if user is None or user.status != "active":
        raise ApiError(401, "owner_user_inactive", "Owner user is not active.")
    return user


def _audit_dashboard(
    session: Session,
    principal: OwnerSessionPrincipal,
    *,
    action: str,
    result: str,
    resource_type: str,
    resource_id: str | None,
    metadata: dict[str, object | None] | None = None,
) -> None:
    record_audit_event(
        session,
        AuditEventInput(
            event_type=f"dashboard.{action}",
            actor_type="human_owner",
            actor_id=principal.user_id,
            channel="dashboard",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            correlation_id=get_correlation_id(),
            metadata=metadata,
        ),
    )


def _record_enrollment_idempotency(
    session: Session,
    *,
    owner_user_id: str,
    idempotency_key: str,
    payload: dict[str, object],
) -> None:
    request_hash = hashlib.sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    existing = session.scalar(
        select(ApiIdempotencyRecord).where(
            ApiIdempotencyRecord.actor_id == owner_user_id,
            ApiIdempotencyRecord.operation == "dashboard.enroll_agent",
            ApiIdempotencyRecord.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        raise ApiError(
            409,
            "agent_enrollment_idempotency_replay_unavailable",
            "Agent enrollment credentials cannot be replayed.",
        )
    session.add(
        ApiIdempotencyRecord(
            actor_id=owner_user_id,
            operation="dashboard.enroll_agent",
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            resource_type="agent",
            resource_id=None,
        )
    )


def _user_payload(user: User) -> dict[str, object]:
    return {
        "user_id": user.user_id,
        "email": user.email,
        "display_name": user.display_name,
        "identity_provider": user.identity_provider,
        "status": user.status,
    }


def _connector_payload(connector: Any) -> dict[str, object]:
    return {
        "connector_type": connector.connector_type,
        "display_name": connector.display_name,
        "version": connector.version,
        "authentication_type": connector.authentication_type,
        "status": connector.status,
        "supported_operations": connector.supported_operations,
        "required_scopes": connector.required_scopes,
        "risk_by_operation": connector.risk_by_operation,
        "supports_health_check": connector.supports_health_check,
        "supports_revocation": connector.supports_revocation,
        "supports_refresh": connector.supports_refresh,
    }


def _connection_payload(connection: Any) -> dict[str, object]:
    return {
        "connection_id": connection.connection_id,
        "connector_type": connection.connector_type,
        "display_name": connection.display_name,
        "account_identifier": connection.account_identifier,
        "status": connection.status,
        "granted_scopes": connection.granted_scopes,
        "health_status": connection.health_status,
        "last_success_at": connection.last_success_at,
        "last_failure_at": connection.last_failure_at,
        "last_health_checked_at": connection.last_health_checked_at,
        "last_error_code": connection.last_error_code,
    }


def _agent_payload(agent: Any) -> dict[str, object]:
    return {
        "agent_id": agent.agent_id,
        "slug": agent.slug,
        "display_name": agent.display_name,
        "description": agent.description,
        "version": agent.version,
        "status": agent.status,
        "risk_level": agent.risk_level,
        "capabilities": agent.capabilities,
        "allowed_tools": agent.allowed_tools,
        "required_connectors": agent.required_connectors,
        "supports_manual_run": agent.supports_manual_run,
        "supports_scheduled_run": agent.supports_scheduled_run,
        "health_status": agent.health_status,
        "health_checked_at": agent.health_checked_at,
        "last_error_code": agent.last_error_code,
        "owner_user_id": agent.owner_user_id,
        "registration_source": agent.registration_source,
        "active_surface_visible": agent.active_surface_visible,
        "lifecycle_status": agent.lifecycle_status,
        "environment": agent.environment,
        "monitoring_mode": agent.monitoring_mode,
        "heartbeat_interval_seconds": agent.heartbeat_interval_seconds,
        "tags": agent.tags,
        "repository_url": agent.repository_url,
        "deployment_url": agent.deployment_url,
        "expected_version": agent.expected_version,
        "observed_health": agent.observed_health,
        "reported_health": agent.reported_health,
        "last_agent_version": agent.last_agent_version,
        "last_build_sha": agent.last_build_sha,
    }


def _run_payload(run: Any) -> dict[str, object]:
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


def _approval_summary(approval: Any) -> dict[str, object]:
    return {
        "approval_id": approval.approval_id,
        "status": approval.status,
        "revision": approval.revision,
        "action_type": approval.action_type,
        "action_reference": approval.action_reference,
        "expires_at": approval.expires_at,
        "created_at": approval.created_at,
    }


def _approval_evidence(approval: Any) -> dict[str, object]:
    return {
        **_approval_summary(approval),
        "action_payload_hash": approval.action_payload_hash,
        "evidence_summary": approval.evidence_summary,
        "decision_context_manifest": approval.decision_context_manifest,
        "continuation_status": approval.continuation_status,
        "superseded_by_approval_id": approval.superseded_by_approval_id,
    }


def _audit_payload(event: AuditEvent) -> dict[str, object]:
    return {
        "audit_event_id": event.audit_event_id,
        "event_type": event.event_type,
        "actor_type": event.actor_type,
        "actor_id": event.actor_id,
        "channel": event.channel,
        "action": event.action,
        "resource_type": event.resource_type,
        "resource_id": event.resource_id,
        "result": event.result,
        "reason_code": event.reason_code,
        "correlation_id": event.correlation_id,
        "redaction_state": event.redaction_state,
        "metadata_json": event.metadata_json,
        "occurred_at": event.occurred_at,
    }


def _smoke_seed_payload(result: RuntimeSmokeSeedResult) -> dict[str, object]:
    return {
        "scope": result.scope,
        "synthetic": result.synthetic,
        "agent": _agent_payload(result.agent),
        "connections": [
            _connection_payload(connection) for connection in result.connections
        ],
        "run": _run_payload(result.run),
        "approval": _approval_summary(result.approval),
    }
