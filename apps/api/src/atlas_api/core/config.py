from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "development", "test", "staging", "production"]
PRODUCTION_LIKE_ENVIRONMENTS = frozenset({"staging", "production"})


class Settings(BaseSettings):
    app_name: str = "atlas-api"
    environment: EnvironmentName = "local"
    database_url: SecretStr | None = None
    external_client_id: str | None = None
    external_client_secret: SecretStr | None = None
    external_client_key_id: str | None = None
    external_client_next_key_id: str | None = None
    external_client_next_secret: SecretStr | None = None
    webhook_signing_secret: SecretStr | None = None
    webhook_signing_key_id: str | None = None
    webhook_signing_next_secret: SecretStr | None = None
    webhook_signing_next_key_id: str | None = None
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: SecretStr | None = None
    google_oauth_redirect_uri: str | None = None
    owner_oidc_client_id: str | None = None
    owner_oidc_client_secret: SecretStr | None = None
    owner_oidc_redirect_uri: str | None = None
    owner_oidc_bootstrap_email: str | None = None
    owner_oidc_transaction_secret: SecretStr | None = None
    require_database: bool = False
    owner_identity_subject: str | None = None
    owner_session_idle_minutes: int = Field(default=30, ge=1, le=1440)
    owner_session_absolute_hours: int = Field(default=12, ge=1, le=168)
    frontend_origin: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="ATLAS_API_",
        env_file=".env",
        extra="ignore",
    )

    def readiness_problems(self) -> list[str]:
        problems: list[str] = []

        if self.environment in PRODUCTION_LIKE_ENVIRONMENTS:
            problems.extend(self._production_like_readiness_problems())

        if self.require_database and not self.database_url:
            problems.append("database_url_missing")

        return sorted(set(problems))

    @property
    def redacted(self) -> dict[str, str | bool | int | None]:
        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "database_url": self._redact(self.database_url),
            "external_client_secret": self._redact(self.external_client_secret),
            "external_client_id_configured": self.external_client_id is not None,
            "external_client_key_id_configured": (
                self.external_client_key_id is not None
            ),
            "external_client_next_key_id_configured": (
                self.external_client_next_key_id is not None
            ),
            "external_client_next_secret": self._redact(
                self.external_client_next_secret
            ),
            "webhook_signing_secret": self._redact(self.webhook_signing_secret),
            "webhook_signing_key_id_configured": (
                self.webhook_signing_key_id is not None
            ),
            "webhook_signing_next_key_id_configured": (
                self.webhook_signing_next_key_id is not None
            ),
            "webhook_signing_next_secret": self._redact(
                self.webhook_signing_next_secret
            ),
            "google_oauth_client_id_configured": (
                self.google_oauth_client_id is not None
            ),
            "google_oauth_client_secret": self._redact(
                self.google_oauth_client_secret
            ),
            "google_oauth_redirect_uri_configured": (
                self.google_oauth_redirect_uri is not None
            ),
            "owner_oidc_client_id_configured": self.owner_oidc_client_id is not None,
            "owner_oidc_client_secret": self._redact(
                self.owner_oidc_client_secret
            ),
            "owner_oidc_redirect_uri_configured": (
                self.owner_oidc_redirect_uri is not None
            ),
            "owner_oidc_bootstrap_email_configured": (
                self.owner_oidc_bootstrap_email is not None
            ),
            "owner_oidc_transaction_secret": self._redact(
                self.owner_oidc_transaction_secret
            ),
            "require_database": self.require_database,
            "owner_identity_subject_configured": (
                self.owner_identity_subject is not None
            ),
            "owner_session_idle_minutes": self.owner_session_idle_minutes,
            "owner_session_absolute_hours": self.owner_session_absolute_hours,
            "frontend_origin_configured": self.frontend_origin is not None,
        }

    @staticmethod
    def _redact(value: SecretStr | None) -> str | None:
        if value is None:
            return None
        return "***"

    def _production_like_readiness_problems(self) -> list[str]:
        required_values = {
            "database_url_missing": self.database_url,
            "external_client_id_missing": self.external_client_id,
            "external_client_key_id_missing": self.external_client_key_id,
            "external_client_secret_missing": self.external_client_secret,
            "google_oauth_client_id_missing": self.google_oauth_client_id,
            "google_oauth_client_secret_missing": self.google_oauth_client_secret,
            "google_oauth_redirect_uri_missing": self.google_oauth_redirect_uri,
            "owner_oidc_bootstrap_email_missing": self.owner_oidc_bootstrap_email,
            "owner_oidc_client_id_missing": self.owner_oidc_client_id,
            "owner_oidc_client_secret_missing": self.owner_oidc_client_secret,
            "owner_oidc_redirect_uri_missing": self.owner_oidc_redirect_uri,
            "owner_oidc_transaction_secret_missing": (
                self.owner_oidc_transaction_secret
            ),
            "owner_identity_subject_missing": self.owner_identity_subject,
            "webhook_signing_key_id_missing": self.webhook_signing_key_id,
            "webhook_signing_secret_missing": self.webhook_signing_secret,
        }
        return [problem for problem, value in required_values.items() if not value]


@lru_cache
def get_settings() -> Settings:
    return Settings()
