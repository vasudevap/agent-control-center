from __future__ import annotations

from atlas_api.core.config import Settings


def normalize_database_url_for_sqlalchemy(database_url: str) -> str:
    """Use the installed psycopg driver for provider-managed Postgres URLs."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    return database_url


def require_database_url(settings: Settings) -> str:
    """Return the configured database URL or fail without exposing values."""
    if settings.database_url is None:
        raise RuntimeError(
            "ATLAS_API_DATABASE_URL is required for database migrations."
        )

    return normalize_database_url_for_sqlalchemy(
        settings.database_url.get_secret_value()
    )
