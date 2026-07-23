from __future__ import annotations

import html
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated, cast
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.core.owner_sessions import (
    OwnerSessionError,
    ensure_owner_user,
    issue_owner_session,
    set_owner_session_cookies,
)
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.owner_identity import (
    OWNER_OIDC_COOKIE_NAME,
    complete_owner_oidc_authorization,
    owner_id_token_verifier_from_app_state,
    owner_token_exchange_from_app_state,
    start_owner_oidc_authorization,
)

router = APIRouter(prefix="/auth/owner/google", tags=["owner-identity"])


def _settings_from_request(request: Request) -> Settings:
    return cast("Settings", request.app.state.settings)


def _session_factory_from_request(request: Request) -> Callable[[], Session] | None:
    return cast("Callable[[], Session] | None", request.app.state.session_factory)


SettingsDependency = Annotated[Settings, Depends(_settings_from_request)]


@router.get("/start")
def start_owner_google_oidc(settings: SettingsDependency) -> RedirectResponse:
    authorization = start_owner_oidc_authorization(
        settings,
        now=datetime.now(UTC),
    )
    response = RedirectResponse(authorization.authorization_url, status_code=307)
    response.set_cookie(
        OWNER_OIDC_COOKIE_NAME,
        authorization.cookie_value,
        max_age=authorization.max_age_seconds,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/callback")
def complete_owner_google_oidc(
    request: Request,
    settings: SettingsDependency,
    code: Annotated[str | None, Query(max_length=1024)] = None,
    state: Annotated[str | None, Query(max_length=160)] = None,
    provider_error: Annotated[str | None, Query(alias="error", max_length=160)] = None,
    transaction_cookie: Annotated[
        str | None,
        Cookie(alias=OWNER_OIDC_COOKIE_NAME),
    ] = None,
) -> Response:
    if provider_error is not None:
        return _completion_response(
            status_code=400,
            title="Owner identity not verified",
            body="The owner identity verification was not completed.",
        )

    exchange = owner_token_exchange_from_app_state(
        getattr(request.app.state, "owner_oidc_token_exchange", None)
    )
    verifier = owner_id_token_verifier_from_app_state(
        getattr(request.app.state, "owner_oidc_id_token_verifier", None)
    )
    claims = complete_owner_oidc_authorization(
        settings,
        state=state,
        authorization_code=code,
        cookie_value=transaction_cookie,
        now=datetime.now(UTC),
        exchange=exchange,
        verifier=verifier,
    )
    if settings.owner_identity_subject is not None:
        return _issue_owner_session_response(request, settings, claims)
    return _completion_response(
        status_code=200,
        title="Owner identity verified",
        body=(
            "Enter this opaque Google subject in Render as "
            "ATLAS_API_OWNER_IDENTITY_SUBJECT: "
            f"<code>{html.escape(claims.subject)}</code>"
        ),
    )


def _issue_owner_session_response(
    request: Request,
    settings: Settings,
    claims: object,
) -> RedirectResponse:
    from atlas_api.services.owner_identity import OwnerIdentityClaims

    owner_claims = cast(OwnerIdentityClaims, claims)
    session_factory = _session_factory_from_request(request)
    if session_factory is None:
        raise ApiError(
            503,
            "owner_session_store_not_configured",
            "Owner session storage is not configured.",
        )
    try:
        with session_factory() as session:
            user = ensure_owner_user(
                session,
                provider="google",
                subject=owner_claims.subject,
                email=owner_claims.email,
                display_name=owner_claims.email,
                settings=settings,
            )
            issued = issue_owner_session(
                session,
                user_id=user.user_id,
                settings=settings,
                now=datetime.now(UTC),
            )
            record_audit_event(
                session,
                AuditEventInput(
                    event_type="owner_session.login",
                    actor_type="human_owner",
                    actor_id=user.user_id,
                    channel="dashboard",
                    action="login",
                    resource_type="owner_session",
                    resource_id=issued.owner_session_id,
                    result="succeeded",
                    metadata={"identity_provider": "google"},
                ),
            )
            session.commit()
    except OwnerSessionError as exc:
        raise ApiError(403, str(exc), "Owner identity is not authorized.") from exc

    response = RedirectResponse(_dashboard_login_redirect(settings), status_code=303)
    set_owner_session_cookies(response, issued)
    response.delete_cookie(OWNER_OIDC_COOKIE_NAME, path="/")
    response.headers["Cache-Control"] = "no-store"
    return response


def _dashboard_login_redirect(settings: Settings) -> str:
    if settings.frontend_origin:
        query = urlencode({"owner_session": "signed_in"})
        return f"{settings.frontend_origin.rstrip('/')}?{query}"
    return "/"


def _completion_response(
    *,
    status_code: int,
    title: str,
    body: str,
) -> HTMLResponse:
    response = HTMLResponse(
        content=(
            "<!doctype html>"
            "<html><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{html.escape(title)}</title></head>"
            "<body>"
            f"<main><h1>{html.escape(title)}</h1><p>{body}</p></main>"
            "</body></html>"
        ),
        status_code=status_code,
        headers={"Cache-Control": "no-store"},
    )
    response.delete_cookie(OWNER_OIDC_COOKIE_NAME, path="/")
    return response
