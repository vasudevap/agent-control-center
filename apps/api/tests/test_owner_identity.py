from __future__ import annotations

from collections.abc import Callable
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from pydantic import SecretStr

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.main import create_app
from atlas_api.services.owner_identity import OwnerIdentityClaims


def owner_oidc_settings() -> Settings:
    return Settings(
        environment="test",
        owner_oidc_client_id="owner-oidc-client.apps.example.test",
        owner_oidc_client_secret=SecretStr("owner-oidc-secret"),
        owner_oidc_redirect_uri=(
            "https://api.atlas.grafley.com/auth/owner/google/callback"
        ),
        owner_oidc_bootstrap_email="grafleyinc@gmail.com",
        owner_oidc_transaction_secret=SecretStr("owner-oidc-transaction-secret"),
    )


def owner_client(
    *,
    verifier: Callable[..., OwnerIdentityClaims] | None = None,
    exchange: Callable[..., str] | None = None,
    settings: Settings | None = None,
) -> TestClient:
    app = create_app(settings or owner_oidc_settings())
    if exchange is not None:
        app.state.owner_oidc_token_exchange = exchange
    if verifier is not None:
        app.state.owner_oidc_id_token_verifier = verifier
    return TestClient(app, base_url="https://api.atlas.grafley.com")


def test_owner_oidc_start_sets_host_only_transaction_cookie_and_redirects() -> None:
    client = owner_client()

    response = client.get("/auth/owner/google/start", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["cache-control"] == "no-store"
    location = response.headers["location"]
    parsed = urlparse(location)
    query = parse_qs(parsed.query)
    assert location.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert query["client_id"] == ["owner-oidc-client.apps.example.test"]
    assert query["redirect_uri"] == [
        "https://api.atlas.grafley.com/auth/owner/google/callback"
    ]
    assert query["scope"] == ["openid email"]
    assert query["response_type"] == ["code"]
    assert query["code_challenge_method"] == ["S256"]
    assert query["state"][0]
    assert query["nonce"][0]
    assert query["code_challenge"][0]
    assert "owner-oidc-transaction-secret" not in response.text

    cookie = response.headers["set-cookie"]
    assert "__Host-atlas_owner_oidc=" in cookie
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=lax" in cookie
    assert "Path=/" in cookie
    assert "Domain=" not in cookie


def test_owner_oidc_callback_returns_minimized_subject_without_tokens() -> None:
    calls: dict[str, str] = {}

    def exchange(**kwargs: object) -> str:
        calls["authorization_code"] = str(kwargs["authorization_code"])
        calls["redirect_uri"] = str(kwargs["redirect_uri"])
        calls["pkce_verifier"] = str(kwargs["pkce_verifier"])
        return "fake-id-token"

    def verifier(**kwargs: object) -> OwnerIdentityClaims:
        assert kwargs["id_token"] == "fake-id-token"
        assert isinstance(kwargs["expected_nonce"], str)
        return OwnerIdentityClaims(
            subject="google-subject-123",
            email="grafleyinc@gmail.com",
            email_verified=True,
            nonce="provider-nonce",
        )

    client = owner_client(exchange=exchange, verifier=verifier)
    start = client.get("/auth/owner/google/start", follow_redirects=False)
    state = parse_qs(urlparse(start.headers["location"]).query)["state"][0]

    callback = client.get(
        f"/auth/owner/google/callback?state={state}&code=provider-code",
        follow_redirects=False,
    )

    assert callback.status_code == 200
    assert "Owner identity verified" in callback.text
    assert "google-subject-123" in callback.text
    assert "provider-code" not in callback.text
    assert "fake-id-token" not in callback.text
    assert "owner-oidc-secret" not in callback.text
    assert calls["authorization_code"] == "provider-code"
    assert calls["redirect_uri"] == (
        "https://api.atlas.grafley.com/auth/owner/google/callback"
    )
    assert calls["pkce_verifier"]
    assert callback.headers["cache-control"] == "no-store"
    assert "__Host-atlas_owner_oidc=" in callback.headers["set-cookie"]
    assert "Max-Age=0" in callback.headers["set-cookie"]


def test_owner_oidc_callback_rejects_bad_state_without_exposing_code() -> None:
    client = owner_client(exchange=lambda **_: "fake-id-token")
    client.get("/auth/owner/google/start", follow_redirects=False)

    response = client.get(
        "/auth/owner/google/callback?state=bad-state&code=provider-code"
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "owner_oidc_state_invalid"
    assert "provider-code" not in response.text


def test_owner_oidc_callback_rejects_tampered_cookie() -> None:
    client = owner_client(exchange=lambda **_: "fake-id-token")
    start = client.get("/auth/owner/google/start", follow_redirects=False)
    state = parse_qs(urlparse(start.headers["location"]).query)["state"][0]
    client.cookies.set(
        "__Host-atlas_owner_oidc",
        "tampered.transaction",
        domain="api.atlas.grafley.com",
        path="/",
    )

    response = client.get(
        f"/auth/owner/google/callback?state={state}&code=provider-code"
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "owner_oidc_transaction_invalid"
    assert "provider-code" not in response.text


def test_owner_oidc_callback_rejects_unverified_or_unexpected_email() -> None:
    def verifier(**_: object) -> OwnerIdentityClaims:
        return OwnerIdentityClaims(
            subject="google-subject-123",
            email="other@example.test",
            email_verified=True,
            nonce="provider-nonce",
        )

    client = owner_client(exchange=lambda **_: "fake-id-token", verifier=verifier)
    start = client.get("/auth/owner/google/start", follow_redirects=False)
    state = parse_qs(urlparse(start.headers["location"]).query)["state"][0]

    response = client.get(
        f"/auth/owner/google/callback?state={state}&code=provider-code"
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "owner_oidc_email_not_allowed"
    assert "provider-code" not in response.text
    assert "other@example.test" not in response.text


def test_owner_oidc_callback_surfaces_verifier_denial_without_token_material() -> None:
    def verifier(**_: object) -> OwnerIdentityClaims:
        raise ApiError(
            422,
            "owner_oidc_nonce_invalid",
            "Owner identity nonce is invalid.",
        )

    client = owner_client(exchange=lambda **_: "fake-id-token", verifier=verifier)
    start = client.get("/auth/owner/google/start", follow_redirects=False)
    state = parse_qs(urlparse(start.headers["location"]).query)["state"][0]

    response = client.get(
        f"/auth/owner/google/callback?state={state}&code=provider-code"
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "owner_oidc_nonce_invalid"
    assert "provider-code" not in response.text
    assert "fake-id-token" not in response.text


def test_owner_oidc_provider_denial_is_minimized_and_clears_cookie() -> None:
    client = owner_client()
    client.get("/auth/owner/google/start", follow_redirects=False)

    response = client.get(
        "/auth/owner/google/callback?error=access_denied&state=provider-state"
    )

    assert response.status_code == 400
    assert "Owner identity not verified" in response.text
    assert "access_denied" not in response.text
    assert "provider-state" not in response.text
    assert "__Host-atlas_owner_oidc=" in response.headers["set-cookie"]
    assert "Max-Age=0" in response.headers["set-cookie"]


def test_owner_oidc_start_fails_closed_when_not_configured() -> None:
    client = owner_client(settings=Settings(environment="test"))

    response = client.get("/auth/owner/google/start", follow_redirects=False)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "owner_oidc_not_configured"
