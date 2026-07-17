from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi import Response
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.owner_sessions import (
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    OwnerSessionError,
    VerifiedIdentity,
    clear_owner_session_cookies,
    issue_owner_session,
    revoke_owner_session,
    set_owner_session_cookies,
    validate_owner_session,
    verify_owner_identity,
)
from atlas_api.db.base import Base
from atlas_api.models import owner_session  # noqa: F401
from atlas_api.models.external_client import User


@pytest.fixture
def database() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(
            User(
                email="owner@example.test",
                display_name="Owner",
                identity_provider="test",
                identity_subject="owner-subject",
            )
        )
        session.commit()
        yield session


def test_owner_identity_fails_closed_without_configured_subject() -> None:
    with pytest.raises(OwnerSessionError, match="owner_identity_not_configured"):
        verify_owner_identity(
            VerifiedIdentity(provider="test", subject="owner"),
            Settings(),
        )


def test_owner_identity_rejects_non_owner() -> None:
    with pytest.raises(OwnerSessionError, match="owner_identity_not_allowed"):
        verify_owner_identity(
            VerifiedIdentity(provider="test", subject="other"),
            Settings(owner_identity_subject="owner"),
        )


def test_session_lifecycle_requires_csrf_and_supports_revocation(
    database: Session,
) -> None:
    user = database.scalar(select(User))
    assert user is not None
    now = datetime(2026, 7, 17, tzinfo=UTC)
    issued = issue_owner_session(
        database,
        user_id=user.user_id,
        settings=Settings(owner_identity_subject="owner"),
        now=now,
    )
    database.commit()

    principal = validate_owner_session(
        database,
        session_token=issued.session_token,
        csrf_token=issued.csrf_token,
        require_csrf=True,
        now=now + timedelta(minutes=1),
    )
    assert principal.user_id == user.user_id

    with pytest.raises(OwnerSessionError, match="owner_session_csrf_invalid"):
        validate_owner_session(
            database,
            session_token=issued.session_token,
            csrf_token=None,
            require_csrf=True,
            now=now + timedelta(minutes=1),
        )

    revoke_owner_session(database, session_token=issued.session_token, now=now)
    database.commit()
    with pytest.raises(OwnerSessionError, match="owner_session_invalid"):
        validate_owner_session(
            database,
            session_token=issued.session_token,
            csrf_token=issued.csrf_token,
            require_csrf=False,
            now=now + timedelta(minutes=1),
        )


def test_session_expiry_and_cookie_flags(database: Session) -> None:
    user = database.scalar(select(User))
    assert user is not None
    now = datetime(2026, 7, 17, tzinfo=UTC)
    issued = issue_owner_session(
        database,
        user_id=user.user_id,
        settings=Settings(owner_identity_subject="owner", owner_session_idle_minutes=1),
        now=now,
    )
    database.commit()

    with pytest.raises(OwnerSessionError, match="owner_session_expired"):
        validate_owner_session(
            database,
            session_token=issued.session_token,
            csrf_token=None,
            require_csrf=False,
            now=now + timedelta(minutes=1),
        )

    response = Response()
    set_owner_session_cookies(response, issued)
    cookie_headers = response.headers.getlist("set-cookie")
    assert any(
        SESSION_COOKIE_NAME in value and "HttpOnly" in value for value in cookie_headers
    )
    assert any(
        CSRF_COOKIE_NAME in value and "HttpOnly" not in value
        for value in cookie_headers
    )
    assert all(
        "Secure" in value and "SameSite=strict" in value for value in cookie_headers
    )

    clear_owner_session_cookies(response)
    assert len(response.headers.getlist("set-cookie")) == 4
