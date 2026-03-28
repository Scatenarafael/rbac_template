from __future__ import annotations

import logging

from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.core.http.app_factory import create_app
from src.modules.auth.domain.exceptions import DomainError


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

    @app.get("/http")
    async def http():
        raise HTTPException(status_code=404, detail="not found")

    return app


def test_request_id_is_returned_on_success():
    client = TestClient(build_app())

    response = client.get("/health", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"


def test_unhandled_errors_return_debuggable_payload():
    client = TestClient(build_app(), raise_server_exceptions=False)

    response = client.get("/boom", headers={"X-Request-ID": "req-500"})

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "req-500"
    assert response.json()["error"]["code"] == "internal_server_error"
    assert response.json()["error"]["request_id"] == "req-500"


def test_domain_errors_are_translated_to_client_response():
    client = TestClient(build_app())

    response = client.get("/domain", headers={"X-Request-ID": "req-domain"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "domain_error"
    assert response.json()["error"]["request_id"] == "req-domain"


def test_request_logs_include_status_code(caplog):
    caplog.set_level(logging.INFO)
    client = TestClient(build_app())

    response = client.get("/http", headers={"X-Request-ID": "req-log"})

    assert response.status_code == 404
    assert any(
        record.getMessage() == "HTTP request completed"
        and getattr(record, "extra_fields", {}).get("status_code") == 404
        for record in caplog.records
    )
