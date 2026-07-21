from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError

OWNER_OIDC_COOKIE_NAME = "__Host-atlas_owner_oidc"
OWNER_OIDC_SCOPES = ("openid", "email")
OWNER_OIDC_TRANSACTION_TTL = timedelta(minutes=10)
GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")


@dataclass(frozen=True)
class OwnerOidcAuthorization:
    authorization_url: str
    cookie_value: str
    max_age_seconds: int


@dataclass(frozen=True)
class OwnerOidcTransaction:
    state_hash: str
    nonce_hash: str
    pkce_verifier_hash: str
    pkce_verifier: str
    redirect_uri: str
    expires_at: datetime


@dataclass(frozen=True)
class OwnerIdentityClaims:
    subject: str
    email: str
    email_verified: bool
    nonce: str


class OwnerTokenExchange(Protocol):
    def __call__(
        self,
        *,
        settings: Settings,
        authorization_code: str,
        redirect_uri: str,
        pkce_verifier: str,
    ) -> str: ...


class OwnerIdTokenVerifier(Protocol):
    def __call__(
        self,
        *,
        settings: Settings,
        id_token: str,
        expected_nonce: str,
        now: datetime,
    ) -> OwnerIdentityClaims: ...


def start_owner_oidc_authorization(
    settings: Settings,
    *,
    now: datetime,
) -> OwnerOidcAuthorization:
    _require_owner_oidc_config(settings)
    assert settings.owner_oidc_client_id is not None
    assert settings.owner_oidc_redirect_uri is not None

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    pkce_verifier = secrets.token_urlsafe(64)
    expires_at = now + OWNER_OIDC_TRANSACTION_TTL
    transaction = OwnerOidcTransaction(
        state_hash=_digest(state),
        nonce_hash=_digest(nonce),
        pkce_verifier_hash=_digest(pkce_verifier),
        pkce_verifier=pkce_verifier,
        redirect_uri=settings.owner_oidc_redirect_uri,
        expires_at=expires_at,
    )
    query = urlencode(
        {
            "response_type": "code",
            "client_id": settings.owner_oidc_client_id,
            "redirect_uri": settings.owner_oidc_redirect_uri,
            "scope": " ".join(OWNER_OIDC_SCOPES),
            "state": state,
            "nonce": nonce,
            "code_challenge": _pkce_code_challenge(pkce_verifier),
            "code_challenge_method": "S256",
            "prompt": "select_account",
        }
    )
    return OwnerOidcAuthorization(
        authorization_url=f"{GOOGLE_AUTHORIZATION_ENDPOINT}?{query}",
        cookie_value=serialize_owner_oidc_transaction(settings, transaction),
        max_age_seconds=int(OWNER_OIDC_TRANSACTION_TTL.total_seconds()),
    )


def complete_owner_oidc_authorization(
    settings: Settings,
    *,
    state: str | None,
    authorization_code: str | None,
    cookie_value: str | None,
    now: datetime,
    exchange: OwnerTokenExchange | None = None,
    verifier: OwnerIdTokenVerifier | None = None,
) -> OwnerIdentityClaims:
    if not state or len(state) > 160:
        raise ApiError(422, "owner_oidc_state_invalid", "OIDC state is invalid.")
    if not authorization_code or len(authorization_code) > 1024:
        raise ApiError(
            422,
            "owner_oidc_authorization_code_invalid",
            "OIDC authorization code is invalid.",
        )
    transaction = parse_owner_oidc_transaction(settings, cookie_value, now=now)
    if not secrets.compare_digest(transaction.state_hash, _digest(state)):
        raise ApiError(422, "owner_oidc_state_invalid", "OIDC state is invalid.")
    id_token = (exchange or exchange_owner_oidc_code)(
        settings=settings,
        authorization_code=authorization_code,
        redirect_uri=transaction.redirect_uri,
        pkce_verifier=transaction.pkce_verifier,
    )
    claims = (verifier or verify_google_owner_id_token)(
        settings=settings,
        id_token=id_token,
        expected_nonce=transaction.nonce_hash,
        now=now,
    )
    _validate_owner_claims(settings, claims)
    return claims


