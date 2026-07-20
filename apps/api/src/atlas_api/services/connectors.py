from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.contracts import (
    PaginationParameters,
    decode_cursor,
    encode_cursor,
)
from atlas_api.core.errors import ApiError
from atlas_api.db.base import prefixed_id, utc_now
from atlas_api.models.connector import (
    ConnectorConnection,
    ConnectorCredentialReference,
    ConnectorOAuthState,
    ConnectorType,
)
from atlas_api.models.external_client import ExternalProductClient
from atlas_api.services.audit import AuditEventInput, record_audit_event

GMAIL_SCOPE_MODIFY = "https://www.googleapis.com/auth/gmail.modify"
DRIVE_SCOPE_FILE = "https://www.googleapis.com/auth/drive.file"
REJECTED_GMAIL_SCOPE_FULL_MAILBOX = "https://mail.google.com/"
OAUTH_STATE_TTL_MINUTES = 15
GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_GMAIL_PROFILE_ENDPOINT = (
    "https://gmail.googleapis.com/gmail/v1/users/me/profile"
)
GOOGLE_DRIVE_ABOUT_ENDPOINT = (
    "https://www.googleapis.com/drive/v3/about?fields=user(emailAddress,displayName)"
)


@dataclass(frozen=True)
class ConnectorPage:
    connectors: list[ConnectorType]
    next_cursor: str | None


@dataclass(frozen=True)
class ConnectionPage:
    connections: list[ConnectorConnection]
    next_cursor: str | None


@dataclass(frozen=True)
class OAuthStartResult:
    oauth_state_id: str
    connector_type: str
    authorization_url: str
    requested_scopes: list[str]
    expires_at: datetime


@dataclass(frozen=True)
class GoogleOAuthExchangeResult:
    account_identifier: str
    granted_scopes: list[str]
    display_name: str | None = None
    credential_key_version: str = "google-oauth-v1"


class GoogleOAuthExchange(Protocol):
    def __call__(
        self,
        *,
        settings: Settings,
        oauth_state: ConnectorOAuthState,
        authorization_code: str,
    ) -> GoogleOAuthExchangeResult: ...


@dataclass(frozen=True)
class ConnectorOperationAuthorization:
    allowed: bool
    reason_code: str


@dataclass(frozen=True)
class DefaultConnectorDescriptor:
    display_name: str
    version: str
    authentication_type: str
    supported_operations: list[str]
    required_scopes: dict[str, list[str]]
    risk_by_operation: dict[str, str]
    provider_docs_reference: str
    configuration_schema: dict[str, object]


DEFAULT_CONNECTOR_DESCRIPTORS = {
    "gmail": DefaultConnectorDescriptor(
        display_name="Gmail",
        version="0.1.0",
        authentication_type="oauth2",
        supported_operations=[
            "gmail.list_messages",
            "gmail.get_message",
            "gmail.apply_label",
            "gmail.archive_message",
            "gmail.create_draft",
            "gmail.get_attachment",
            "gmail.send_message_later",
        ],
        required_scopes={
            "gmail.list_messages": [GMAIL_SCOPE_MODIFY],
            "gmail.get_message": [GMAIL_SCOPE_MODIFY],
            "gmail.apply_label": [GMAIL_SCOPE_MODIFY],
            "gmail.archive_message": [GMAIL_SCOPE_MODIFY],
            "gmail.create_draft": [GMAIL_SCOPE_MODIFY],
            "gmail.get_attachment": [GMAIL_SCOPE_MODIFY],
            "gmail.send_message_later": [GMAIL_SCOPE_MODIFY],
        },
        risk_by_operation={
            "gmail.list_messages": "medium",
            "gmail.get_message": "medium",
            "gmail.apply_label": "low",
            "gmail.archive_message": "low",
            "gmail.create_draft": "medium",
            "gmail.get_attachment": "medium",
            "gmail.send_message_later": "high",
        },
        provider_docs_reference=(
            "https://developers.google.com/workspace/gmail/api/auth/scopes"
        ),
        configuration_schema={
            "type": "object",
            "properties": {
                "eligible_query": {"type": "string", "maxLength": 240},
                "max_messages_per_run": {"type": "integer", "minimum": 1},
            },
        },
    ),
    "google_drive": DefaultConnectorDescriptor(
        display_name="Google Drive",
        version="0.1.0",
        authentication_type="oauth2",
        supported_operations=[
            "drive.create_folder",
            "drive.save_attachment",
        ],
        required_scopes={
            "drive.create_folder": [DRIVE_SCOPE_FILE],
            "drive.save_attachment": [DRIVE_SCOPE_FILE],
        },
        risk_by_operation={
            "drive.create_folder": "low",
            "drive.save_attachment": "low",
        },
        provider_docs_reference=(
            "https://developers.google.com/workspace/drive/api/guides/api-specific-auth"
        ),
        configuration_schema={
            "type": "object",
            "properties": {
                "root_folder_reference": {"type": "string", "maxLength": 160}
            },
        },
    ),
}

