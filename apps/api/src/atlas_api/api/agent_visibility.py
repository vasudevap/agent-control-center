from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated, cast

from fastapi import APIRouter, Cookie, Header, Query, Request
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from atlas_api.core.authorization import (
    ActorKind,
    AuthorizationContext,
    Channel,
    authorize,
)
from atlas_api.core.contracts import success_payload
from atlas_api.core.correlation import get_correlation_id
from atlas_api.core.errors import ApiError
from atlas_api.core.owner_sessions import (
    SESSION_COOKIE_NAME,
    OwnerSessionError,
    OwnerSessionPrincipal,
    validate_owner_session,
)
from atlas_api.models.agent import (
    AgentActivityEvent,
    AgentAlert,
    AgentExecution,
    AgentRegistration,
)
from atlas_api.services.agent_alerts import acknowledge_alert
from atlas_api.services.audit import AuditEventInput, record_audit_event

router = APIRouter(prefix="/api/v1", tags=["agent-visibility"])


def _session_factory_from_request(request: Request) -> Callable[[], Session] | None:
    return cast("Callable[[], Session] | None", request.app.state.session_factory)


@router.get("/executions")
def list_agent_executions(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="agent_execution",
            action="list",
            risk_level="low",
        )
        executions = list(
            session.scalars(
                select(AgentExecution)
                .join(
                    AgentRegistration,
                    AgentRegistration.agent_id == AgentExecution.agent_id,
                )
                .where(
                    AgentRegistration.owner_user_id == principal.user_id,
                    AgentRegistration.active_surface_visible.is_(True),
                )
                .order_by(AgentExecution.last_reported_at.desc())
                .limit(limit)
            )
        )
        return success_payload(
            [_execution_payload(execution) for execution in executions],
            meta={"correlation_id": get_correlation_id(), "next_cursor": None},
        )


