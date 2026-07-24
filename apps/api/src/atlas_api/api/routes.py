from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from atlas_api.core.auth import ExternalClientPrincipal, verify_external_client
from atlas_api.core.config import Settings
from atlas_api.core.contracts import success_payload
from atlas_api.core.correlation import get_correlation_id
from atlas_api.services.agent_health_evaluator import evaluator_freshness

router = APIRouter()


def get_request_settings(request: Request) -> Settings:
    return cast("Settings", request.app.state.settings)


def _session_factory_from_request(request: Request) -> Callable[[], Session] | None:
    return cast("Callable[[], Session] | None", request.app.state.session_factory)


SettingsDependency = Annotated[Settings, Depends(get_request_settings)]
ExternalClientDependency = Annotated[
    ExternalClientPrincipal,
    Depends(verify_external_client),
]


@router.get("/health/live", tags=["health"])
def live(settings: SettingsDependency) -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }


@router.get("/health/ready", tags=["health"])
def ready(request: Request, settings: SettingsDependency) -> dict[str, object]:
    problems = settings.readiness_problems()
    checks: dict[str, object] = {
        "configuration": "ok" if not problems else "failed",
    }
    if settings.agent_health_evaluator_enabled:
        evaluator_problem, evaluator_check = _agent_health_evaluator_readiness(
            request,
        )
        checks["agent_health_evaluator"] = evaluator_check
        if evaluator_problem is not None:
            problems.append(evaluator_problem)
    return {
        "status": "ready" if not problems else "not_ready",
        "service": settings.app_name,
        "checks": checks,
        "problems": problems,
    }


def _agent_health_evaluator_readiness(
    request: Request,
) -> tuple[str | None, dict[str, Any]]:
    session_factory = _session_factory_from_request(request)
    if session_factory is None:
        return (
            "agent_health_evaluator_store_not_configured",
            {"status": "store_not_configured"},
        )
    with session_factory() as session:
        freshness = evaluator_freshness(session)
    if freshness["status"] == "fresh":
        return None, freshness
    return f"agent_health_evaluator_{freshness['status']}", freshness


@router.get("/api/v1/health", tags=["api-health"])
def api_health(settings: SettingsDependency) -> dict[str, object]:
    return success_payload(
        {"status": "ok", "service": settings.app_name},
        meta={"correlation_id": get_correlation_id()},
    )


@router.get(
    "/api/v1/external-client/authentication/probe",
    tags=["external-client"],
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def external_client_probe(
    principal: ExternalClientDependency,
) -> dict[str, object]:
    return success_payload(
        {
            "status": "authenticated",
            "external_client_id": principal.external_client_id,
        },
        meta={"correlation_id": get_correlation_id()},
    )
