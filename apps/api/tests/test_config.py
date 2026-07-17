from __future__ import annotations

import pytest
from pydantic import ValidationError

from atlas_api.core.config import Settings


def test_local_and_development_do_not_require_a_database_by_default() -> None:
    assert Settings(environment="local").readiness_problems() == []
    assert Settings(environment="development").readiness_problems() == []


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_production_like_environments_require_a_database(environment: str) -> None:
    assert Settings(environment=environment).readiness_problems() == [
        "database_url_missing"
    ]


def test_explicit_database_requirement_is_enforced() -> None:
    assert Settings(require_database=True).readiness_problems() == [
        "database_url_missing"
    ]


def test_secret_settings_are_redacted() -> None:
    settings = Settings(
        database_url="postgresql://example-user:example-password@example-host/example-db",
        external_client_secret="example-external-client-secret",
        webhook_signing_secret="example-webhook-signing-secret",
    )

    assert settings.redacted == {
        "app_name": "atlas-api",
        "environment": "local",
        "database_url": "***",
        "external_client_secret": "***",
        "webhook_signing_secret": "***",
        "require_database": False,
    }


def test_unsupported_environment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="preview")
