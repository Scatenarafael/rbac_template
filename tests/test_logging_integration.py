from __future__ import annotations

import asyncio
import logging

from fastapi import HTTPException
import httpx

from src.core.http.app_factory import create_app
from src.modules.auth.domain.exceptions import DomainError, InvalidCredentials
from src.modules.auth.infrastructure.services.HandleTokenService import HandleTokenService


def build_app():
    app = create_app()

    @app.get("/health")
    async def health():
        return {"ok": True}

    @app.get("/boom")
    async def boom():
        raise ValueError("exploded")

    @app.get("/domain")
    async def domain():
        raise DomainError("invalid tenant context")

    @app.get("/auth-error")
    async def auth_error():
        raise InvalidCredentials("bad credentials")

    @app.get("/http")
    async def http():
        raise HTTPException(status_code=404, detail="not found")

    return app


async def auth_cookies() -> dict[str, str]:
    access_token = await HandleTokenService(refresh_token_repository=None).create_access_token("11111111-1111-1111-1111-111111111111")
    return {"access_token": access_token}


def perform_request(
    path: str,
    *,
    raise_app_exceptions: bool = True,
    headers: dict[str, str] | None = None,
    authenticated: bool = True,
):
    async def run():
        transport = httpx.ASGITransport(app=build_app(), raise_app_exceptions=raise_app_exceptions)
        cookies = await auth_cookies() if authenticated else {}
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver", cookies=cookies) as client:
            return await client.get(path, headers=headers)

    return asyncio.run(run())


def test_request_id_is_returned_on_success():
    response = perform_request("/health", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"


def test_request_id_is_returned_on_auth_middleware_error():
    response = perform_request("/health", headers={"X-Request-ID": "req-auth-middleware"}, authenticated=False)

    assert response.status_code == 401
    assert response.headers["X-Request-ID"] == "req-auth-middleware"
    assert response.json()["error"]["request_id"] == "req-auth-middleware"


def test_unhandled_errors_return_debuggable_payload():
    response = perform_request("/boom", raise_app_exceptions=False, headers={"X-Request-ID": "req-500"})

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "req-500"
    assert response.json()["error"]["code"] == "internal_server_error"
    assert response.json()["error"]["request_id"] == "req-500"


def test_domain_errors_are_translated_to_client_response():
    response = perform_request("/domain", headers={"X-Request-ID": "req-domain"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "domain_error"
    assert response.json()["error"]["request_id"] == "req-domain"


def test_auth_errors_are_translated_with_specific_status_and_code():
    response = perform_request("/auth-error", headers={"X-Request-ID": "req-auth"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"
    assert response.json()["error"]["request_id"] == "req-auth"


def test_request_logs_include_status_code(caplog):
    caplog.set_level(logging.INFO)
    response = perform_request("/http", headers={"X-Request-ID": "req-log"})

    assert response.status_code == 404
    assert any(
        record.getMessage() == "HTTP request completed"
        and getattr(record, "extra_fields", {}).get("status_code") == 404
        for record in caplog.records
    )


def test_request_logs_include_authenticated_user_id(caplog):
    caplog.set_level(logging.INFO)
    response = perform_request("/health", headers={"X-Request-ID": "req-user-log"})

    assert response.status_code == 200
    assert any(
        record.getMessage() == "HTTP request completed"
        and getattr(record, "extra_fields", {}).get("user_id") == "11111111-1111-1111-1111-111111111111"
        for record in caplog.records
    )