ACCEPTED_SCOPES_BY_CONNECTOR = {
    "gmail": [GMAIL_SCOPE_MODIFY],
    "google_drive": [DRIVE_SCOPE_FILE],
}


def ensure_default_connector_types(session: Session) -> None:
    for connector_type, descriptor in DEFAULT_CONNECTOR_DESCRIPTORS.items():
        existing = session.get(ConnectorType, connector_type)
        if existing is None:
            session.add(
                ConnectorType(
                    connector_type=connector_type,
                    display_name=descriptor.display_name,
                    version=descriptor.version,
                    authentication_type=descriptor.authentication_type,
                    status="active",
                    supported_operations=list(descriptor.supported_operations),
                    required_scopes=dict(descriptor.required_scopes),
                    risk_by_operation=dict(descriptor.risk_by_operation),
                    supports_health_check=True,
                    supports_revocation=True,
                    supports_refresh=True,
                    provider_docs_reference=descriptor.provider_docs_reference,
                    configuration_schema=dict(descriptor.configuration_schema),
                )
            )
        else:
            existing.display_name = descriptor.display_name
            existing.version = descriptor.version
            existing.authentication_type = descriptor.authentication_type
            existing.status = "active"
            existing.supported_operations = list(descriptor.supported_operations)
            existing.required_scopes = dict(descriptor.required_scopes)
            existing.risk_by_operation = dict(descriptor.risk_by_operation)
            existing.provider_docs_reference = descriptor.provider_docs_reference
            existing.configuration_schema = dict(descriptor.configuration_schema)
    session.flush()


def list_connector_types(
    session: Session,
    *,
    pagination: PaginationParameters,
    status: str | None = None,
) -> ConnectorPage:
    ensure_default_connector_types(session)
    if status is not None and status not in {"active", "disabled"}:
        raise ApiError(422, "connector_status_invalid", "Connector status is invalid.")
    query = select(ConnectorType)
    if status is not None:
        query = query.where(ConnectorType.status == status)
    query = _apply_connector_cursor(query, pagination.cursor)
    query = query.order_by(ConnectorType.created_at, ConnectorType.connector_type)
    rows = list(session.scalars(query.limit(pagination.limit + 1)))
    next_cursor = None
    if len(rows) > pagination.limit:
        rows = rows[: pagination.limit]
        last = rows[-1]
        next_cursor = encode_cursor(
            {
                "created_at": last.created_at.isoformat(),
                "connector_type": last.connector_type,
            }
        )
    return ConnectorPage(connectors=rows, next_cursor=next_cursor)


def get_connector_type(session: Session, connector_type: str) -> ConnectorType:
    ensure_default_connector_types(session)
    connector = session.get(ConnectorType, connector_type)
    if connector is None:
        raise ApiError(404, "connector_not_found", "Connector was not found.")
    return connector


