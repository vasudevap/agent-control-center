from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "atlas-api"
    environment: str = "local"
    database_url: SecretStr | None = None
    external_client_secret: SecretStr | None = None
    webhook_signing_secret: SecretStr | None = None
    require_database: bool = False

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
    def redacted(self) -> dict[str, str | bool | None]:
        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "database_url": self._redact(self.database_url),
            "external_client_secret": self._redact(self.external_client_secret),
            "webhook_signing_secret": self._redact(self.webhook_signing_secret),
            "require_database": self.require_database,
        }

    @staticmethod
    def _redact(value: SecretStr | None) -> str | None:
        if value is None:
            return None
        return "***"


@lru_cache
def get_settings() -> Settings:
    return Settings()
