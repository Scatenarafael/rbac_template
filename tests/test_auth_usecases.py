import asyncio
import uuid

import pytest
from fastapi import Response

from src.modules.auth.application.usecases.AuthUseCase import RefreshTokenUseCase
from src.modules.auth.domain.exceptions import RefreshInvalid, RefreshNotFound
from src.modules.auth.infrastructure.services.HandleTokenService import HandleTokenService


class FakeHandleTokenService:
    def __init__(self) -> None:
        self.rotate_calls: list[tuple[str, str]] = []

    async def rotate_refresh(self, raw_refresh: str, jti: str) -> dict[str, str]:
        self.rotate_calls.append((raw_refresh, jti))
        return {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token",
            "refresh_jti": str(uuid.uuid4()),
        }

    @staticmethod
    def set_access_cookie(response: Response, access_token: str) -> None:
        response.set_cookie(key="access_token", value=access_token)

    @staticmethod
    def set_refresh_cookie(response: Response, jti: str, raw_refresh: str) -> None:
        response.set_cookie(key="refresh_token", value=f"{jti}:{raw_refresh}")


class FakeRefreshTokensQuery:
    def __init__(self) -> None:
        self.get_by_id_calls: list[object] = []

    async def get_by_id(self, id):
        self.get_by_id_calls.append(id)
        return None


def test_refresh_usecase_passes_raw_token_and_jti_in_correct_order():
    service = FakeHandleTokenService()
    usecase = RefreshTokenUseCase(handle_token_service=service)
    response = Response()
    refresh_jti = str(uuid.uuid4())
    request = type("RequestStub", (), {"cookies": {"refresh_token": f"{refresh_jti}:opaque-refresh-token"}})()

    result = asyncio.run(usecase.execute(request=request, response=response))

    assert service.rotate_calls == [("opaque-refresh-token", refresh_jti)]
    assert result == {"access_token": "new-access-token"}


def test_refresh_usecase_rejects_malformed_refresh_cookie():
    service = FakeHandleTokenService()
    usecase = RefreshTokenUseCase(handle_token_service=service)
    response = Response()
    request = type("RequestStub", (), {"cookies": {"refresh_token": "malformed-cookie"}})()

    with pytest.raises(RefreshInvalid, match="Formato do cookie de refresh invalido"):
        asyncio.run(usecase.execute(request=request, response=response))


def test_refresh_usecase_requires_refresh_cookie():
    service = FakeHandleTokenService()
    usecase = RefreshTokenUseCase(handle_token_service=service)
    response = Response()
    request = type("RequestStub", (), {"cookies": {}})()

    with pytest.raises(RefreshNotFound, match="Refresh token not found"):
        asyncio.run(usecase.execute(request=request, response=response))


def test_handle_token_service_rejects_invalid_jti_before_repository_lookup():
    repository = object()
    refresh_tokens_query = FakeRefreshTokensQuery()
    service = HandleTokenService(refresh_token_repository=repository, refresh_tokens_query=refresh_tokens_query)

    with pytest.raises(RefreshInvalid, match="Identificador do refresh invalido"):
        asyncio.run(service.rotate_refresh("opaque-refresh-token", "not-a-uuid"))

    assert refresh_tokens_query.get_by_id_calls == []