def start_oauth_connection(
    session: Session,
    *,
    owner_user_id: str,
    connector_type: str,
    requested_scopes: list[str],
    redirect_uri: str,
    settings: Settings | None = None,
) -> OAuthStartResult:
    connector = get_connector_type(session, connector_type)
    _validate_redirect_uri(redirect_uri)
    accepted_scopes = _accepted_scopes(connector.connector_type)
    _validate_exact_scopes(
        connector_type=connector.connector_type,
        requested_scopes=requested_scopes,
        accepted_scopes=accepted_scopes,
    )
    raw_state = secrets.token_urlsafe(32)
    pkce_verifier = secrets.token_urlsafe(64)
    state = ConnectorOAuthState(
        owner_user_id=owner_user_id,
        connector_type=connector.connector_type,
        state_hash=_hash(raw_state),
        pkce_challenge=pkce_verifier,
        redirect_uri=redirect_uri,
        requested_scopes=accepted_scopes,
        status="pending",
        expires_at=ConnectorOAuthState.pending_until(OAUTH_STATE_TTL_MINUTES),
    )
    session.add(state)
    session.flush()
    if _google_oauth_configured(settings):
        assert settings is not None
        authorization_url = _google_authorization_url(
            settings=settings,
            redirect_uri=redirect_uri,
            state=raw_state,
            scopes=accepted_scopes,
            pkce_verifier=pkce_verifier,
        )
    else:
        authorization_url = _fake_authorization_url(
            connector_type=connector.connector_type,
            redirect_uri=redirect_uri,
            state=raw_state,
            scopes=accepted_scopes,
            pkce_challenge=pkce_verifier,
        )
    return OAuthStartResult(
        oauth_state_id=state.oauth_state_id,
        connector_type=connector.connector_type,
        authorization_url=authorization_url,
        requested_scopes=accepted_scopes,
        expires_at=state.expires_at,
    )


def complete_oauth_connection(
    session: Session,
    *,
    owner_user_id: str,
    connector_type: str,
    state: str,
    authorization_code: str,
    account_identifier: str,
    granted_scopes: list[str],
    display_name: str | None = None,
) -> ConnectorConnection:
    connector = get_connector_type(session, connector_type)
    if not authorization_code.strip() or len(authorization_code) > 512:
        raise ApiError(
            422,
            "oauth_authorization_code_invalid",
            "OAuth code is invalid.",
        )
    _validate_account_identifier(account_identifier)
    accepted_scopes = _accepted_scopes(connector.connector_type)
    _validate_exact_scopes(
        connector_type=connector.connector_type,
        requested_scopes=granted_scopes,
        accepted_scopes=accepted_scopes,
    )
    oauth_state = session.scalar(
        select(ConnectorOAuthState).where(
            ConnectorOAuthState.owner_user_id == owner_user_id,
            ConnectorOAuthState.connector_type == connector.connector_type,
            ConnectorOAuthState.state_hash == _hash(state),
        )
    )
    if oauth_state is None:
        raise ApiError(422, "oauth_state_invalid", "OAuth state is invalid.")
    return _complete_oauth_connection_for_state(
        session,
        owner_user_id=owner_user_id,
        connector=connector,
        oauth_state=oauth_state,
        account_identifier=account_identifier,
        granted_scopes=granted_scopes,
        display_name=display_name,
        credential_key_version="local-fake-v1",
    )


def complete_google_oauth_connection(
    session: Session,
    *,
    owner_user_id: str,
    state: str,
    authorization_code: str,
    settings: Settings,
    exchange: GoogleOAuthExchange | None = None,
) -> ConnectorConnection:
    if not authorization_code.strip() or len(authorization_code) > 512:
        raise ApiError(
            422,
            "oauth_authorization_code_invalid",
            "OAuth code is invalid.",
        )
    if not _google_oauth_configured(settings):
        raise ApiError(
            503,
            "google_oauth_not_configured",
            "Google OAuth is not configured.",
        )
    oauth_state = session.scalar(
        select(ConnectorOAuthState).where(
            ConnectorOAuthState.owner_user_id == owner_user_id,
            ConnectorOAuthState.state_hash == _hash(state),
        )
    )
    if oauth_state is None:
        raise ApiError(422, "oauth_state_invalid", "OAuth state is invalid.")
    if oauth_state.redirect_uri != settings.google_oauth_redirect_uri:
        raise ApiError(422, "oauth_redirect_uri_invalid", "Redirect URI is invalid.")
    _validate_pending_oauth_state(oauth_state)
    connector = get_connector_type(session, oauth_state.connector_type)
    provider_result = (exchange or exchange_google_oauth_code)(
        settings=settings,
        oauth_state=oauth_state,
        authorization_code=authorization_code,
    )
    _validate_account_identifier(provider_result.account_identifier)
    return _complete_oauth_connection_for_state(
        session,
        owner_user_id=owner_user_id,
        connector=connector,
        oauth_state=oauth_state,
        account_identifier=provider_result.account_identifier,
        granted_scopes=provider_result.granted_scopes,
        display_name=provider_result.display_name,
        credential_key_version=provider_result.credential_key_version,
    )