def serialize_owner_oidc_transaction(
    settings: Settings,
    transaction: OwnerOidcTransaction,
) -> str:
    secret = _transaction_secret(settings)
    payload = {
        "state_hash": transaction.state_hash,
        "nonce_hash": transaction.nonce_hash,
        "pkce_verifier_hash": transaction.pkce_verifier_hash,
        "pkce_verifier": transaction.pkce_verifier,
        "redirect_uri": transaction.redirect_uri,
        "expires_at": transaction.expires_at.isoformat(),
    }
    encoded_payload = _urlsafe_json(payload)
    signature = _sign(encoded_payload, secret)
    return f"{encoded_payload}.{signature}"


def parse_owner_oidc_transaction(
    settings: Settings,
    cookie_value: str | None,
    *,
    now: datetime,
) -> OwnerOidcTransaction:
    if not cookie_value or "." not in cookie_value:
        raise ApiError(
            422,
            "owner_oidc_transaction_invalid",
            "OIDC transaction is invalid.",
        )
    encoded_payload, signature = cookie_value.rsplit(".", 1)
    expected_signature = _sign(encoded_payload, _transaction_secret(settings))
    if not secrets.compare_digest(signature, expected_signature):
        raise ApiError(
            422,
            "owner_oidc_transaction_invalid",
            "OIDC transaction is invalid.",
        )
    try:
        payload = json.loads(_urlsafe_decode(encoded_payload).decode("utf-8"))
        expires_at = datetime.fromisoformat(_required_string(payload, "expires_at"))
        transaction = OwnerOidcTransaction(
            state_hash=_required_string(payload, "state_hash"),
            nonce_hash=_required_string(payload, "nonce_hash"),
            pkce_verifier_hash=_required_string(payload, "pkce_verifier_hash"),
            pkce_verifier=_required_string(payload, "pkce_verifier"),
            redirect_uri=_required_string(payload, "redirect_uri"),
            expires_at=_as_utc(expires_at),
        )
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError, KeyError) as exc:
        raise ApiError(
            422,
            "owner_oidc_transaction_invalid",
            "OIDC transaction is invalid.",
        ) from exc
    if transaction.expires_at <= now:
        raise ApiError(
            422,
            "owner_oidc_transaction_expired",
            "OIDC transaction is expired.",
        )
    if not secrets.compare_digest(
        transaction.pkce_verifier_hash,
        _digest(transaction.pkce_verifier),
    ):
        raise ApiError(
            422,
            "owner_oidc_transaction_invalid",
            "OIDC transaction is invalid.",
        )
    if transaction.redirect_uri != settings.owner_oidc_redirect_uri:
        raise ApiError(
            422,
            "owner_oidc_redirect_uri_invalid",
            "OIDC redirect URI is invalid.",
        )
    return transaction


