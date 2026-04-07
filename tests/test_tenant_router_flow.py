import asyncio
from uuid import UUID, uuid4

import pytest

from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.presentation.routers.tenant_router import create_tenant, update_tenant
from src.modules.auth.presentation.schemas.pydantic.tenant_schema import TenantCreationPayloadSchema


class RequestStub:
    def __init__(self, cookies: dict[str, str]):
        self.cookies = cookies


class FakeCreateTenantUseCase:
    def __init__(self) -> None:
        self.calls = []

    async def execute(self, payload, user_id):
        self.calls.append((payload, user_id))
        return {"name": payload.name, "user_id": str(user_id)}


class FakeLoggedUserIdUseCase:
    def __init__(self, user_id: str | None) -> None:
        self.user_id = user_id
        self.calls = []

    async def execute(self, access_token: str) -> str | None:
        self.calls.append(access_token)
        return self.user_id


class FakeUpdateTenantUseCase:
    def __init__(self) -> None:
        self.calls = []

    async def execute(self, tenant_id, payload):
        self.calls.append((tenant_id, payload))
        return {"tenant_id": str(tenant_id), "name": payload.name}


def test_create_tenant_uses_authenticated_user_id_from_access_token():
    request = RequestStub(cookies={"access_token": "valid-token"})
    payload = TenantCreationPayloadSchema(name="Acme")
    usecase = FakeCreateTenantUseCase()
    get_user_id_usecase = FakeLoggedUserIdUseCase(user_id=str(uuid4()))

    result = asyncio.run(
        create_tenant(
            request=request,
            payload=payload,
            usecase=usecase,
            get_user_id_usecase=get_user_id_usecase,
        )
    )

    assert result["name"] == "Acme"
    assert get_user_id_usecase.calls == ["valid-token"]
    assert usecase.calls[0][0] == payload
    assert isinstance(usecase.calls[0][1], UUID)
    assert result["user_id"] == str(usecase.calls[0][1])


def test_create_tenant_rejects_invalid_or_expired_access_token():
    request = RequestStub(cookies={"access_token": "expired-token"})
    payload = TenantCreationPayloadSchema(name="Acme")

    with pytest.raises(InvalidCredentials, match="Access token invalid or expired"):
        asyncio.run(
            create_tenant(
                request=request,
                payload=payload,
                usecase=FakeCreateTenantUseCase(),
                get_user_id_usecase=FakeLoggedUserIdUseCase(user_id=None),
            )
        )


def test_update_tenant_forwards_tenant_id_and_payload_to_update_usecase():
    tenant_id = uuid4()
    payload = TenantCreationPayloadSchema(name="Renamed tenant")
    usecase = FakeUpdateTenantUseCase()

    result = asyncio.run(update_tenant(tenant_id=tenant_id, payload=payload, usecase=usecase))

    assert usecase.calls == [(tenant_id, payload)]
    assert result == {"tenant_id": str(tenant_id), "name": "Renamed tenant"}
