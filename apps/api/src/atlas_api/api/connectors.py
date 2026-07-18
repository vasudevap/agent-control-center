from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
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
from atlas_api.models.connector import ConnectorConnection, ConnectorType
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.connectors import (
    check_connection_health,
    complete_oauth_connection,
    get_connection,
    get_connector_type,
    list_connections,
    list_connector_types,
    resolve_connector_owner_user_id,
    revoke_connection,
    start_oauth_connection,
)

router = APIRouter(prefix="/api/v1", tags=["connectors"])


class ConnectorDescriptorPayload(BaseModel):
    connector_type: str
    display_name: str
    version: str
    authentication_type: str
    status: str
    supported_operations: list[str]
    required_scopes: dict[str, list[str]]
    risk_by_operation: dict[str, str]
    supports_health_check: bool
    supports_revocation: bool
    supports_refresh: bool
    provider_docs_reference: str
    configuration_schema: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ConnectorConnectionPayload(BaseModel):
    connection_id: str
    connector_type: str
    display_name: str
    account_identifier: str
    status: str
    granted_scopes: list[str]
    health_status: str
    last_success_at: datetime | None
    last_failure_at: datetime | None
    last_health_checked_at: datetime | None
    last_error_code: str | None
    created_at: datetime
    updated_at: datetime


class OAuthStartRequest(BaseModel):
    requested_scopes: list[str] = Field(min_length=1, max_length=8)
    redirect_uri: str = Field(min_length=8, max_length=500)


class OAuthStartPayload(BaseModel):
    oauth_state_id: str
    connector_type: str
    authorization_url: str
    requested_scopes: list[str]
    expires_at: datetime


class OAuthCallbackRequest(BaseModel):
    state: str = Field(min_length=16, max_length=160)
    authorization_code: str = Field(min_length=1, max_length=512)
    account_identifier: str = Field(min_length=3, max_length=320)
    granted_scopes: list[str] = Field(min_length=1, max_length=8)
    display_name: str | None = Field(default=None, min_length=1, max_length=160)


class ConnectorMeta(BaseModel):
    correlation_id: str | None
    next_cursor: str | None = None


class ConnectorListResponse(BaseModel):
    data: list[ConnectorDescriptorPayload]
    meta: ConnectorMeta


class ConnectorDescriptorResponse(BaseModel):
    data: ConnectorDescriptorPayload
    meta: ConnectorMeta


class ConnectionListResponse(BaseModel):
    data: list[ConnectorConnectionPayload]
    meta: ConnectorMeta


class ConnectionResponse(BaseModel):
    data: ConnectorConnectionPayload
    meta: ConnectorMeta


class OAuthStartResponse(BaseModel):
    data: OAuthStartPayload
    meta: ConnectorMeta


ExternalClientDependency = Annotated[
    ExternalClientPrincipal,
    Depends(verify_external_client),
]


def _session_factory_from_request(request: Request) -> Callable[[], Session] | None:
    return cast("Callable[[], Session] | None", request.app.state.session_factory)