def _complete_oauth_connection_for_state(
    session: Session,
    *,
    owner_user_id: str,
    connector: ConnectorType,
    oauth_state: ConnectorOAuthState,
    account_identifier: str,
    granted_scopes: list[str],
    display_name: str | None,
    credential_key_version: str,
) -> ConnectorConnection:
    _validate_pending_oauth_state(oauth_state)
    accepted_scopes = _accepted_scopes(connector.connector_type)
    _validate_exact_scopes(
        connector_type=connector.connector_type,
        requested_scopes=granted_scopes,
        accepted_scopes=accepted_scopes,
    )
    if sorted(oauth_state.requested_scopes) != sorted(granted_scopes):
        raise ApiError(
            422,
            "connector_scope_mismatch",
            "Granted scopes do not match the approved request.",
        )
    credential_reference = ConnectorCredentialReference(
        owner_user_id=owner_user_id,
        connector_type=connector.connector_type,
        reference_label=f"{connector.connector_type}:oauth:{prefixed_id('ref')}",
        key_version=credential_key_version,
        status="active",
        last_rotated_at=utc_now(),
    )
    session.add(credential_reference)
    session.flush()
    connection = session.scalar(
        select(ConnectorConnection).where(
            ConnectorConnection.owner_user_id == owner_user_id,
            ConnectorConnection.connector_type == connector.connector_type,
            ConnectorConnection.account_identifier == account_identifier,
        )
    )
    if connection is None:
        connection = ConnectorConnection(
            owner_user_id=owner_user_id,
            connector_type=connector.connector_type,
            display_name=display_name or connector.display_name,
            account_identifier=account_identifier,
            status="connected",
            granted_scopes=accepted_scopes,
            credential_reference_id=credential_reference.credential_reference_id,
            health_status="healthy",
            last_success_at=utc_now(),
            last_health_checked_at=utc_now(),
        )
        session.add(connection)
    else:
        connection.display_name = display_name or connection.display_name
        connection.status = "connected"
        connection.granted_scopes = accepted_scopes
        connection.credential_reference_id = (
            credential_reference.credential_reference_id
        )
        connection.health_status = "healthy"
        connection.last_success_at = utc_now()
        connection.last_failure_at = None
        connection.last_error_code = None
        connection.last_health_checked_at = utc_now()
    oauth_state.status = "consumed"
    oauth_state.consumed_at = utc_now()
    session.flush()
    return connection


def _validate_pending_oauth_state(oauth_state: ConnectorOAuthState) -> None:
    if oauth_state.status != "pending" or _is_expired(oauth_state.expires_at):
        raise ApiError(422, "oauth_state_expired", "OAuth state is expired.")


def list_connections(
    session: Session,
    *,
    owner_user_id: str,
    pagination: PaginationParameters,
    connector_type: str | None = None,
    status: str | None = None,
) -> ConnectionPage:
    if connector_type is not None:
        get_connector_type(session, connector_type)
    if status is not None and status not in {
        "connected",
        "degraded",
        "expired",
        "revoked",
        "error",
        "disconnected",
    }:
        raise ApiError(
            422,
            "connection_status_invalid",
            "Connection status is invalid.",
        )
    query = select(ConnectorConnection).where(
        ConnectorConnection.owner_user_id == owner_user_id
    )
    if connector_type is not None:
        query = query.where(ConnectorConnection.connector_type == connector_type)
    if status is not None:
        query = query.where(ConnectorConnection.status == status)
    query = _apply_connection_cursor(query, pagination.cursor)
    query = query.order_by(
        ConnectorConnection.created_at,
        ConnectorConnection.connection_id,
    )
    rows = list(session.scalars(query.limit(pagination.limit + 1)))
    next_cursor = None
    if len(rows) > pagination.limit:
        rows = rows[: pagination.limit]
        last = rows[-1]
        next_cursor = encode_cursor(
            {
                "created_at": last.created_at.isoformat(),
                "connection_id": last.connection_id,
            }
        )
    return ConnectionPage(connections=rows, next_cursor=next_cursor)


