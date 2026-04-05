import asyncio
import json
from types import SimpleNamespace

from fastapi.responses import PlainTextResponse

from src.modules.auth.presentation.middlewares.auth_middleware import AuthMiddleware


class RequestStub:
    def __init__(self, path: str, cookies: dict[str, str] | None = None, request_id: str = "req-123") -> None:
        self.url = SimpleNamespace(path=path)
        self.cookies = cookies or {}
        self.state = SimpleNamespace(request_id=request_id)


def parse_response_body(response) -> dict:
    return json.loads(response.body.decode())


def test_auth_middleware_allows_public_paths_without_access_token():
    middleware = AuthMiddleware(app=lambda scope, receive, send: None)
    request = RequestStub("/auth/sign-in")
    observed = []

    async def call_next(request):
        observed.append(request.url.path)
        return PlainTextResponse("ok", status_code=200)

    response = asyncio.run(middleware.dispatch(request, call_next))

    assert response.status_code == 200
    assert observed == ["/auth/sign-in"]


def test_auth_middleware_rejects_missing_access_token_cookie():
    middleware = AuthMiddleware(app=lambda scope, receive, send: None)
    request = RequestStub("/tenants", request_id="req-missing-cookie")

    async def call_next(_request):
        raise AssertionError("call_next should not be reached when access token is missing")

    response = asyncio.run(middleware.dispatch(request, call_next))
    payload = parse_response_body(response)

    assert response.status_code == 401
    assert response.headers["X-Request-ID"] == "req-missing-cookie"
    assert payload["error"]["code"] == "invalid_credentials"
    assert payload["error"]["message"] == "Access token not found"


def test_auth_middleware_rejects_invalid_or_expired_access_token(monkeypatch):
    middleware = AuthMiddleware(app=lambda scope, receive, send: None)
    request = RequestStub("/tenants", cookies={"access_token": "invalid-token"}, request_id="req-invalid-token")

    async def fake_verify_access_token(_token: str):
        return None

    async def call_next(_request):
        raise AssertionError("call_next should not be reached when token is invalid")

    monkeypatch.setattr(
        "src.modules.auth.presentation.middlewares.auth_middleware.HandleTokenService.verify_access_token",
        staticmethod(fake_verify_access_token),
    )

    response = asyncio.run(middleware.dispatch(request, call_next))
    payload = parse_response_body(response)

    assert response.status_code == 401
    assert response.headers["X-Request-ID"] == "req-invalid-token"
    assert payload["error"]["message"] == "Access token invalid or expired"


def test_auth_middleware_sets_authenticated_user_id_before_calling_next(monkeypatch):
    middleware = AuthMiddleware(app=lambda scope, receive, send: None)
    request = RequestStub("/tenants", cookies={"access_token": "valid-token"})
    observed_user_ids = []

    async def fake_verify_access_token(_token: str):
        return {"sub": "user-123"}

    async def call_next(request):
        observed_user_ids.append(request.state.user_id)
        return PlainTextResponse("ok", status_code=200)

    monkeypatch.setattr(
        "src.modules.auth.presentation.middlewares.auth_middleware.HandleTokenService.verify_access_token",
        staticmethod(fake_verify_access_token),
    )

    response = asyncio.run(middleware.dispatch(request, call_next))

    assert response.status_code == 200
    assert request.state.user_id == "user-123"
    assert observed_user_ids == ["user-123"]
