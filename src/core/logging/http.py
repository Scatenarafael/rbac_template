from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.core.config.config import get_settings
from src.core.logging.context import (
    bind_request_id,
    bind_user_id,
    get_request_id,
    reset_request_id,
    reset_user_id,
)
from src.core.logging.logger import get_logger
from src.modules.auth.domain.exceptions import DomainError

http_logger = get_logger("src.core.http")


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = headers.get("x-request-id") or str(uuid4())
        request_token = bind_request_id(request_id)
        user_token = bind_user_id(None)
        start_time = perf_counter()
        status_code = 500

        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]
                mutable_headers = MutableHeaders(scope=message)
                mutable_headers["X-Request-ID"] = request_id

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round((perf_counter() - start_time) * 1000, 2)
            http_logger.info(
                "HTTP request completed",
                method=scope.get("method"),
                path=scope.get("path"),
                route=getattr(scope.get("route"), "path", None),
                query_string=scope.get("query_string", b"").decode("utf-8", errors="replace") or None,
                client_ip=_get_client_ip(scope, headers),
                status_code=status_code,
                duration_ms=duration_ms,
            )
            reset_user_id(user_token)
            reset_request_id(request_token)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(DomainError, domain_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = _resolve_request_id(request)
    level = http_logger.warning if exc.status_code < 500 else http_logger.error
    level(
        "HTTP exception handled",
        request_id=request_id,
        status_code=exc.status_code,
        detail=exc.detail,
    )
    return _error_response(
        status_code=exc.status_code,
        code="http_error",
        message=str(exc.detail),
        request_id=request_id,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = _resolve_request_id(request)
    http_logger.warning(
        "Request validation failed",
        request_id=request_id,
        errors=exc.errors(),
    )
    return _error_response(
        status_code=422,
        code="validation_error",
        message="Request validation failed",
        request_id=request_id,
        debug=exc.errors(),
    )


async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    request_id = _resolve_request_id(request)
    http_logger.warning(
        "Domain rule violated",
        request_id=request_id,
        detail=str(exc),
    )
    return _error_response(
        status_code=400,
        code="domain_error",
        message=str(exc) or "Domain rule violated",
        request_id=request_id,
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    request_id = _resolve_request_id(request)
    http_logger.exception(
        "Database error",
        request_id=request_id,
        error_type=type(exc).__name__,
    )
    return _error_response(
        status_code=500,
        code="database_error",
        message="Database operation failed",
        request_id=request_id,
        debug=str(exc),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _resolve_request_id(request)
    http_logger.exception(
        "Unhandled application exception",
        request_id=request_id,
        error_type=type(exc).__name__,
    )
    return _error_response(
        status_code=500,
        code="internal_server_error",
        message="Internal server error",
        request_id=request_id,
        debug=str(exc),
    )


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    request_id: str | None = None,
    debug: object | None = None,
) -> JSONResponse:
    settings = get_settings()
    request_id = request_id or get_request_id()

    payload: dict[str, object] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }

    if debug is not None and settings.DEBUG:
        payload["error"]["debug"] = debug

    headers = {"X-Request-ID": request_id} if request_id else None
    return JSONResponse(status_code=status_code, content=payload, headers=headers)


def _get_client_ip(scope: Scope, headers: Headers) -> str | None:
    forwarded_for = headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    client = scope.get("client")
    return client[0] if client else None


def _resolve_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None) or get_request_id()
