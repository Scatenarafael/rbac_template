import asyncio
from typing import cast
from uuid import uuid4

from sqlalchemy import column, select, table
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.pagination import DEFAULT_PER_PAGE, paginate_query
from src.modules.auth.application.usecases.TenantUseCase import ListTenantsUseCase
from src.modules.auth.application.usecases.UserUseCase import ListUserUseCase
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestStatus
from src.modules.auth.domain.entities.User import User
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.infrastructure.models.LinkUserTenantRequest import LinkUserTenantRequestModel
from src.modules.auth.infrastructure.queries.LinkUserTenantRequests import LinkUserTenantRequestsQuery
from src.modules.auth.presentation.routers.tenant_router import list_tenants


class FakeScalarResult:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


class FakeResult:
    def __init__(self, items):
        self.items = items

    def scalars(self):
        return FakeScalarResult(self.items)


class FakeSession:
    def __init__(self, items):
        self.items = items
        self.execute_calls = []
        self.scalar_calls = []

    async def execute(self, stmt):
        self.execute_calls.append(stmt)
        return FakeResult(self.items)

    async def scalar(self, stmt):
        self.scalar_calls.append(stmt)
        return None


class FakeUsersQuery:
    def __init__(self, result):
        self.result = result
        self.calls = []

    async def list(self, page=None, per_page=DEFAULT_PER_PAGE):
        self.calls.append((page, per_page))
        return self.result


class FakeListTenantsUseCase:
    def __init__(self):
        self.calls = []

    async def execute(self, page=None, per_page=DEFAULT_PER_PAGE):
        self.calls.append((page, per_page))
        return {"page": page, "per_page": per_page}


def make_user(email: str) -> User:
    return User(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email=Email(email),
        hashed_password="hashed-password",
    )


def test_paginate_query_without_page_returns_raw_list():
    items = [1, 2]
    session = FakeSession(items=items)
    stmt = select(table("items", column("id")))

    result = asyncio.run(paginate_query(cast(AsyncSession, session), stmt, lambda item: item * 2))

    assert result == [2, 4]
    assert len(session.execute_calls) == 1
    assert session.scalar_calls == []


def test_paginate_query_with_page_returns_meta_and_results():
    items = [1, 2]
    session = FakeSession(items=items)
    stmt = select(table("items", column("id")))

    result = asyncio.run(paginate_query(cast(AsyncSession, session), stmt, lambda item: item * 2, page=2))

    assert result == {
        "meta": {
            "perPage": DEFAULT_PER_PAGE,
            "pageIndex": 2,
        },
        "results": [2, 4],
    }
    assert session.scalar_calls == []
    assert len(session.execute_calls) == 1


def test_paginate_query_with_custom_per_page_returns_meta_and_results():
    items = [1, 2]
    session = FakeSession(items=items)
    stmt = select(table("items", column("id")))

    result = asyncio.run(paginate_query(cast(AsyncSession, session), stmt, lambda item: item * 2, page=2, per_page=5))

    assert result == {
        "meta": {
            "perPage": 5,
            "pageIndex": 2,
        },
        "results": [2, 4],
    }
    assert session.scalar_calls == []
    assert len(session.execute_calls) == 1


def test_list_user_usecase_passes_page_to_query_when_received():
    users = [make_user("john@email.com")]
    users_query = FakeUsersQuery(result=users)
    usecase = ListUserUseCase(cast(IUsersQuery, users_query))

    result = asyncio.run(usecase.execute(page=3, per_page=10))

    assert result == users
    assert users_query.calls == [(3, 10)]


def test_list_tenants_router_passes_page_to_usecase_when_received():
    usecase = FakeListTenantsUseCase()

    result = asyncio.run(list_tenants(page=2, per_page=15, usecase=cast(ListTenantsUseCase, usecase)))

    assert result == {"page": 2, "per_page": 15}
    assert usecase.calls == [(2, 15)]


def test_find_pending_by_tenant_and_user_returns_paginated_result_when_page_is_received():
    tenant_id = uuid4()
    user_id = uuid4()
    model = LinkUserTenantRequestModel(
        id=uuid4(),
        fk_tenant_id=tenant_id,
        fk_user_id=user_id,
        status=LinkUserTenantRequestStatus.PENDING,
    )
    session = FakeSession(items=[model])
    query = LinkUserTenantRequestsQuery(cast(AsyncSession, session))

    result = asyncio.run(query.find_pending_by_tenant_and_user(tenant_id, user_id, page=1))

    assert isinstance(result, dict)
    assert result["meta"] == {
        "perPage": DEFAULT_PER_PAGE,
        "pageIndex": 1,
    }
    assert len(result["results"]) == 1
    assert result["results"][0].id == model.id
    assert result["results"][0].fk_tenant_id == tenant_id
    assert result["results"][0].fk_user_id == user_id
    assert result["results"][0].status == LinkUserTenantRequestStatus.PENDING
    assert len(session.execute_calls) == 1
    assert session.scalar_calls == []
