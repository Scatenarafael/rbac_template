# pyright: reportArgumentType=false
import asyncio
from typing import Any, cast
from uuid import uuid4

from fastapi import Response

from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase, SignInUseCase, SignOutUseCase
from src.modules.auth.domain.entities.Role import Role
from src.modules.auth.domain.entities.Tenant import Tenant
from src.modules.auth.domain.entities.User import User, UserWithTenantRoles
from src.modules.auth.domain.entities.UserTenantRole import UserTenantRoleDetailed
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.presentation.factories.UseCaseFactory import AuthUseCaseFactory
from src.modules.auth.presentation.routers.auth_router import (
    refresh_token,
    sign_in,
    sign_out,
)
from src.modules.auth.presentation.schemas.pydantic.auth_schema import MeResponseBody, SignInRequestPayload


class FakeUsersQuery:
    def __init__(self, user: User) -> None:
        self.user = user
        self.find_by_email_calls = []

    async def find_by_email(self, email: str) -> User:
        self.find_by_email_calls.append(email)
        return self.user


class FakeHashPasswordService:
    def __init__(self, is_valid: bool = True) -> None:
        self.is_valid = is_valid
        self.verify_calls = []

    def verify_password(self, password: str, hashed_password: str) -> bool:
        self.verify_calls.append((password, hashed_password))
        return self.is_valid


class FakeHandleTokenService:
    def __init__(self, payload=None) -> None:
        self.payload = payload
        self.access_cookie_calls = []
        self.refresh_cookie_calls = []
        self.clear_cookie_calls = []
        self.create_access_token_calls = []
        self.create_refresh_token_calls = []
        self.verify_calls = []

    async def create_access_token(self, user_id: str) -> str:
        self.create_access_token_calls.append(user_id)
        return "access-token"

    async def create_refresh_token(self, user_id: str) -> dict[str, str]:
        self.create_refresh_token_calls.append(user_id)
        return {
            "refresh_token": "refresh-token",
            "refresh_jti": str(uuid4()),
            "user_id": user_id,
        }

    def set_access_cookie(self, response: Response, access_token: str) -> None:
        self.access_cookie_calls.append((response, access_token))

    def set_refresh_cookie(self, response: Response, jti: str, raw_refresh: str) -> None:
        self.refresh_cookie_calls.append((response, jti, raw_refresh))

    def clear_cookies(self, response: Response) -> None:
        self.clear_cookie_calls.append(response)

    async def verify_access_token(self, token: str):
        self.verify_calls.append(token)
        return self.payload


def make_user() -> User:
    return User(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email=Email("john.doe@email.com"),
        hashed_password="hashed-password",
    )


def test_sign_in_usecase_returns_tokens_and_sets_cookies():
    user = make_user()
    users_query = FakeUsersQuery(user)
    hash_password_service = FakeHashPasswordService()
    handle_token_service = FakeHandleTokenService()
    usecase = SignInUseCase(users_query, hash_password_service, handle_token_service)
    response = Response()
    payload = SignInRequestPayload(email="john.doe@email.com", password="secret123")

    result = asyncio.run(usecase.execute(payload=payload, response=response))

    assert users_query.find_by_email_calls == ["john.doe@email.com"]
    assert hash_password_service.verify_calls == [("secret123", "hashed-password")]
    assert handle_token_service.create_access_token_calls == [str(user.id)]
    assert handle_token_service.create_refresh_token_calls == [str(user.id)]
    assert handle_token_service.access_cookie_calls == [(response, "access-token")]
    assert handle_token_service.refresh_cookie_calls[0][0] is response
    assert handle_token_service.refresh_cookie_calls[0][2] == "refresh-token"
    assert result["access_token"] == "access-token"
    assert result["user_id"] == str(user.id)


def test_sign_out_usecase_clears_response_cookies():
    handle_token_service = FakeHandleTokenService()
    usecase = SignOutUseCase(handle_token_service)
    response = Response()

    asyncio.run(usecase.execute(response))

    assert handle_token_service.clear_cookie_calls == [response]


