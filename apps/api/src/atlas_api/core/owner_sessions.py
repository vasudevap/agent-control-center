from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.models.external_client import ExternalProductClient, User
from atlas_api.models.owner_session import OwnerSession

SESSION_COOKIE_NAME = "atlas_owner_session"
CSRF_COOKIE_NAME = "atlas_csrf"


@dataclass(frozen=True)
class VerifiedIdentity:
    provider: str
    subject: str


@dataclass(frozen=True)
class IssuedOwnerSession:
    session_token: str
    csrf_token: str
    owner_session_id: str


@dataclass(frozen=True)
class OwnerSessionPrincipal:
    user_id: str
    owner_session_id: str


class OwnerSessionError(Exception):
    pass


def verify_owner_identity(identity: VerifiedIdentity, settings: Settings) -> None:
    if settings.owner_identity_subject is None:
        raise OwnerSessionError("owner_identity_not_configured")
    if identity.subject != settings.owner_identity_subject:
        raise OwnerSessionError("owner_identity_not_allowed")


def issue_owner_session(
    database: Session,
    *,
    user_id: str,
    settings: Settings,
    now: datetime,
) -> IssuedOwnerSession:
    session_token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)
    record = OwnerSession(
        user_id=user_id,
        session_token_hash=_digest(session_token),
        csrf_token_hash=_digest(csrf_token),
        issued_at=now,
        last_seen_at=now,
        idle_expires_at=now + timedelta(minutes=settings.owner_session_idle_minutes),
        absolute_expires_at=now
        + timedelta(hours=settings.owner_session_absolute_hours),
        revoked_at=None,
    )
    database.add(record)
    database.flush()
    return IssuedOwnerSession(
        session_token=session_token,
        csrf_token=csrf_token,
        owner_session_id=record.owner_session_id,
    )


def ensure_owner_user(
    database: Session,
    *,
    provider: str,
    subject: str,
    email: str,
    display_name: str,
    settings: Settings,
) -> User:
    verify_owner_identity(
        VerifiedIdentity(provider=provider, subject=subject),
        settings,
    )
    user = database.scalar(
        select(User).where(
            User.identity_provider == provider,
            User.identity_subject == subject,
        )
    )
    if user is None:
        user = User(
            email=email,
            display_name=display_name,
            identity_provider=provider,
            identity_subject=subject,
            status="active",
        )
        database.add(user)
        database.flush()
    elif user.status != "active":
        raise OwnerSessionError("owner_user_inactive")
    else:
        user.email = email
        user.display_name = display_name

    if settings.external_client_id is not None:
        client = database.get(ExternalProductClient, settings.external_client_id)
        if client is not None:
            if client.human_owner_user_id is None:
                client.human_owner_user_id = user.user_id
            elif client.human_owner_user_id != user.user_id:
                raise OwnerSessionError("owner_external_client_mismatch")
    database.flush()
    return user


def validate_owner_session(
    database: Session,
    *,
    session_token: str | None,
    csrf_token: str | None,
    require_csrf: bool,
    now: datetime,
) -> OwnerSessionPrincipal:
    if session_token is None:
        raise OwnerSessionError("owner_session_missing")

    record = database.scalar(
        select(OwnerSession).where(
            OwnerSession.session_token_hash == _digest(session_token)
        )
    )
    if record is None or record.revoked_at is not None:
        raise OwnerSessionError("owner_session_invalid")
    if now >= _as_utc(record.absolute_expires_at) or now >= _as_utc(
        record.idle_expires_at
    ):
        raise OwnerSessionError("owner_session_expired")
    if require_csrf and (
        csrf_token is None
        or not secrets.compare_digest(_digest(csrf_token), record.csrf_token_hash)
    ):
        raise OwnerSessionError("owner_session_csrf_invalid")

    record.last_seen_at = now
    return OwnerSessionPrincipal(
        user_id=record.user_id,
        owner_session_id=record.owner_session_id,
    )


def revoke_owner_session(
    database: Session,
    *,
    session_token: str | None,
    now: datetime,
) -> None:
    if session_token is None:
        return
    record = database.scalar(
        select(OwnerSession).where(
            OwnerSession.session_token_hash == _digest(session_token)
        )
    )
    if record is not None and record.revoked_at is None:
        record.revoked_at = now


def rotate_owner_session_csrf(
    database: Session,
    *,
    principal: OwnerSessionPrincipal,
) -> str:
    record = database.get(OwnerSession, principal.owner_session_id)
    if record is None or record.revoked_at is not None:
        raise OwnerSessionError("owner_session_invalid")
    csrf_token = secrets.token_urlsafe(32)
    record.csrf_token_hash = _digest(csrf_token)
    database.flush()
    return csrf_token


def set_owner_session_cookies(response: Response, issued: IssuedOwnerSession) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        issued.session_token,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
    )
    response.set_cookie(
        CSRF_COOKIE_NAME,
        issued.csrf_token,
        httponly=False,
        secure=True,
        samesite="strict",
        path="/",
    )


def clear_owner_session_cookies(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.delete_cookie(CSRF_COOKIE_NAME, path="/")


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
