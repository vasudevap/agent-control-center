from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass
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


@dataclass(frozen=True)
class IssuedAgentCredential:
    credential: AgentCredential
    plaintext_token: str


def issue_agent_credential(
    session: Session,
    *,
    agent: AgentRegistration,
    settings: Settings,
) -> IssuedAgentCredential:
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
        issued_at=utc_now(),
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
    parsed = parse_agent_token(token)
    if parsed is None:
        return None
    lookup_id, secret = parsed
    credential = session.scalar(
        select(AgentCredential).where(
            AgentCredential.credential_lookup_id == lookup_id,
            AgentCredential.status == "active",
        )
    )
    if credential is None:
        return None
    pepper = _require_agent_credential_pepper(settings)
    expected = _verifier(secret, pepper)
    if not hmac.compare_digest(expected, credential.verifier_hmac_sha256):
        return None
    credential.last_used_at = utc_now()
    return credential


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
