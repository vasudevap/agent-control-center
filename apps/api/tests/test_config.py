from __future__ import annotations

import pytest
from pydantic import ValidationError

from atlas_api.core.config import Settings
from atlas_api.db.config import (
    normalize_database_url_for_sqlalchemy,
    require_database_url,
)


def test_local_and_development_do_not_require_a_database_by_default() -> None:
    assert Settings(environment="local").readiness_problems() == []
    assert Settings(environment="development").readiness_problems() == []


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_production_like_environments_require_release_configuration(
    environment: str,
) -> None:
    assert Settings(environment=environment).readiness_problems() == [
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


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_production_like_readiness_passes_with_required_release_configuration(
    environment: str,
) -> None:
    settings = Settings(
        environment=environment,
        database_url="postgresql+psycopg://placeholder",
        external_client_id="atlas-external-client",
        external_client_key_id="atlas-key-current",
        external_client_secret="example-external-client-secret",
        google_oauth_client_id="google-oauth-client-id.example.test",
        google_oauth_client_secret="example-google-oauth-client-secret",
        google_oauth_redirect_uri="https://atlas.example.test/oauth/google/callback",
        owner_oidc_client_id="owner-oidc-client-id.example.test",
        owner_oidc_client_secret="example-owner-oidc-client-secret",
        owner_oidc_redirect_uri=(
            "https://api.atlas.example.test/auth/owner/google/callback"
        ),
        owner_oidc_bootstrap_email="owner@example.test",
        owner_oidc_transaction_secret="example-owner-oidc-transaction-secret",
        owner_identity_subject="owner@example.test",
        webhook_signing_key_id="atlas-webhook-current",
        webhook_signing_secret="example-webhook-signing-secret",
    )

    assert settings.readiness_problems() == []


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


@pytest.mark.parametrize(
    ("database_url", "expected"),
    [
        (
            "postgresql://user:pass@example.test/db",
            "postgresql+psycopg://user:pass@example.test/db",
        ),
        (
            "postgres://user:pass@example.test/db",
            "postgresql+psycopg://user:pass@example.test/db",
        ),
        (
            "postgresql+psycopg://user:pass@example.test/db",
            "postgresql+psycopg://user:pass@example.test/db",
        ),
        ("sqlite:////tmp/atlas.db", "sqlite:////tmp/atlas.db"),
    ],
)
def test_database_urls_are_normalized_for_sqlalchemy(
    database_url: str,
    expected: str,
) -> None:
    assert normalize_database_url_for_sqlalchemy(database_url) == expected


def test_secret_settings_are_redacted() -> None:
    settings = Settings(
        database_url="postgresql://example-user:example-password@example-host/example-db",
        external_client_id="atlas-external-client",
        external_client_key_id="atlas-key-current",
        external_client_secret="example-external-client-secret",
        external_client_next_key_id="atlas-key-next",
        external_client_next_secret="example-external-client-next-secret",
        webhook_signing_key_id="atlas-webhook-current",
        webhook_signing_secret="example-webhook-signing-secret",
        webhook_signing_next_key_id="atlas-webhook-next",
        webhook_signing_next_secret="example-webhook-signing-next-secret",
        google_oauth_client_id="google-oauth-client-id.example.test",
        google_oauth_client_secret="example-google-oauth-client-secret",
        google_oauth_redirect_uri="https://atlas.example.test/oauth/google/callback",
        owner_oidc_client_id="owner-oidc-client-id.example.test",
        owner_oidc_client_secret="example-owner-oidc-client-secret",
        owner_oidc_redirect_uri=(
            "https://api.atlas.example.test/auth/owner/google/callback"
        ),
        owner_oidc_bootstrap_email="owner@example.test",
        owner_oidc_transaction_secret="example-owner-oidc-transaction-secret",
    )

    assert settings.redacted == {
        "app_name": "atlas-api",
        "environment": "local",
        "database_url": "***",
        "external_client_secret": "***",
        "external_client_id_configured": True,
        "external_client_key_id_configured": True,
        "external_client_next_key_id_configured": True,
        "external_client_next_secret": "***",
        "webhook_signing_secret": "***",
        "webhook_signing_key_id_configured": True,
        "webhook_signing_next_key_id_configured": True,
        "webhook_signing_next_secret": "***",
        "google_oauth_client_id_configured": True,
        "google_oauth_client_secret": "***",
        "google_oauth_redirect_uri_configured": True,
        "owner_oidc_client_id_configured": True,
        "owner_oidc_client_secret": "***",
        "owner_oidc_redirect_uri_configured": True,
        "owner_oidc_bootstrap_email_configured": True,
        "owner_oidc_transaction_secret": "***",
        "require_database": False,
        "owner_identity_subject_configured": False,
        "owner_session_idle_minutes": 30,
        "owner_session_absolute_hours": 12,
        "frontend_origin_configured": False,
    }


def test_unsupported_environment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="preview")
