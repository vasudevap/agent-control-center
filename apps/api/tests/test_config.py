from __future__ import annotations

import pytest
from pydantic import ValidationError

from atlas_api.core.config import Settings
from atlas_api.db.config import require_database_url


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


def test_database_migrations_require_a_database_url() -> None:
    with pytest.raises(RuntimeError, match="ATLAS_API_DATABASE_URL is required"):
        require_database_url(Settings())


def test_database_migrations_receive_the_configured_database_url() -> None:
    settings = Settings(database_url="postgresql+psycopg://placeholder")

    assert require_database_url(settings) == "postgresql+psycopg://placeholder"


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
