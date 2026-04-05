from __future__ import annotations

import asyncio
import logging

from fastapi import HTTPException
from fastapi.testclient import TestClient

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


def auth_cookies() -> dict[str, str]:
    access_token = asyncio.run(HandleTokenService(refresh_token_repository=None).create_access_token("11111111-1111-1111-1111-111111111111"))
    return {"access_token": access_token}


def test_request_id_is_returned_on_success():
    client = TestClient(build_app())

    response = client.get("/health", headers={"X-Request-ID": "req-123"}, cookies=auth_cookies())

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"


def test_unhandled_errors_return_debuggable_payload():
    client = TestClient(build_app(), raise_server_exceptions=False)

    response = client.get("/boom", headers={"X-Request-ID": "req-500"}, cookies=auth_cookies())

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "req-500"
    assert response.json()["error"]["code"] == "internal_server_error"
    assert response.json()["error"]["request_id"] == "req-500"


def test_domain_errors_are_translated_to_client_response():
    client = TestClient(build_app())

    response = client.get("/domain", headers={"X-Request-ID": "req-domain"}, cookies=auth_cookies())

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "domain_error"
    assert response.json()["error"]["request_id"] == "req-domain"


def test_auth_errors_are_translated_with_specific_status_and_code():
    client = TestClient(build_app())

    response = client.get("/auth-error", headers={"X-Request-ID": "req-auth"}, cookies=auth_cookies())

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"
    assert response.json()["error"]["request_id"] == "req-auth"


def test_request_logs_include_status_code(caplog):
    caplog.set_level(logging.INFO)
    client = TestClient(build_app())

    response = client.get("/http", headers={"X-Request-ID": "req-log"}, cookies=auth_cookies())

    assert response.status_code == 404
    assert any(
        record.getMessage() == "HTTP request completed"
        and getattr(record, "extra_fields", {}).get("status_code") == 404
        for record in caplog.records
    )
