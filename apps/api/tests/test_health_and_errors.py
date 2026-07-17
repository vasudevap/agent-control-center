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


def test_versioned_health_uses_the_success_envelope() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/api/v1/health", headers={"X-Correlation-Id": "corr-api"})

    assert response.status_code == 200
    assert response.json() == {
        "data": {"status": "ok", "service": "atlas-api"},
        "meta": {"correlation_id": "corr-api"},
    }


def test_placeholder_endpoint_fails_closed_with_correlation_id() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get(
        "/api/v1/knowledge/facts",
        headers={"X-Correlation-Id": "corr-placeholder"},
    )

    assert response.status_code == 501
    expected_message = (
        "Knowledge fact APIs require a later approved Phase 5 work order."
    )
    assert response.json() == {
        "error": {
            "code": "knowledge_contract_not_implemented",
            "message": expected_message,
            "correlation_id": "corr-placeholder",
        },
    }