def test_get_logged_user_id_usecase_returns_subject_when_token_is_valid():
    usecase = GetLoggedUserIdUseCase(FakeHandleTokenService(payload={"sub": "user-123"}))

    result = asyncio.run(usecase.execute("valid-token"))

    assert result == "user-123"


def test_get_logged_user_id_usecase_returns_none_when_token_is_invalid():
    usecase = GetLoggedUserIdUseCase(FakeHandleTokenService(payload=None))

    result = asyncio.run(usecase.execute("invalid-token"))

    assert result is None


def test_auth_router_dependency_factories_inject_same_session_into_queries_and_repositories():
    session = object()

    factory = AuthUseCaseFactory(session)
    sign_in_usecase = factory.build_sign_in_usecase()
    refresh_usecase = factory.build_refresh_token_usecase()
    sign_out_usecase = factory.build_sign_out_usecase()
    sign_in_token_service = cast(Any, sign_in_usecase.handle_token_service)
    refresh_token_service = cast(Any, refresh_usecase.handle_token_service)
    sign_out_token_service = cast(Any, sign_out_usecase.handle_token_service)

    assert sign_in_usecase.users_query._session is session
    assert sign_in_token_service.refresh_token_repository._session is session
    assert sign_in_token_service.refresh_tokens_query._session is session
    assert refresh_token_service.refresh_token_repository._session is session
    assert refresh_token_service.refresh_tokens_query._session is session
    assert sign_out_token_service.refresh_token_repository._session is session
    assert sign_out_token_service.refresh_tokens_query._session is session


def test_sign_in_router_delegates_to_usecase():
    payload = SignInRequestPayload(email="john.doe@email.com", password="secret123")
    response = Response()

    class FakeSignInUseCase:
        def __init__(self) -> None:
            self.calls = []

        async def execute(self, payload, response):
            self.calls.append((payload, response))
            return {"access_token": "token"}

    usecase = FakeSignInUseCase()

    result = asyncio.run(sign_in(response=response, payload=payload, sign_in_usecase=usecase))

    assert result == {"access_token": "token"}
    assert usecase.calls == [(payload, response)]


def test_refresh_token_router_delegates_request_and_response_to_usecase():
    request = type("RequestStub", (), {"cookies": {"refresh_token": "cookie"}})()
    response = Response()

    class FakeRefreshTokenUseCase:
        def __init__(self) -> None:
            self.calls = []

        async def execute(self, request, response):
            self.calls.append((request, response))
            return {"access_token": "token"}

    usecase = FakeRefreshTokenUseCase()

    result = asyncio.run(refresh_token(request=request, response=response, refresh_token_usecase=usecase))

    assert result == {"access_token": "token"}
    assert usecase.calls == [(request, response)]


def test_sign_out_router_awaits_usecase_execution():
    response = Response()

    class FakeSignOutUseCase:
        def __init__(self) -> None:
            self.calls = []

        async def execute(self, response):
            self.calls.append(response)

    usecase = FakeSignOutUseCase()

    result = asyncio.run(sign_out(response=response, sign_out_usecase=usecase))

    assert result is None
    assert usecase.calls == [response]


def test_me_response_body_exposes_only_id_and_name_for_tenant_and_role():
    me_response = UserWithTenantRoles(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email="john.doe@email.com",
        user_tenant_roles=[
            UserTenantRoleDetailed(
                id=uuid4(),
                fk_user_tenant_id=uuid4(),
                fk_role_id=uuid4(),
                tenant=Tenant(id=uuid4(), name="Acme"),
                role=Role(id=uuid4(), name="tenantadmin", description="Tenant admin"),
            )
        ],
    )

    response = MeResponseBody.model_validate(me_response)
    tenant = me_response.user_tenant_roles[0].tenant
    assert tenant is not None

    assert response.model_dump() == {
        "id": me_response.id,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com",
        "user_tenant_roles": [
            {
                "id": me_response.user_tenant_roles[0].id,
                "tenant": {
                    "id": tenant.id,
                    "name": "Acme",
                },
                "role": {
                    "id": me_response.user_tenant_roles[0].role.id,
                    "name": "tenantadmin",
                },
            }
        ],
    }