@router.get(
    "/connectors",
    response_model=ConnectorListResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def list_connector_descriptors(
    request: Request,
    principal: ExternalClientDependency,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str | None, Query(min_length=1, max_length=40)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_connector(session, principal, action="list")
        page = list_connector_types(
            session,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status=status,
        )
        _audit(
            session,
            principal,
            action="list",
            result="succeeded",
            resource_id=None,
            metadata={"count": len(page.connectors), "status": status},
        )
        session.commit()
        return success_payload(
            [_descriptor_payload(connector) for connector in page.connectors],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@router.get(
    "/connectors/{connector_type}",
    response_model=ConnectorDescriptorResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_connector_descriptor(
    connector_type: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_connector(session, principal, action="read")
        connector = get_connector_type(session, connector_type)
        _audit(
            session,
            principal,
            action="read",
            result="succeeded",
            resource_id=connector.connector_type,
            metadata={"connector_type": connector.connector_type},
        )
        session.commit()
        return success_payload(
            _descriptor_payload(connector),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post(
    "/connectors/{connector_type}/oauth/start",
    response_model=OAuthStartResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def start_connector_oauth(
    connector_type: str,
    payload: OAuthStartRequest,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_connector(session, principal, action="start_oauth")
        owner_user_id = resolve_connector_owner_user_id(
            session,
            principal.external_client_id,
        )
        try:
            result = start_oauth_connection(
                session,
                owner_user_id=owner_user_id,
                connector_type=connector_type,
                requested_scopes=payload.requested_scopes,
                redirect_uri=payload.redirect_uri,
            )
        except ApiError as exc:
            _audit(
                session,
                principal,
                action="start_oauth",
                result="denied",
                resource_id=connector_type,
                reason_code=exc.code,
                metadata={"connector_type": connector_type},
            )
            session.commit()
            raise
        _audit(
            session,
            principal,
            action="start_oauth",
            result="succeeded",
            resource_id=result.oauth_state_id,
            metadata={
                "connector_type": connector_type,
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


@router.post(
    "/connectors/{connector_type}/oauth/callback",
    response_model=ConnectionResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def complete_connector_oauth(
    connector_type: str,
    payload: OAuthCallbackRequest,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_connector(session, principal, action="complete_oauth")
        owner_user_id = resolve_connector_owner_user_id(
            session,
            principal.external_client_id,
        )
        try:
            connection = complete_oauth_connection(
                session,
                owner_user_id=owner_user_id,
                connector_type=connector_type,
                state=payload.state,
                authorization_code=payload.authorization_code,
                account_identifier=payload.account_identifier,
                granted_scopes=payload.granted_scopes,
                display_name=payload.display_name,
            )
        except ApiError as exc:
            _audit(
                session,
                principal,
                action="complete_oauth",
                result="denied",
                resource_id=connector_type,
                reason_code=exc.code,
                metadata={"connector_type": connector_type},
            )
            session.commit()
            raise
        _audit(
            session,
            principal,
            action="complete_oauth",
            result="succeeded",
            resource_id=connection.connection_id,
            metadata={
                "connector_type": connection.connector_type,
                "connection_id": connection.connection_id,
                "scope_count": len(connection.granted_scopes),
            },
        )
        session.commit()
        return success_payload(
            _connection_payload(connection),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get(
    "/connections",
    response_model=ConnectionListResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def list_connector_connections(
    request: Request,
    principal: ExternalClientDependency,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    connector_type: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
    status: Annotated[str | None, Query(min_length=1, max_length=40)] = None,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_connector(session, principal, action="list_connections")
        owner_user_id = resolve_connector_owner_user_id(
            session,
            principal.external_client_id,
        )
        page = list_connections(
            session,
            owner_user_id=owner_user_id,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            connector_type=connector_type,
            status=status,
        )
        _audit(
            session,
            principal,
            action="list_connections",
            result="succeeded",
            resource_id=None,
            metadata={
                "connector_type": connector_type,
                "count": len(page.connections),
                "status": status,
            },
        )
        session.commit()
        return success_payload(
            [_connection_payload(connection) for connection in page.connections],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@router.get(
    "/connections/{connection_id}",
    response_model=ConnectionResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_connector_connection(
    connection_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_connector(session, principal, action="read_connection")
        owner_user_id = resolve_connector_owner_user_id(
            session,
            principal.external_client_id,
        )
        connection = get_connection(
            session,
            owner_user_id=owner_user_id,
            connection_id=connection_id,
        )
        _audit(
            session,
            principal,
            action="read_connection",
            result="succeeded",
            resource_id=connection.connection_id,
            metadata={"connector_type": connection.connector_type},
        )
        session.commit()
        return success_payload(
            _connection_payload(connection),
            meta={"correlation_id": get_correlation_id()},
        )


@router.get(
    "/connections/{connection_id}/health",
    response_model=ConnectionResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_connection_health(
    connection_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_connector(session, principal, action="read_health")
        owner_user_id = resolve_connector_owner_user_id(
            session,
            principal.external_client_id,
        )
        connection = check_connection_health(
            session,
            owner_user_id=owner_user_id,
            connection_id=connection_id,
        )
        _audit(
            session,
            principal,
            action="read_health",
            result="succeeded",
            resource_id=connection.connection_id,
            metadata={
                "connector_type": connection.connector_type,
                "connection_id": connection.connection_id,
                "health_status": connection.health_status,
            },
        )
        session.commit()
        return success_payload(
            _connection_payload(connection),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post(
    "/connections/{connection_id}/revoke",
    response_model=ConnectionResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def revoke_connector_connection(
    connection_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_connector(session, principal, action="revoke")
        owner_user_id = resolve_connector_owner_user_id(
            session,
            principal.external_client_id,
        )
        connection = revoke_connection(
            session,
            owner_user_id=owner_user_id,
            connection_id=connection_id,
        )
        _audit(
            session,
            principal,
            action="revoke",
            result="succeeded",
            resource_id=connection.connection_id,
            metadata={
                "connector_type": connection.connector_type,
                "connection_id": connection.connection_id,
                "outcome": "revoked",
            },
        )
        session.commit()
        return success_payload(
            _connection_payload(connection),
            meta={"correlation_id": get_correlation_id()},
        )


@router.post(
    "/connections/{connection_id}/reconnect",
    response_model=OAuthStartResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def reconnect_connector_connection(
    connection_id: str,
    payload: OAuthStartRequest,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        _authorize_connector(session, principal, action="reconnect")
        owner_user_id = resolve_connector_owner_user_id(
            session,
            principal.external_client_id,
        )
        connection = get_connection(
            session,
            owner_user_id=owner_user_id,
            connection_id=connection_id,
        )
        result = start_oauth_connection(
            session,
            owner_user_id=owner_user_id,
            connector_type=connection.connector_type,
            requested_scopes=payload.requested_scopes,
            redirect_uri=payload.redirect_uri,
        )
        _audit(
            session,
            principal,
            action="reconnect",
            result="succeeded",
            resource_id=connection.connection_id,
            metadata={
                "connector_type": connection.connector_type,
                "connection_id": connection.connection_id,
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


def _require_session_factory(request: Request) -> Callable[[], Session]:
    session_factory = _session_factory_from_request(request)
    if session_factory is None:
        raise ApiError(
            status_code=503,
            code="connector_store_not_configured",
            message="Connector storage is not configured.",
        )
    return session_factory


def _authorize_connector(
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
            resource="connector",
            action=action,
            risk_level=(
                "medium"
                if action
                in {"start_oauth", "complete_oauth", "revoke", "reconnect"}
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
        message="External client is not authorized for connector access.",
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
            event_type=f"connector.{action}",
            actor_type="external_client",
            actor_id=principal.external_client_id,
            channel="external_product_client",
            action=action,
            resource_type="connector",
            resource_id=resource_id,
            result=result,
            reason_code=reason_code,
            correlation_id=get_correlation_id(),
            metadata=metadata,
        ),
    )


def _descriptor_payload(connector: ConnectorType) -> dict[str, object]:
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
        "provider_docs_reference": connector.provider_docs_reference,
        "configuration_schema": connector.configuration_schema,
        "created_at": connector.created_at,
        "updated_at": connector.updated_at,
    }


def _connection_payload(connection: ConnectorConnection) -> dict[str, object]:
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
        "created_at": connection.created_at,
        "updated_at": connection.updated_at,
    }
