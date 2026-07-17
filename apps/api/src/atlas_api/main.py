from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI
from sqlalchemy.orm import Session

from atlas_api.api.routes import router
from atlas_api.core.config import Settings, get_settings
from atlas_api.core.correlation import CorrelationIdMiddleware
from atlas_api.core.errors import register_exception_handlers


def create_app(
    settings: Settings | None = None,
    session_factory: Callable[[], Session] | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(
        title="Atlas API",
        version="0.1.0",
        description="Backend foundation for the Agent Control Center.",
    )
    app.state.settings = resolved_settings
    app.state.session_factory = session_factory
    app.add_middleware(CorrelationIdMiddleware)
    register_exception_handlers(app)
    app.include_router(router)
    return app


app = create_app()