def get_connection(
    session: Session,
    *,
    owner_user_id: str,
    connection_id: str,
) -> ConnectorConnection:
    connection = session.get(ConnectorConnection, connection_id)
    if connection is None or connection.owner_user_id != owner_user_id:
        raise ApiError(404, "connection_not_found", "Connection was not found.")
    return connection


def check_connection_health(
    session: Session,
    *,
    owner_user_id: str,
    connection_id: str,
) -> ConnectorConnection:
    connection = get_connection(
        session,
        owner_user_id=owner_user_id,
        connection_id=connection_id,
    )
    credential = session.get(
        ConnectorCredentialReference,
        connection.credential_reference_id,
    )
    accepted_scopes = _accepted_scopes(connection.connector_type)
    if (
        connection.status == "revoked"
        or credential is None
        or credential.status == "revoked"
    ):
        connection.health_status = "revoked"
        connection.last_error_code = "credential_revoked"
    elif sorted(connection.granted_scopes) != sorted(accepted_scopes):
        connection.health_status = "degraded"
        connection.status = "degraded"
        connection.last_error_code = "connector_scope_mismatch"
        connection.last_failure_at = utc_now()
    elif connection.status == "connected":
        connection.health_status = "healthy"
        connection.last_error_code = None
        connection.last_success_at = utc_now()
    else:
        connection.health_status = "unknown"
    connection.last_health_checked_at = utc_now()
    session.flush()
    return connection


def revoke_connection(
    session: Session,
    *,
    owner_user_id: str,
    connection_id: str,
) -> ConnectorConnection:
    connection = get_connection(
        session,
        owner_user_id=owner_user_id,
        connection_id=connection_id,
    )
    credential = session.get(
        ConnectorCredentialReference,
        connection.credential_reference_id,
    )
    connection.status = "revoked"
    connection.health_status = "revoked"
    connection.last_error_code = "credential_revoked"
    connection.last_health_checked_at = utc_now()
    if credential is not None:
        credential.status = "revoked"
    session.flush()
    return connection


def authorize_connector_operation(
    session: Session,
    *,
    owner_user_id: str,
    connection_id: str,
    operation_id: str,
    actor_id: str,
    correlation_id: str | None = None,
) -> ConnectorOperationAuthorization:
    connection = get_connection(
        session,
        owner_user_id=owner_user_id,
        connection_id=connection_id,
    )
    connector = get_connector_type(session, connection.connector_type)
    result = _operation_authorization(connection, connector, operation_id)
    record_audit_event(
        session,
        AuditEventInput(
            event_type="connector.operation_authorization",
            actor_type="external_client",
            actor_id=actor_id,
            channel="external_product_client",
            action="authorize_operation",
            resource_type="connector_connection",
            resource_id=connection.connection_id,
            result="succeeded" if result.allowed else "denied",
            reason_code=None if result.allowed else result.reason_code,
            correlation_id=correlation_id,
            metadata={
                "connector_type": connection.connector_type,
                "connection_id": connection.connection_id,
                "operation_id": operation_id,
                "outcome": "authorized" if result.allowed else result.reason_code,
            },
        )
    )
    return result


def resolve_connector_owner_user_id(session: Session, external_client_id: str) -> str:
    client = session.get(ExternalProductClient, external_client_id)
    if (
        client is None
        or client.status != "active"
        or client.human_owner_user_id is None
    ):
        raise ApiError(
            status_code=403,
            code="connector_owner_unavailable",
            message="External client is not linked to an active human owner.",
        )
    return client.human_owner_user_id