@router.get("/executions/{execution_id}")
def read_agent_execution(
    execution_id: str,
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="agent_execution",
            action="read",
            risk_level="low",
        )
        execution = _owned_execution(
            session,
            owner_user_id=principal.user_id,
            execution_id=execution_id,
        )
        return success_payload(
            _execution_payload(execution),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get("/alerts")
def list_agent_alerts(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="agent_alert",
            action="list",
            risk_level="low",
        )
        alerts = list(
            session.scalars(
                select(AgentAlert)
                .join(
                    AgentRegistration,
                    AgentRegistration.agent_id == AgentAlert.agent_id,
                )
                .where(
                    AgentRegistration.owner_user_id == principal.user_id,
                    AgentRegistration.active_surface_visible.is_(True),
                )
                .order_by(AgentAlert.last_seen_at.desc())
                .limit(limit)
            )
        )
        return success_payload(
            [_alert_payload(alert) for alert in alerts],
            meta={"correlation_id": get_correlation_id(), "next_cursor": None},
        )


@router.get("/alerts/{alert_id}")
def read_agent_alert(
    alert_id: str,
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="agent_alert",
            action="read",
            risk_level="low",
        )
        alert = _owned_alert(
            session,
            owner_user_id=principal.user_id,
            alert_id=alert_id,
        )
        return success_payload(
            _alert_payload(alert),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_agent_alert(
    alert_id: str,
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    csrf_token: Annotated[str | None, Header(alias="X-Atlas-CSRF-Token")] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_owner(
            session,
            session_token=session_token,
            csrf_token=csrf_token,
            require_csrf=True,
            resource="agent_alert",
            action="acknowledge",
            risk_level="medium",
        )
        _owned_alert(session, owner_user_id=principal.user_id, alert_id=alert_id)
        alert = acknowledge_alert(
            session,
            alert_id=alert_id,
            acknowledged_by_user_id=principal.user_id,
            now=datetime.now(UTC),
        )
        _audit_visibility_action(
            session,
            principal,
            action="acknowledge_alert",
            result="succeeded",
            resource_type="agent_alert",
            resource_id=alert.alert_id,
            metadata={"condition_key": alert.condition_key},
        )
        session.commit()
        return success_payload(
            _alert_payload(alert),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get("/activity")
def list_agent_activity(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        principal = _authorized_owner(
            session,
            session_token=session_token,
            csrf_token=None,
            require_csrf=False,
            resource="agent_activity",
            action="list",
            risk_level="low",
        )
        events = list(
            session.scalars(
                select(AgentActivityEvent)
                .outerjoin(
                    AgentRegistration,
                    AgentRegistration.agent_id == AgentActivityEvent.agent_id,
                )
                .where(
                    or_(
                        AgentActivityEvent.agent_id.is_(None),
                        (AgentRegistration.owner_user_id == principal.user_id)
                        & (AgentRegistration.active_surface_visible.is_(True)),
                    )
                )
                .order_by(AgentActivityEvent.occurred_at.desc())
                .limit(limit)
            )
        )
        return success_payload(
            [_activity_payload(event) for event in events],
            meta={"correlation_id": get_correlation_id(), "next_cursor": None},
        )


def _require_session_factory(request: Request) -> Callable[[], Session]:
    session_factory = _session_factory_from_request(request)
    if session_factory is None:
        raise ApiError(
            503,
            "agent_visibility_store_not_configured",
            "Agent visibility storage is not configured.",
        )
    return session_factory


def _authorized_owner(
    session: Session,
    *,
    session_token: str | None,
    csrf_token: str | None,
    require_csrf: bool,
    resource: str,
    action: str,
    risk_level: str,
) -> OwnerSessionPrincipal:
    try:
        principal = validate_owner_session(
            session,
            session_token=session_token,
            csrf_token=csrf_token,
            require_csrf=require_csrf,
            now=datetime.now(UTC),
        )
    except OwnerSessionError as exc:
        raise ApiError(401, str(exc), "Owner session is not authorized.") from exc
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


def _owned_execution(
    session: Session,
    *,
    owner_user_id: str,
    execution_id: str,
) -> AgentExecution:
    execution = session.scalar(
        select(AgentExecution)
        .join(AgentRegistration, AgentRegistration.agent_id == AgentExecution.agent_id)
        .where(
            AgentExecution.agent_execution_id == execution_id,
            AgentRegistration.owner_user_id == owner_user_id,
            AgentRegistration.active_surface_visible.is_(True),
        )
    )
    if execution is None:
        raise ApiError(404, "agent_execution_not_found", "Execution was not found.")
    return execution


def _owned_alert(
    session: Session,
    *,
    owner_user_id: str,
    alert_id: str,
) -> AgentAlert:
    alert = session.scalar(
        select(AgentAlert)
        .join(AgentRegistration, AgentRegistration.agent_id == AgentAlert.agent_id)
        .where(
            AgentAlert.alert_id == alert_id,
            AgentRegistration.owner_user_id == owner_user_id,
            AgentRegistration.active_surface_visible.is_(True),
        )
    )
    if alert is None:
        raise ApiError(404, "agent_alert_not_found", "Alert was not found.")
    return alert


def _audit_visibility_action(
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
            event_type=f"agent_visibility.{action}",
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


def _execution_payload(execution: AgentExecution) -> dict[str, object]:
    return {
        "agent_execution_id": execution.agent_execution_id,
        "agent_id": execution.agent_id,
        "external_execution_id": execution.external_execution_id,
        "status": execution.status,
        "trigger": execution.trigger,
        "started_at": execution.started_at,
        "finished_at": execution.finished_at,
        "duration_ms": execution.duration_ms,
        "summary": execution.summary,
        "error_code": execution.error_code,
        "correlation_id": execution.correlation_id,
        "agent_version": execution.agent_version,
        "build_sha": execution.build_sha,
        "first_reported_at": execution.first_reported_at,
        "last_reported_at": execution.last_reported_at,
        "terminal_at": execution.terminal_at,
    }


def _alert_payload(alert: AgentAlert) -> dict[str, object]:
    return {
        "alert_id": alert.alert_id,
        "agent_id": alert.agent_id,
        "condition_key": alert.condition_key,
        "status": alert.status,
        "severity": alert.severity,
        "first_seen_at": alert.first_seen_at,
        "last_seen_at": alert.last_seen_at,
        "acknowledged_at": alert.acknowledged_at,
        "acknowledged_by_user_id": alert.acknowledged_by_user_id,
        "resolved_at": alert.resolved_at,
        "resolved_reason": alert.resolved_reason,
        "evidence_json": alert.evidence_json,
    }


def _activity_payload(event: AgentActivityEvent) -> dict[str, object]:
    return {
        "activity_event_id": event.activity_event_id,
        "agent_id": event.agent_id,
        "source_type": event.source_type,
        "source_id": event.source_id,
        "event_type": event.event_type,
        "severity": event.severity,
        "summary": event.summary,
        "correlation_id": event.correlation_id,
        "actor_type": event.actor_type,
        "actor_id": event.actor_id,
        "metadata_json": event.metadata_json,
        "occurred_at": event.occurred_at,
    }
