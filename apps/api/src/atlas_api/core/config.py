from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "development", "test", "staging", "production"]


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
    require_database: bool = False
    owner_identity_subject: str | None = None
    owner_session_idle_minutes: int = Field(default=30, ge=1, le=1440)
    owner_session_absolute_hours: int = Field(default=12, ge=1, le=168)

    model_config = SettingsConfigDict(
        env_prefix="ATLAS_API_",
        env_file=".env",
        extra="ignore",
    )

    def readiness_problems(self) -> list[str]:
        problems: list[str] = []

        if self.environment in {"production", "staging"} and not self.database_url:
            problems.append("database_url_missing")

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
            "external_client_next_secret": self._redact(
                self.external_client_next_secret
            ),
            "webhook_signing_secret": self._redact(self.webhook_signing_secret),
            "webhook_signing_next_secret": self._redact(
                self.webhook_signing_next_secret
            ),
            "require_database": self.require_database,
            "owner_identity_subject_configured": (
                self.owner_identity_subject is not None
            ),
            "owner_session_idle_minutes": self.owner_session_idle_minutes,
            "owner_session_absolute_hours": self.owner_session_absolute_hours,
        }

    @staticmethod
    def _redact(value: SecretStr | None) -> str | None:
        if value is None:
            return None
        return "***"


@lru_cache
def get_settings() -> Settings:
    return Settings()
