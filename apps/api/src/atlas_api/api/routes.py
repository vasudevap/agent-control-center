from __future__ import annotations

from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request

from atlas_api.core.auth import ExternalClientPrincipal, verify_external_client
from atlas_api.core.config import Settings
from atlas_api.core.contracts import success_payload
from atlas_api.core.correlation import get_correlation_id
from atlas_api.core.errors import ApiError

router = APIRouter()


def get_request_settings(request: Request) -> Settings:
    return cast("Settings", request.app.state.settings)


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
def ready(settings: SettingsDependency) -> dict[str, object]:
    problems = settings.readiness_problems()
    return {
        "status": "ready" if not problems else "not_ready",
        "service": settings.app_name,
        "checks": {
            "configuration": "ok" if not problems else "failed",
        },
        "problems": problems,
    }


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


@router.get("/api/v1/knowledge/facts", tags=["knowledge"])
def knowledge_facts_placeholder() -> None:
    raise ApiError(
        status_code=501,
        code="knowledge_contract_not_implemented",
        message="Knowledge fact APIs require a later approved Phase 5 work order.",
    )