def _operation_authorization(
    connection: ConnectorConnection,
    connector: ConnectorType,
    operation_id: str,
) -> ConnectorOperationAuthorization:
    if connection.status != "connected":
        return ConnectorOperationAuthorization(False, "connector_not_connected")
    if operation_id not in connector.supported_operations:
        return ConnectorOperationAuthorization(False, "connector_operation_unsupported")
    required_scopes = connector.required_scopes.get(operation_id, [])
    if not set(required_scopes).issubset(set(connection.granted_scopes)):
        return ConnectorOperationAuthorization(False, "connector_scope_missing")
    return ConnectorOperationAuthorization(True, "explicit_allow")


def _accepted_scopes(connector_type: str) -> list[str]:
    try:
        return list(ACCEPTED_SCOPES_BY_CONNECTOR[connector_type])
    except KeyError as exc:
        raise ApiError(
            404,
            "connector_not_found",
            "Connector was not found.",
        ) from exc


def _validate_exact_scopes(
    *,
    connector_type: str,
    requested_scopes: list[str],
    accepted_scopes: list[str],
) -> None:
    if REJECTED_GMAIL_SCOPE_FULL_MAILBOX in requested_scopes:
        raise ApiError(
            422,
            "connector_scope_rejected",
            "Requested scope exceeds the accepted MVP boundary.",
            details={"connector_type": connector_type},
        )
    if sorted(set(requested_scopes)) != sorted(accepted_scopes):
        raise ApiError(
            422,
            "connector_scope_mismatch",
            "Requested scopes must exactly match the accepted connector scope set.",
            details={"connector_type": connector_type},
        )


def _validate_redirect_uri(redirect_uri: str) -> None:
    if not redirect_uri.startswith(("http://localhost", "https://")):
        raise ApiError(422, "oauth_redirect_uri_invalid", "Redirect URI is invalid.")
    if len(redirect_uri) > 500:
        raise ApiError(422, "oauth_redirect_uri_invalid", "Redirect URI is invalid.")


def _validate_account_identifier(account_identifier: str) -> None:
    if (
        len(account_identifier) > 320
        or "@" not in account_identifier
        or any(char.isspace() for char in account_identifier)
    ):
        raise ApiError(
            422,
            "connector_account_identifier_invalid",
            "Connector account identifier is invalid.",
        )


