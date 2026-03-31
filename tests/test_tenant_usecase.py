import asyncio
from uuid import uuid4

import pytest

from src.modules.auth.application.usecases.TenantUseCase import CreateTenantUseCase
from src.modules.auth.domain.entities import Role, Tenant, User, UserTenant, UserTenantRole
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.presentation.factories.UseCaseFactory import TenantUseCaseFactory
from src.modules.auth.presentation.schemas.pydantic.tenant_schema import TenantCreationPayloadSchema


class FakeSession:
    def __init__(self) -> None:
        self.commit_calls = 0
        self.rollback_calls = 0

    async def commit(self) -> None:
        self.commit_calls += 1

    async def rollback(self) -> None:
        self.rollback_calls += 1


class FakeTenantRepository:
    def __init__(self) -> None:
        self.created: list[Tenant] = []

    async def create(self, data: Tenant) -> Tenant:
        self.created.append(data)
        return data

    async def find_by_name(self, name: str) -> Tenant | None:
        return None


class FakeUserRepository:
    def __init__(self, user: User | None) -> None:
        self.user = user

    async def get_by_id(self, id):
        return self.user


class FakeRoleRepository:
    def __init__(self, role: Role | None) -> None:
        self.role = role

    async def find_by_name(self, name: str) -> Role | None:
        return self.role


class FakeUserTenantRepository:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.created: list[UserTenant] = []

    async def create(self, data: UserTenant) -> UserTenant:
        if self.should_fail:
            raise RuntimeError("failed to create user tenant")

        self.created.append(data)
        return data


class FakeUserTenantRoleRepository:
    def __init__(self) -> None:
        self.created: list[UserTenantRole] = []

    async def create(self, data: UserTenantRole) -> UserTenantRole:
        self.created.append(data)
        return data


def make_user() -> User:
    return User(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email=Email("john.doe@email.com"),
        hashed_password="hashed-password",
    )


def make_role() -> Role:
    return Role(id=uuid4(), name="tenantadmin", description="Tenant admin")


def test_get_create_tenant_usecase_injects_same_session_everywhere():
    session = object()

    usecase = TenantUseCaseFactory(session).build_create_tenant_usecase()

    assert isinstance(usecase, CreateTenantUseCase)
    assert usecase.session is session
    assert usecase.tenant_repository._session is session
    assert usecase.user_repository._session is session
    assert usecase.role_repository._session is session
    assert usecase.user_tenant_repository._session is session
    assert usecase.user_tenant_role_repository._session is session


def test_create_tenant_usecase_commits_once_after_creating_tenant_relationships():
    session = FakeSession()
    tenant_repository = FakeTenantRepository()
    user_repository = FakeUserRepository(make_user())
    role_repository = FakeRoleRepository(make_role())
    user_tenant_repository = FakeUserTenantRepository()
    user_tenant_role_repository = FakeUserTenantRoleRepository()
    payload = TenantCreationPayloadSchema(name="Acme")
    usecase = CreateTenantUseCase(
        session=session,
        tenant_repository=tenant_repository,
        user_repository=user_repository,
        role_repository=role_repository,
        user_tenant_repository=user_tenant_repository,
        user_tenant_role_repository=user_tenant_role_repository,
    )

    tenant = asyncio.run(usecase.execute(payload, uuid4()))

    assert tenant.name == "Acme"
    assert [created.name for created in tenant_repository.created] == ["Acme"]
    assert len(user_tenant_repository.created) == 1
    assert user_tenant_repository.created[0].fk_tenant_id == tenant.id
    assert len(user_tenant_role_repository.created) == 1
    assert user_tenant_role_repository.created[0].fk_user_tenant_id == user_tenant_repository.created[0].id
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


def test_create_tenant_usecase_rolls_back_when_relationship_creation_fails():
    session = FakeSession()
    usecase = CreateTenantUseCase(
        session=session,
        tenant_repository=FakeTenantRepository(),
        user_repository=FakeUserRepository(make_user()),
        role_repository=FakeRoleRepository(make_role()),
        user_tenant_repository=FakeUserTenantRepository(should_fail=True),
        user_tenant_role_repository=FakeUserTenantRoleRepository(),
    )

    with pytest.raises(RuntimeError, match="failed to create user tenant"):
        asyncio.run(usecase.execute(TenantCreationPayloadSchema(name="Acme"), uuid4()))

    assert session.commit_calls == 0
    assert session.rollback_calls == 1
