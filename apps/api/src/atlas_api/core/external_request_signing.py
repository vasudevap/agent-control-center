from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from atlas_api.core.config import Settings


@dataclass(frozen=True)
class SignedExternalRequest:
    client_id: str
    key_id: str
    timestamp: int
    nonce: str
    signature: str
    method: str
    path_query: str
    body: bytes


class ExternalRequestSignatureError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def verify_signature(
    request: SignedExternalRequest,
    settings: Settings,
    *,
    now: datetime,
) -> None:
    secret = _secret_for_key(request.key_id, settings)
    timestamp = datetime.fromtimestamp(request.timestamp, tz=UTC)
    if abs(now - timestamp) > timedelta(minutes=5):
        raise ExternalRequestSignatureError("external_client_timestamp_invalid")
    expected = sign_request(request, secret)
    if not hmac.compare_digest(request.signature, expected):
        raise ExternalRequestSignatureError("external_client_signature_invalid")


def sign_request(request: SignedExternalRequest, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        _canonical_message(request).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _secret_for_key(key_id: str, settings: Settings) -> str:
    if key_id == settings.external_client_key_id and settings.external_client_secret:
        return settings.external_client_secret.get_secret_value()
    if (
        key_id == settings.external_client_next_key_id
        and settings.external_client_next_secret
    ):
        return settings.external_client_next_secret.get_secret_value()
    raise ExternalRequestSignatureError("external_client_key_unknown")


def _canonical_message(request: SignedExternalRequest) -> str:
    body_digest = hashlib.sha256(request.body).hexdigest()
    return "\n".join(
        [
            request.method.upper(),
            request.path_query,
            str(request.timestamp),
            request.nonce,
            body_digest,
        ]
    )
