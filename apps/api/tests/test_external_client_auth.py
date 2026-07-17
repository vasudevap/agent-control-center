from __future__ import annotations

from fastapi.testclient import TestClient
from pydantic import SecretStr

from atlas_api.core.config import Settings
from atlas_api.main import create_app


def test_external_client_auth_fails_closed_when_unconfigured() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/api/v1/external-client/authentication/probe")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == (
        "external_client_authentication_not_configured"
    )


def test_external_client_auth_rejects_missing_credentials() -> None:
    client = TestClient(
        create_app(
            Settings(
                environment="test",
                external_client_secret=SecretStr("expected-secret"),
            ),
        ),
    )

    response = client.get("/api/v1/external-client/authentication/probe")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "external_client_credentials_required"


def test_external_client_auth_accepts_valid_client_without_human_attribution() -> None:
    client = TestClient(
        create_app(
            Settings(
                environment="test",
                external_client_secret=SecretStr("expected-secret"),
            ),
        ),
    )

    response = client.get(
        "/api/v1/external-client/authentication/probe",
        headers={
            "X-Atlas-Client-Id": "external-client-1",
            "X-Atlas-Client-Secret": "expected-secret",
        },
    )

    assert response.status_code == 200
    assert response.json()["external_client_id"] == "external-client-1"
    assert "human" not in response.text.lower()
