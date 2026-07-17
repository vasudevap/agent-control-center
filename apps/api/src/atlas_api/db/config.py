from __future__ import annotations

from atlas_api.core.config import Settings


def require_database_url(settings: Settings) -> str:
    """Return the configured database URL or fail without exposing values."""
    if settings.database_url is None:
        raise RuntimeError(
            "ATLAS_API_DATABASE_URL is required for database migrations."
        )

    return settings.database_url.get_secret_value()
