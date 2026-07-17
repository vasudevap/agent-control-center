from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from atlas_api.core.correlation import get_correlation_id


@dataclass(frozen=True)
class ApiError(Exception):
    status_code: int
    code: str
    message: str


def error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {
        "error": {
            "code": code,
            "message": message,
            "correlation_id": get_correlation_id(),
        },
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(
        _request: Request,
        exc: ApiError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc.code, exc.message),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload("http_error", str(exc.detail)),
        )