def _fake_authorization_url(
    *,
    connector_type: str,
    redirect_uri: str,
    state: str,
    scopes: list[str],
    pkce_challenge: str,
) -> str:
    query = urlencode(
        {
            "response_type": "code",
            "client_id": f"atlas-{connector_type}-local",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "code_challenge": pkce_challenge,
            "code_challenge_method": "S256",
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"


def _google_oauth_configured(settings: Settings | None) -> bool:
    return bool(
        settings
        and settings.google_oauth_client_id
        and settings.google_oauth_client_secret
        and settings.google_oauth_redirect_uri
    )


def _google_authorization_url(
    *,
    settings: Settings,
    redirect_uri: str,
    state: str,
    scopes: list[str],
    pkce_verifier: str,
) -> str:
    if redirect_uri != settings.google_oauth_redirect_uri:
        raise ApiError(422, "oauth_redirect_uri_invalid", "Redirect URI is invalid.")
    query = urlencode(
        {
            "response_type": "code",
            "client_id": settings.google_oauth_client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "code_challenge": _pkce_code_challenge(pkce_verifier),
            "code_challenge_method": "S256",
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return f"{GOOGLE_AUTHORIZATION_ENDPOINT}?{query}"


def exchange_google_oauth_code(
    *,
    settings: Settings,
    oauth_state: ConnectorOAuthState,
    authorization_code: str,
) -> GoogleOAuthExchangeResult:
    client_secret = settings.google_oauth_client_secret
    if (
        settings.google_oauth_client_id is None
        or client_secret is None
        or settings.google_oauth_redirect_uri is None
    ):
        raise ApiError(
            503,
            "google_oauth_not_configured",
            "Google OAuth is not configured.",
        )
    token_response = _post_google_form(
        GOOGLE_TOKEN_ENDPOINT,
        {
            "code": authorization_code,
            "client_id": settings.google_oauth_client_id,
            "client_secret": client_secret.get_secret_value(),
            "redirect_uri": settings.google_oauth_redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": oauth_state.pkce_challenge,
        },
    )
    access_token = _required_json_string(
        token_response,
        "access_token",
        error_code="google_oauth_exchange_failed",
    )
    granted_scope_text = _required_json_string(
        token_response,
        "scope",
        error_code="google_oauth_scope_unavailable",
    )
    granted_scopes = [scope for scope in granted_scope_text.split(" ") if scope]
    profile = _google_account_profile(
        connector_type=oauth_state.connector_type,
        access_token=access_token,
    )
    return GoogleOAuthExchangeResult(
        account_identifier=profile["account_identifier"],
        granted_scopes=granted_scopes,
        display_name=profile.get("display_name"),
    )


def _google_account_profile(
    *,
    connector_type: str,
    access_token: str,
) -> dict[str, str]:
    if connector_type == "gmail":
        payload = _get_google_json(GOOGLE_GMAIL_PROFILE_ENDPOINT, access_token)
        email = _required_json_string(
            payload,
            "emailAddress",
            error_code="google_oauth_account_unavailable",
        )
        return {"account_identifier": email, "display_name": "Gmail"}
    if connector_type == "google_drive":
        payload = _get_google_json(GOOGLE_DRIVE_ABOUT_ENDPOINT, access_token)
        user = payload.get("user")
        if not isinstance(user, dict):
            raise ApiError(
                502,
                "google_oauth_account_unavailable",
                "Google account identity is unavailable.",
            )
        email = _required_json_string(
            user,
            "emailAddress",
            error_code="google_oauth_account_unavailable",
        )
        display_name = user.get("displayName")
        return {
            "account_identifier": email,
            "display_name": display_name if isinstance(display_name, str) else "Drive",
        }
    raise ApiError(404, "connector_not_found", "Connector was not found.")


def _post_google_form(url: str, values: dict[str, str]) -> dict[str, Any]:
    body = urlencode(values).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    return _read_google_json(request)


def _get_google_json(url: str, access_token: str) -> dict[str, Any]:
    request = Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    return _read_google_json(request)


def _read_google_json(request: Request) -> dict[str, Any]:
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise ApiError(
            502,
            "google_oauth_exchange_failed",
            "Google OAuth exchange failed.",
        ) from exc
    if not isinstance(payload, dict):
        raise ApiError(
            502,
            "google_oauth_exchange_failed",
            "Google OAuth exchange failed.",
        )
    return payload


def _required_json_string(
    payload: dict[str, Any],
    key: str,
    *,
    error_code: str,
) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ApiError(502, error_code, "Google OAuth response is incomplete.")
    return value


def _pkce_code_challenge(verifier: str) -> str:
    import base64

    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _is_expired(expires_at: datetime) -> bool:
    normalized = (
        expires_at.replace(tzinfo=UTC)
        if expires_at.tzinfo is None
        else expires_at.astimezone(UTC)
    )
    return normalized <= utc_now()


def _apply_connector_cursor(
    query: Select[tuple[ConnectorType]],
    cursor: str | None,
) -> Select[tuple[ConnectorType]]:
    if cursor is None:
        return query
    values = decode_cursor(cursor)
    try:
        created_at = datetime.fromisoformat(values["created_at"])
        connector_type = values["connector_type"]
    except (KeyError, ValueError) as exc:
        raise ApiError(
            status_code=422,
            code="pagination_cursor_invalid",
            message="Pagination cursor is invalid.",
        ) from exc
    return query.where(
        or_(
            ConnectorType.created_at > created_at,
            and_(
                ConnectorType.created_at == created_at,
                ConnectorType.connector_type > connector_type,
            ),
        )
    )


def _apply_connection_cursor(
    query: Select[tuple[ConnectorConnection]],
    cursor: str | None,
) -> Select[tuple[ConnectorConnection]]:
    if cursor is None:
        return query
    values = decode_cursor(cursor)
    try:
        created_at = datetime.fromisoformat(values["created_at"])
        connection_id = values["connection_id"]
    except (KeyError, ValueError) as exc:
        raise ApiError(
            status_code=422,
            code="pagination_cursor_invalid",
            message="Pagination cursor is invalid.",
        ) from exc
    return query.where(
        or_(
            ConnectorConnection.created_at > created_at,
            and_(
                ConnectorConnection.created_at == created_at,
                ConnectorConnection.connection_id > connection_id,
            ),
        )
    )