def exchange_owner_oidc_code(
    *,
    settings: Settings,
    authorization_code: str,
    redirect_uri: str,
    pkce_verifier: str,
) -> str:
    _require_owner_oidc_config(settings)
    assert settings.owner_oidc_client_id is not None
    assert settings.owner_oidc_client_secret is not None
    body = urlencode(
        {
            "code": authorization_code,
            "client_id": settings.owner_oidc_client_id,
            "client_secret": settings.owner_oidc_client_secret.get_secret_value(),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": pkce_verifier,
        }
    ).encode("utf-8")
    request = Request(
        GOOGLE_TOKEN_ENDPOINT,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise ApiError(
            502,
            "owner_oidc_exchange_failed",
            "Owner identity exchange failed.",
        ) from exc
    if not isinstance(payload, dict):
        raise ApiError(
            502,
            "owner_oidc_exchange_failed",
            "Owner identity exchange failed.",
        )
    id_token = payload.get("id_token")
    if not isinstance(id_token, str) or not id_token.strip():
        raise ApiError(
            502,
            "owner_oidc_id_token_missing",
            "Owner identity token is unavailable.",
        )
    return id_token


def verify_google_owner_id_token(
    *,
    settings: Settings,
    id_token: str,
    expected_nonce: str,
    now: datetime,
) -> OwnerIdentityClaims:
    if settings.owner_oidc_client_id is None:
        raise ApiError(
            503,
            "owner_oidc_not_configured",
            "Owner identity verification is not configured.",
        )
    try:
        from jwt import (  # type: ignore[import-not-found]
            PyJWKClient,
            PyJWTError,
            decode,
        )
    except ImportError as exc:
        raise ApiError(
            503,
            "owner_oidc_verifier_unavailable",
            "Owner identity verifier is unavailable.",
        ) from exc
    try:
        signing_key = PyJWKClient(GOOGLE_JWKS_URI).get_signing_key_from_jwt(id_token)
        decoded = decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.owner_oidc_client_id,
            issuer=GOOGLE_ISSUERS,
            options={"require": ["aud", "exp", "iat", "iss", "nonce", "sub"]},
            leeway=60,
        )
    except PyJWTError as exc:
        raise ApiError(
            422,
            "owner_oidc_id_token_invalid",
            "Owner identity token is invalid.",
        ) from exc
    if not isinstance(decoded, dict):
        raise ApiError(
            422,
            "owner_oidc_id_token_invalid",
            "Owner identity token is invalid.",
        )
    issued_at = decoded.get("iat")
    if isinstance(issued_at, int) and issued_at > int(now.timestamp()) + 60:
        raise ApiError(
            422,
            "owner_oidc_id_token_invalid",
            "Owner identity token is invalid.",
        )
    nonce = _claim_string(decoded, "nonce")
    if not secrets.compare_digest(_digest(nonce), expected_nonce):
        raise ApiError(
            422,
            "owner_oidc_nonce_invalid",
            "Owner identity nonce is invalid.",
        )
    return OwnerIdentityClaims(
        subject=_claim_string(decoded, "sub"),
        email=_claim_string(decoded, "email"),
        email_verified=decoded.get("email_verified") is True,
        nonce=nonce,
    )


def _validate_owner_claims(settings: Settings, claims: OwnerIdentityClaims) -> None:
    bootstrap_email = settings.owner_oidc_bootstrap_email
    if not bootstrap_email:
        raise ApiError(
            503,
            "owner_oidc_bootstrap_email_missing",
            "Owner identity bootstrap email is not configured.",
        )
    if not claims.email_verified:
        raise ApiError(
            422,
            "owner_oidc_email_unverified",
            "Owner identity email is not verified.",
        )
    if claims.email.casefold() != bootstrap_email.casefold():
        raise ApiError(
            403,
            "owner_oidc_email_not_allowed",
            "Owner identity email is not allowed.",
        )
    if not claims.subject.strip() or len(claims.subject) > 160:
        raise ApiError(
            422,
            "owner_oidc_subject_invalid",
            "Owner identity subject is invalid.",
        )


def _require_owner_oidc_config(settings: Settings) -> None:
    if not (
        settings.owner_oidc_client_id
        and settings.owner_oidc_client_secret
        and settings.owner_oidc_redirect_uri
        and settings.owner_oidc_bootstrap_email
        and settings.owner_oidc_transaction_secret
    ):
        raise ApiError(
            503,
            "owner_oidc_not_configured",
            "Owner identity verification is not configured.",
        )


def _transaction_secret(settings: Settings) -> str:
    if settings.owner_oidc_transaction_secret is None:
        raise ApiError(
            503,
            "owner_oidc_not_configured",
            "Owner identity verification is not configured.",
        )
    return settings.owner_oidc_transaction_secret.get_secret_value()


def _urlsafe_json(payload: dict[str, str]) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(body).decode("ascii").rstrip("=")


def _urlsafe_decode(value: str) -> bytes:
    padded = value + ("=" * (-len(value) % 4))
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _sign(value: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), value.encode("ascii"), hashlib.sha256)
    return base64.urlsafe_b64encode(digest.digest()).decode("ascii").rstrip("=")


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _pkce_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _claim_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ApiError(
            422,
            "owner_oidc_id_token_invalid",
            "Owner identity token is invalid.",
        )
    return value


def _required_string(payload: dict[str, Any], key: str) -> str:
    value = payload[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(key)
    return value


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def owner_token_exchange_from_app_state(value: object) -> OwnerTokenExchange | None:
    return cast("OwnerTokenExchange | None", value)


def owner_id_token_verifier_from_app_state(
    value: object,
) -> OwnerIdTokenVerifier | None:
    return cast("OwnerIdTokenVerifier | None", value)
