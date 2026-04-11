# pyright: reportArgumentType=false
import asyncio
from uuid import UUID, uuid4

import pytest

from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.presentation.routers.link_user_tenant_request_router import (
    approve_user_tenant_request,
    invite_user_to_tenant,
    list_link_user_tenant_requests_by_tenant_id,
    reject_user_tenant_request,
    request_tenant_entry,
)


class RequestStub:
    def __init__(self, cookies: dict[str, str]):
        self.cookies = cookies


class FakeLoggedUserIdUseCase:
    def __init__(self, user_id: str | None) -> None:
        self.user_id = user_id
        self.calls = []

    async def execute(self, access_token: str) -> str | None:
        self.calls.append(access_token)
        return self.user_id


class FakeUseCase:
    def __init__(self) -> None:
        self.calls = []

    async def execute(self, *args):
        self.calls.append(args)
        return {"args": [str(arg) for arg in args]}


def test_list_link_user_tenant_requests_forwards_tenant_and_authenticated_user():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    request = RequestStub({"access_token": "valid-token"})
    usecase = FakeUseCase()
    get_user_id_usecase = FakeLoggedUserIdUseCase(str(authenticated_user_id))

    result = asyncio.run(
        list_link_user_tenant_requests_by_tenant_id(
            request=request,
            tenant_id=tenant_id,
            usecase=usecase,
            get_user_id_usecase=get_user_id_usecase,
        )
    )

    assert get_user_id_usecase.calls == ["valid-token"]
    assert usecase.calls == [(tenant_id, authenticated_user_id)]
    assert result == {"args": [str(tenant_id), str(authenticated_user_id)]}


def test_invite_user_to_tenant_forwards_tenant_actor_and_requested_user():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    requested_user_id = uuid4()
    usecase = FakeUseCase()

    asyncio.run(
        invite_user_to_tenant(
            request=RequestStub({"access_token": "valid-token"}),
            tenant_id=tenant_id,
            requested_user_id=requested_user_id,
            usecase=usecase,
            get_user_id_usecase=FakeLoggedUserIdUseCase(str(authenticated_user_id)),
        )
    )

    assert usecase.calls == [(tenant_id, authenticated_user_id, requested_user_id)]


def test_request_tenant_entry_forwards_tenant_and_authenticated_user():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    usecase = FakeUseCase()

    asyncio.run(
        request_tenant_entry(
            request=RequestStub({"access_token": "valid-token"}),
            tenant_id=tenant_id,
            usecase=usecase,
            get_user_id_usecase=FakeLoggedUserIdUseCase(str(authenticated_user_id)),
        )
    )

    assert usecase.calls == [(tenant_id, authenticated_user_id)]


def test_approve_user_tenant_request_forwards_request_and_authenticated_user():
    link_request_id = uuid4()
    authenticated_user_id = uuid4()
    usecase = FakeUseCase()

    asyncio.run(
        approve_user_tenant_request(
            request=RequestStub({"access_token": "valid-token"}),
            link_user_tenant_request_id=link_request_id,
            usecase=usecase,
            get_user_id_usecase=FakeLoggedUserIdUseCase(str(authenticated_user_id)),
        )
    )

    assert usecase.calls == [(link_request_id, authenticated_user_id)]


def test_reject_user_tenant_request_forwards_request_and_authenticated_user():
    link_request_id = uuid4()
    authenticated_user_id = uuid4()
    usecase = FakeUseCase()

    asyncio.run(
        reject_user_tenant_request(
            request=RequestStub({"access_token": "valid-token"}),
            link_user_tenant_request_id=link_request_id,
            usecase=usecase,
            get_user_id_usecase=FakeLoggedUserIdUseCase(str(authenticated_user_id)),
        )
    )

    assert usecase.calls == [(link_request_id, authenticated_user_id)]


def test_link_user_tenant_request_router_requires_access_token_cookie():
    with pytest.raises(InvalidCredentials, match="Access token not found"):
        asyncio.run(
            request_tenant_entry(
                request=RequestStub({}),
                tenant_id=uuid4(),
                usecase=FakeUseCase(),
                get_user_id_usecase=FakeLoggedUserIdUseCase(str(uuid4())),
            )
        )


def test_link_user_tenant_request_router_rejects_invalid_or_expired_access_token():
    with pytest.raises(InvalidCredentials, match="Access token invalid or expired"):
        asyncio.run(
            request_tenant_entry(
                request=RequestStub({"access_token": "expired-token"}),
                tenant_id=uuid4(),
                usecase=FakeUseCase(),
                get_user_id_usecase=FakeLoggedUserIdUseCase(None),
            )
        )


def test_link_user_tenant_request_router_rejects_invalid_authenticated_user_identifier():
    with pytest.raises(InvalidCredentials, match="Authenticated user identifier is invalid"):
        asyncio.run(
            request_tenant_entry(
                request=RequestStub({"access_token": "valid-token"}),
                tenant_id=uuid4(),
                usecase=FakeUseCase(),
                get_user_id_usecase=FakeLoggedUserIdUseCase("not-a-uuid"),
            )
        )


def test_link_user_tenant_request_router_converts_authenticated_user_to_uuid():
    authenticated_user_id = uuid4()
    usecase = FakeUseCase()

    asyncio.run(
        request_tenant_entry(
            request=RequestStub({"access_token": "valid-token"}),
            tenant_id=uuid4(),
            usecase=usecase,
            get_user_id_usecase=FakeLoggedUserIdUseCase(str(authenticated_user_id)),
        )
    )

    assert isinstance(usecase.calls[0][1], UUID)
