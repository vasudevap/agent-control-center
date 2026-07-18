from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI
from sqlalchemy.orm import Session

from atlas_api.api.agent_registry import router as agent_registry_router
from atlas_api.api.routes import router
from atlas_api.core.config import Settings, get_settings
from atlas_api.core.correlation import CorrelationIdMiddleware
from atlas_api.core.errors import register_exception_handlers

OPENAPI_TAGS = [
    {"name": "health", "description": "Unversioned infrastructure health checks."},
    {"name": "api-health", "description": "Versioned API health contract."},
    {
        "name": "external-client",
        "description": "Signed external-client boundary probes.",
    },
    {"name": "agents", "description": "Generic agent registry contracts."},
    {"name": "knowledge", "description": "Reserved knowledge API contract."},
]


def create_app(
    settings: Settings | None = None,
    session_factory: Callable[[], Session] | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(
        title="Atlas API",
        version="0.1.0",
        description="Backend foundation for the Agent Control Center.",
        openapi_tags=OPENAPI_TAGS,
    )
    app.state.settings = resolved_settings
    app.state.session_factory = session_factory
    app.add_middleware(CorrelationIdMiddleware)
    register_exception_handlers(app)
    app.include_router(router)
    app.include_router(agent_registry_router)
    _configure_openapi(app)
    return app


def _configure_openapi(app: FastAPI) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, object]:
        if app.openapi_schema:
            return app.openapi_schema
        schema = original_openapi()
        schema.setdefault("components", {}).setdefault("securitySchemes", {})[
            "ExternalClientHmac"
        ] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-Atlas-Signature",
            "description": (
                "HMAC-SHA256 signature. Requests also require X-Atlas-Client-Id, "
                "X-Atlas-Key-Id, X-Atlas-Timestamp, and X-Atlas-Nonce."
            ),
        }
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]


app = create_app()
