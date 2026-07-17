from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from atlas_api.core.authorization import (
    ActorKind,
    AuthorizationContext,
    Channel,
    authorize,
)
from atlas_api.core.config import Settings
from atlas_api.core.correlation import get_correlation_id
from atlas_api.core.errors import ApiError
from atlas_api.core.external_request_signing import (
    ExternalRequestSignatureError,
    SignedExternalRequest,
    verify_signature,
)
from atlas_api.models.audit import AuditEvent
from atlas_api.models.external_request_nonce import ExternalRequestNonce

NONCE_RETENTION = timedelta(minutes=10)


@dataclass(frozen=True)
class ExternalClientPrincipal:
    external_client_id: str
    channel: str = "external_product_client"


def get_settings_from_request(request: Request) -> Settings:
    return request.app.state.settings


def _session_factory_from_request(request: Request) -> Callable[[], Session] | None:
    return request.app.state.session_factory


def _audit_authorization(
    session: Session,
    *,
    external_client_id: str | None,
    key_id: str | None,
    outcome: str,
) -> None:
    session.add(
        AuditEvent(
            event_type="external_client_authorization",
            actor_type="external_client",
            actor_id=external_client_id,
            resource_type="external_client_authentication",
            resource_id=external_client_id,
            correlation_id=get_correlation_id(),
            redaction_state="metadata_only",
            metadata_json={
                "channel": "external_product_client",
                "outcome": outcome,
                "key_id": key_id,
            },
        )
    )


def _consume_nonce(
    session: Session,
    request: SignedExternalRequest,
    *,
    now: datetime,
) -> bool:
    session.execute(
        delete(ExternalRequestNonce).where(ExternalRequestNonce.expires_at <= now)
    )
    try:
        with session.begin_nested():
            session.add(
                ExternalRequestNonce(
                    external_client_id=request.client_id,
                    key_id=request.key_id,
                    nonce=request.nonce,
                    expires_at=now + NONCE_RETENTION,
                )
            )
            session.flush()
    except IntegrityError:
        return False
    return True


def _external_client_configured(settings: Settings) -> bool:
    return bool(
        settings.external_client_id
        and settings.external_client_key_id
        and settings.external_client_secret
    )


def _api_error(code: str, message: str, *, status_code: int = 401) -> ApiError:
    return ApiError(status_code=status_code, code=code, message=message)


async def verify_external_client(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings_from_request)],
    external_client_id: Annotated[str | None, Header(alias="X-Atlas-Client-Id")] = None,
    key_id: Annotated[str | None, Header(alias="X-Atlas-Key-Id")] = None,
    timestamp: Annotated[str | None, Header(alias="X-Atlas-Timestamp")] = None,
    nonce: Annotated[str | None, Header(alias="X-Atlas-Nonce")] = None,
    signature: Annotated[str | None, Header(alias="X-Atlas-Signature")] = None,
) -> ExternalClientPrincipal:
    if not _external_client_configured(settings):
        raise _api_error(
            "external_client_authentication_not_configured",
            "External client authentication is not configured.",
            status_code=503,
        )

    if not all([external_client_id, key_id, timestamp, nonce, signature]):
        raise _api_error(
            "external_client_signature_headers_required",
            "Signed external client request headers are required.",
        )
    assert external_client_id is not None
    assert key_id is not None
    assert timestamp is not None
    assert nonce is not None
    assert signature is not None
    if external_client_id != settings.external_client_id:
        raise _api_error(
            "external_client_identity_invalid", "External client identity is invalid."
        )
    if len(nonce) > 160 or not nonce.isascii() or not nonce.strip():
        raise _api_error(
            "external_client_nonce_invalid", "External client nonce is invalid."
        )
    if re.fullmatch(r"[0-9a-f]{64}", signature) is None:
        raise _api_error(
            "external_client_signature_invalid",
            "External client request signature is invalid.",
        )
    try:
        timestamp_value = int(timestamp)
    except ValueError as exc:
        raise _api_error(
            "external_client_timestamp_invalid", "External client timestamp is invalid."
        ) from exc

    signed_request = SignedExternalRequest(
        client_id=external_client_id,
        key_id=key_id,
        timestamp=timestamp_value,
        nonce=nonce,
        signature=signature,
        method=request.method,
        path_query=request.url.path
        + (f"?{request.url.query}" if request.url.query else ""),
        body=await request.body(),
    )
    session_factory = _session_factory_from_request(request)
    if session_factory is None:
        raise _api_error(
            "external_client_nonce_store_not_configured",
            "External client authentication storage is not configured.",
            status_code=503,
        )

    now = datetime.now(UTC)
    with session_factory() as session:
        try:
            verify_signature(signed_request, settings, now=now)
        except (
            ExternalRequestSignatureError,
            OverflowError,
            OSError,
            ValueError,
        ) as exc:
            code = (
                exc.code
                if isinstance(exc, ExternalRequestSignatureError)
                else "external_client_timestamp_invalid"
            )
            _audit_authorization(
                session,
                external_client_id=external_client_id,
                key_id=key_id,
                outcome=code,
            )
            session.commit()
            raise _api_error(
                code, "External client request signature is invalid."
            ) from exc

        decision = authorize(
            AuthorizationContext(
                actor_kind=ActorKind.EXTERNAL_CLIENT,
                actor_id=external_client_id,
                channel=Channel.EXTERNAL_PRODUCT_CLIENT,
                resource="external_client_authentication",
                action="probe",
            )
        )
        if not decision.allowed:
            _audit_authorization(
                session,
                external_client_id=external_client_id,
                key_id=key_id,
                outcome=decision.reason_code,
            )
            session.commit()
            raise _api_error(
                "authorization_denied",
                "External client is not authorized.",
                status_code=403,
            )
        if not _consume_nonce(session, signed_request, now=now):
            _audit_authorization(
                session,
                external_client_id=external_client_id,
                key_id=key_id,
                outcome="external_client_nonce_replayed",
            )
            session.commit()
            raise _api_error(
                "external_client_nonce_replayed",
                "External client nonce has already been used.",
            )
        _audit_authorization(
            session,
            external_client_id=external_client_id,
            key_id=key_id,
            outcome="authorized",
        )
        session.commit()

    return ExternalClientPrincipal(external_client_id=external_client_id)
