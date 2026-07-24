from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.agent import AgentCredential, AgentRegistration

TOKEN_PREFIX = "atl_agent_"
CREDENTIAL_LOOKUP_PREFIX = "cred_"
CREDENTIAL_SCOPE = "telemetry_write"
ROTATION_OVERLAP_DURATION = timedelta(hours=24)


@dataclass(frozen=True)
class IssuedAgentCredential:
    credential: AgentCredential
    plaintext_token: str


def issue_agent_credential(
    session: Session,
    *,
    agent: AgentRegistration,
    settings: Settings,
    now: datetime | None = None,
) -> IssuedAgentCredential:
    issued_at = now or utc_now()
    pepper = _require_agent_credential_pepper(settings)
    key_id = _require_agent_credential_key_id(settings)
    lookup_id = _new_lookup_id()
    secret = secrets.token_urlsafe(32)
    credential = AgentCredential(
        agent_id=agent.agent_id,
        credential_lookup_id=lookup_id,
        verifier_hmac_sha256=_verifier(secret, pepper),
        verifier_key_id=key_id,
        status="active",
        scope=CREDENTIAL_SCOPE,
        issued_at=issued_at,
    )
    session.add(credential)
    session.flush()
    return IssuedAgentCredential(
        credential=credential,
        plaintext_token=f"{TOKEN_PREFIX}{lookup_id}.{secret}",
    )


def verify_agent_token(
    session: Session,
    *,
    token: str,
    settings: Settings,
) -> AgentCredential | None:
    now = utc_now()
    parsed = parse_agent_token(token)
    if parsed is None:
        return None
    lookup_id, secret = parsed
    credential = session.scalar(
        select(AgentCredential).where(
            AgentCredential.credential_lookup_id == lookup_id,
        )
    )
    if credential is None:
        return None
    if credential.status == "overlap":
        overlap_expires_at = _as_utc(credential.overlap_expires_at)
        if overlap_expires_at is None or overlap_expires_at <= now:
            credential.status = "expired"
            credential.expires_at = overlap_expires_at or now
            return None
    elif credential.status != "active":
        return None
    pepper = _require_agent_credential_pepper(settings)
    expected = _verifier(secret, pepper)
    if not hmac.compare_digest(expected, credential.verifier_hmac_sha256):
        return None
    credential.last_used_at = utc_now()
    return credential


def rotate_agent_credential(
    session: Session,
    *,
    agent: AgentRegistration,
    settings: Settings,
    now: datetime | None = None,
) -> IssuedAgentCredential:
    rotated_at = now or utc_now()
    active_credentials = list(
        session.scalars(
            select(AgentCredential).where(
                AgentCredential.agent_id == agent.agent_id,
                AgentCredential.status == "active",
            )
        )
    )
    if not active_credentials:
        raise ApiError(
            409,
            "agent_active_credential_missing",
            "Agent has no active credential to rotate.",
        )
    overlap_expires_at = rotated_at + ROTATION_OVERLAP_DURATION
    for credential in active_credentials:
        credential.status = "overlap"
        credential.overlap_expires_at = overlap_expires_at
    return issue_agent_credential(
        session,
        agent=agent,
        settings=settings,
        now=rotated_at,
    )


def revoke_agent_credentials(
    session: Session,
    *,
    agent: AgentRegistration,
    now: datetime | None = None,
) -> list[AgentCredential]:
    revoked_at = now or utc_now()
    credentials = list(
        session.scalars(
            select(AgentCredential).where(
                AgentCredential.agent_id == agent.agent_id,
                AgentCredential.status.in_(("active", "overlap")),
            )
        )
    )
    for credential in credentials:
        credential.status = "revoked"
        credential.revoked_at = revoked_at
        overlap_expires_at = _as_utc(credential.overlap_expires_at)
        if overlap_expires_at is not None:
            credential.overlap_expires_at = min(overlap_expires_at, revoked_at)
    return credentials


def parse_agent_token(token: str) -> tuple[str, str] | None:
    if not token.startswith(TOKEN_PREFIX):
        return None
    body = token.removeprefix(TOKEN_PREFIX)
    lookup_id, separator, secret = body.partition(".")
    if separator != "." or not lookup_id.startswith(CREDENTIAL_LOOKUP_PREFIX):
        return None
    if not lookup_id or not secret:
        return None
    return lookup_id, secret


def _new_lookup_id() -> str:
    return f"{CREDENTIAL_LOOKUP_PREFIX}{secrets.token_urlsafe(18)}"


def _verifier(secret: str, pepper: str) -> str:
    return hmac.new(
        pepper.encode("utf-8"),
        secret.encode("utf-8"),
        sha256,
    ).hexdigest()


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _require_agent_credential_pepper(settings: Settings) -> str:
    if settings.agent_credential_pepper is None:
        raise ApiError(
            503,
            "agent_credential_pepper_missing",
            "Agent credential pepper is not configured.",
        )
    return settings.agent_credential_pepper.get_secret_value()


def _require_agent_credential_key_id(settings: Settings) -> str:
    if settings.agent_credential_pepper_key_id is None:
        raise ApiError(
            503,
            "agent_credential_pepper_key_id_missing",
            "Agent credential pepper key id is not configured.",
        )
    return settings.agent_credential_pepper_key_id
