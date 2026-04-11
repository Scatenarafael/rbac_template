# pyright: reportArgumentType=false
import asyncio

import pytest

from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.presentation.routers.tenant_router import create_tenant
from src.modules.auth.presentation.schemas.pydantic.tenant_schema import TenantCreationPayloadSchema


class RequestStub:
    def __init__(self, cookies: dict[str, str]):
        self.cookies = cookies


class FakeCreateTenantUseCase:
    async def execute(self, payload, user_id):
        return {"name": payload.name, "user_id": str(user_id)}


class FakeLoggedUserIdUseCase:
    def __init__(self, user_id: str | None) -> None:
        self.user_id = user_id

    async def execute(self, access_token: str) -> str | None:
        return self.user_id


def test_create_tenant_requires_access_token_cookie():
    request = RequestStub(cookies={})
    payload = TenantCreationPayloadSchema(name="Acme")

    with pytest.raises(InvalidCredentials, match="Access token not found"):
        asyncio.run(
            create_tenant(
                request=request,
                payload=payload,
                usecase=FakeCreateTenantUseCase(),
                get_user_id_usecase=FakeLoggedUserIdUseCase(user_id="123"),
            )
        )


def test_create_tenant_rejects_invalid_authenticated_user_identifier():
    request = RequestStub(cookies={"access_token": "valid-token"})
    payload = TenantCreationPayloadSchema(name="Acme")

    with pytest.raises(InvalidCredentials, match="Authenticated user identifier is invalid"):
        asyncio.run(
            create_tenant(
                request=request,
                payload=payload,
                usecase=FakeCreateTenantUseCase(),
                get_user_id_usecase=FakeLoggedUserIdUseCase(user_id="not-a-uuid"),
            )
        )
