from __future__ import annotations

from fastapi.testclient import TestClient

from atlas_api.core.config import Settings
from atlas_api.main import create_app


def test_health_live_returns_service_status() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/health/live", headers={"X-Correlation-Id": "corr-test"})

    assert response.status_code == 200
    assert response.headers["X-Correlation-Id"] == "corr-test"
    assert response.json() == {
        "status": "ok",
        "service": "atlas-api",
        "environment": "test",
    }


def test_readiness_reports_missing_required_database() -> None:
    client = TestClient(create_app(Settings(environment="test", require_database=True)))

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "not_ready"
    assert response.json()["problems"] == ["database_url_missing"]


def test_readiness_omits_cors_headers_by_default() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get(
        "/health/ready",
        headers={"Origin": "https://atlas-agent-control-center.netlify.app"},
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_readiness_allows_configured_frontend_origin() -> None:
    frontend_origin = "https://atlas-agent-control-center.netlify.app"
    client = TestClient(
        create_app(Settings(environment="test", frontend_origin=frontend_origin))
    )

    response = client.get("/health/ready", headers={"Origin": frontend_origin})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == frontend_origin


def test_readiness_preflight_allows_configured_frontend_origin() -> None:
    frontend_origin = "https://atlas-agent-control-center.netlify.app"
    client = TestClient(
        create_app(Settings(environment="test", frontend_origin=frontend_origin))
    )

    response = client.options(
        "/health/ready",
        headers={
            "Origin": frontend_origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "accept",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == frontend_origin
    assert "GET" in response.headers["access-control-allow-methods"]


def test_readiness_reports_production_like_configuration_without_values() -> None:
    client = TestClient(create_app(Settings(environment="production")))

    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"] == {"configuration": "failed"}
    assert body["problems"] == [
        "agent_credential_pepper_key_id_missing",
        "agent_credential_pepper_missing",
        "database_url_missing",
        "external_client_id_missing",
        "external_client_key_id_missing",
        "external_client_secret_missing",
        "google_oauth_client_id_missing",
        "google_oauth_client_secret_missing",
        "google_oauth_redirect_uri_missing",
        "owner_identity_subject_missing",
        "owner_oidc_bootstrap_email_missing",
        "owner_oidc_client_id_missing",
        "owner_oidc_client_secret_missing",
        "owner_oidc_redirect_uri_missing",
        "owner_oidc_transaction_secret_missing",
        "webhook_signing_key_id_missing",
        "webhook_signing_secret_missing",
    ]
    assert "secret" not in response.text.lower().replace("_secret_missing", "")
    assert "postgresql://" not in response.text
    assert "gmail" not in response.text.lower().replace("google_oauth", "")


def test_versioned_health_uses_the_success_envelope() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/api/v1/health", headers={"X-Correlation-Id": "corr-api"})

    assert response.status_code == 200
    assert response.json() == {
        "data": {"status": "ok", "service": "atlas-api"},
        "meta": {"correlation_id": "corr-api"},
    }


def test_app_uses_database_url_for_default_session_factory() -> None:
    app = create_app(Settings(environment="test", database_url="sqlite://"))

    assert app.state.session_factory is not None
    with app.state.session_factory() as session:
        assert session.is_active


def test_knowledge_endpoint_requires_external_client_configuration() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get(
        "/api/v1/knowledge/facts",
        headers={"X-Correlation-Id": "corr-placeholder"},
    )

    assert response.status_code == 503
    expected_message = "External client authentication is not configured."
    assert response.json() == {
        "error": {
            "code": "external_client_authentication_not_configured",
            "message": expected_message,
            "correlation_id": "corr-placeholder",
        },
    }
