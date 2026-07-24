from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager, suppress

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.middleware.cors import CORSMiddleware

from atlas_api.api.agent_registry import router as agent_registry_router
from atlas_api.api.approvals import approval_router, manual_router
from atlas_api.api.connectors import router as connectors_router
from atlas_api.api.dashboard import router as dashboard_router
from atlas_api.api.knowledge_facts import router as knowledge_facts_router
from atlas_api.api.knowledge_questions import router as knowledge_questions_router
from atlas_api.api.owner_identity import router as owner_identity_router
from atlas_api.api.routes import router
from atlas_api.api.runs import router as runs_router
from atlas_api.core.config import Settings, get_settings
from atlas_api.core.correlation import CorrelationIdMiddleware
from atlas_api.core.errors import register_exception_handlers
from atlas_api.db.config import require_database_url
from atlas_api.services.agent_health_evaluator import (
    EVALUATOR_TICK_INTERVAL_SECONDS,
    evaluate_agent_health_once,
    record_evaluator_error,
)

OPENAPI_TAGS = [
    {"name": "health", "description": "Unversioned infrastructure health checks."},
    {"name": "api-health", "description": "Versioned API health contract."},
    {
        "name": "external-client",
        "description": "Signed external-client boundary probes.",
    },
    {"name": "agents", "description": "Generic agent registry contracts."},
    {"name": "approvals", "description": "Generic approval decision contracts."},
    {"name": "connectors", "description": "Connector OAuth and health contracts."},
    {
        "name": "dashboard",
        "description": "Owner-authenticated dashboard runtime facade.",
    },
    {"name": "knowledge", "description": "Reserved knowledge API contract."},
    {
        "name": "manual-handling",
        "description": "Non-approval manual-handling contracts.",
    },
    {
        "name": "owner-identity",
        "description": "Single-owner Google OIDC enrollment boundary.",
    },
    {"name": "runs", "description": "Generic run lifecycle contracts."},
]


def create_app(
    settings: Settings | None = None,
    session_factory: Callable[[], Session] | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_session_factory = session_factory or _session_factory_from_settings(
        resolved_settings
    )
    app = FastAPI(
        title="Atlas API",
        version="0.1.0",
        description="Backend foundation for the Agent Control Center.",
        openapi_tags=OPENAPI_TAGS,
        lifespan=_agent_health_evaluator_lifespan(
            settings=resolved_settings,
            session_factory=resolved_session_factory,
        ),
    )
    app.state.settings = resolved_settings
    app.state.session_factory = resolved_session_factory
    app.state.agent_health_evaluator_task = None
    if resolved_settings.frontend_origin:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[resolved_settings.frontend_origin],
            allow_methods=["GET", "POST"],
            allow_headers=[
                "Accept",
                "Content-Type",
                "Idempotency-Key",
                "X-Atlas-CSRF-Token",
                "X-Correlation-Id",
            ],
            allow_credentials=True,
        )
    app.add_middleware(CorrelationIdMiddleware)
    register_exception_handlers(app)
    app.include_router(router)
    app.include_router(agent_registry_router)
    app.include_router(approval_router)
    app.include_router(manual_router)
    app.include_router(connectors_router)
    app.include_router(dashboard_router)
    app.include_router(owner_identity_router)
    app.include_router(knowledge_facts_router)
    app.include_router(knowledge_questions_router)
    app.include_router(runs_router)
    _configure_openapi(app)
    return app


def _session_factory_from_settings(
    settings: Settings,
) -> Callable[[], Session] | None:
    if settings.database_url is None:
        return None
    engine = create_engine(require_database_url(settings), pool_pre_ping=True)
    return sessionmaker(engine)


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


def _agent_health_evaluator_lifespan(
    *,
    settings: Settings,
    session_factory: Callable[[], Session] | None,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None, bool | None]] | None:
    if not settings.agent_health_evaluator_enabled or session_factory is None:
        return None

    holder_id = f"{settings.app_name}:{os.getpid()}"

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.agent_health_evaluator_task = asyncio.create_task(
            _agent_health_evaluator_loop(
                session_factory=session_factory,
                holder_id=holder_id,
            )
        )
        try:
            yield
        finally:
            task = app.state.agent_health_evaluator_task
            if task is not None:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

    return lifespan


async def _agent_health_evaluator_loop(
    *,
    session_factory: Callable[[], Session],
    holder_id: str,
) -> None:
    while True:
        try:
            with session_factory() as session:
                evaluate_agent_health_once(session, holder_id=holder_id)
                session.commit()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            with suppress(Exception):
                with session_factory() as session:
                    record_evaluator_error(
                        session,
                        holder_id=holder_id,
                        error_code=exc.__class__.__name__,
                    )
                    session.commit()
        await asyncio.sleep(EVALUATOR_TICK_INTERVAL_SECONDS)


app = create_app()
