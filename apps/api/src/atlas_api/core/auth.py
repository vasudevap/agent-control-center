from __future__ import annotations

import hmac
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, Request

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError


@dataclass(frozen=True)
class ExternalClientPrincipal:
    external_client_id: str
    channel: str = "external_product_client"


def get_settings_from_request(request: Request) -> Settings:
    return request.app.state.settings


async def verify_external_client(
    settings: Annotated[Settings, Depends(get_settings_from_request)],
    external_client_id: Annotated[str | None, Header(alias="X-Atlas-Client-Id")] = None,
    external_client_secret: Annotated[
        str | None,
        Header(alias="X-Atlas-Client-Secret"),
    ] = None,
) -> ExternalClientPrincipal:
    if not settings.external_client_secret:
        raise ApiError(
            status_code=503,
            code="external_client_authentication_not_configured",
            message="External client authentication is not configured.",
        )

    if not external_client_id or not external_client_secret:
        raise ApiError(
            status_code=401,
            code="external_client_credentials_required",
            message="External client credentials are required.",
        )

    if not hmac.compare_digest(
        external_client_secret,
        settings.external_client_secret.get_secret_value(),
    ):
        raise ApiError(
            status_code=401,
            code="external_client_credentials_invalid",
            message="External client credentials are invalid.",
        )

    return ExternalClientPrincipal(external_client_id=external_client_id)
