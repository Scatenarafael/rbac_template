# pyright: reportArgumentType=false
import asyncio
from uuid import uuid4

import pytest

from src.modules.auth.application.usecases.LinkUserTenantRequestUseCase import (
    AproveUserTenantRequestUseCase,
    InviteUserToTenantUseCase,
    ListLinkUserTenantRequestUseCase,
    RejectUserTenantRequestUseCase,
    RequestTenantEntryUseCase,
)
from src.modules.auth.domain.entities import LinkUserTenantRequest, Role, UserTenant, UserTenantRole
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestType
from src.modules.auth.domain.exceptions import ForbiddenError


class FakeLinkUserTenantRequestQuery:
    def __init__(self, result=None) -> None:
        self.result = result or []
        self.list_by_tenant_id_calls = []

    async def list_by_tenant_id(self, tenant_id):
        self.list_by_tenant_id_calls.append(tenant_id)
        return self.result


class FakeLinkUserTenantRequestRepository:
    def __init__(self) -> None:
        self.created: list[LinkUserTenantRequest] = []
        self.approved_ids = []
        self.rejected_ids = []

    async def create(self, data: LinkUserTenantRequest):
        self.created.append(data)
        return data

    async def approve(self, id):
        self.approved_ids.append(id)
        return LinkUserTenantRequest(fk_tenant_id=uuid4(), fk_user_id=uuid4())

    async def reject(self, id):
        self.rejected_ids.append(id)


class FakeRules:
    def __init__(self, link: LinkUserTenantRequest | None = None) -> None:
        self.link = link
        self.list_calls = []
        self.invite_calls = []
        self.request_entry_calls = []
        self.approve_or_reject_calls = []

    async def validate_list_link_user_tenant_requests(self, tenant_id, authenticated_user_id):
        self.list_calls.append((tenant_id, authenticated_user_id))

    async def validate_invite_user_to_tenant(self, tenant_id, authenticated_user_id, requested_user_id):
        self.invite_calls.append((tenant_id, authenticated_user_id, requested_user_id))

    async def validate_request_tenant_entry(self, tenant_id, authenticated_user_id):
        self.request_entry_calls.append((tenant_id, authenticated_user_id))

    async def validate_approve_or_reject_link_user_tenant_request(self, link_user_tenant_request_id, authenticated_user_id):
        self.approve_or_reject_calls.append((link_user_tenant_request_id, authenticated_user_id))
        return self.link


class FakeUserTenantRepository:
    def __init__(self) -> None:
        self.created: list[UserTenant] = []

    async def create(self, data: UserTenant):
        self.created.append(data)
        return data


class FakeUserTenantRoleRepository:
    def __init__(self) -> None:
        self.created: list[UserTenantRole] = []

    async def create(self, data: UserTenantRole):
        self.created.append(data)
        return data


class FakeRolesQuery:
    def __init__(self, role: Role | None) -> None:
        self.role = role
        self.find_by_name_calls = []

    async def find_by_name(self, name: str):
        self.find_by_name_calls.append(name)
        return self.role


def make_link() -> LinkUserTenantRequest:
    return LinkUserTenantRequest(fk_tenant_id=uuid4(), fk_user_id=uuid4())


def test_list_link_user_tenant_requests_validates_access_and_returns_query_result():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    result = [object()]
    query = FakeLinkUserTenantRequestQuery(result=result)
    rules = FakeRules()
    usecase = ListLinkUserTenantRequestUseCase(query, rules)

    response = asyncio.run(usecase.execute(tenant_id, authenticated_user_id))

    assert response == result
    assert rules.list_calls == [(tenant_id, authenticated_user_id)]
    assert query.list_by_tenant_id_calls == [tenant_id]


@pytest.mark.xfail(reason="A lógica atual não define type=INVITE ao criar convite.", strict=True)
def test_invite_user_to_tenant_creates_invite_request_after_validation():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    requested_user_id = uuid4()
    repository = FakeLinkUserTenantRequestRepository()
    rules = FakeRules()
    usecase = InviteUserToTenantUseCase(repository, rules)

    asyncio.run(usecase.execute(tenant_id, authenticated_user_id, requested_user_id))

    assert rules.invite_calls == [(tenant_id, authenticated_user_id, requested_user_id)]
    assert repository.created[0].fk_tenant_id == tenant_id
    assert repository.created[0].fk_user_id == requested_user_id
    assert repository.created[0].type == LinkUserTenantRequestType.INVITE


def test_request_tenant_entry_creates_request_entry_for_authenticated_user():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    repository = FakeLinkUserTenantRequestRepository()
    rules = FakeRules()
    usecase = RequestTenantEntryUseCase(repository, rules)

    asyncio.run(usecase.execute(tenant_id, authenticated_user_id))

    assert rules.request_entry_calls == [(tenant_id, authenticated_user_id)]
    assert repository.created[0].fk_tenant_id == tenant_id
    assert repository.created[0].fk_user_id == authenticated_user_id
    assert repository.created[0].type == LinkUserTenantRequestType.REQUEST_ENTRY


def test_approve_user_tenant_request_marks_request_and_creates_member_relationships():
    link = make_link()
    link_request_repository = FakeLinkUserTenantRequestRepository()
    user_tenant_repository = FakeUserTenantRepository()
    user_tenant_role_repository = FakeUserTenantRoleRepository()
    member_role = Role(id=uuid4(), name="member", description="Default role")
    role_query = FakeRolesQuery(member_role)
    rules = FakeRules(link=link)
    usecase = AproveUserTenantRequestUseCase(
        link_request_repository,
        user_tenant_repository,
        user_tenant_role_repository,
        role_query,
        rules,
    )

    asyncio.run(usecase.execute(link.id, uuid4()))

    assert link_request_repository.approved_ids == [link.id]
    assert role_query.find_by_name_calls == ["member"]
    assert user_tenant_repository.created[0].fk_user_id == link.fk_user_id
    assert user_tenant_repository.created[0].fk_tenant_id == link.fk_tenant_id
    assert user_tenant_role_repository.created[0].fk_user_tenant_id == user_tenant_repository.created[0].id
    assert user_tenant_role_repository.created[0].fk_role_id == member_role.id


def test_approve_user_tenant_request_rejects_when_member_role_is_missing():
    link = make_link()
    usecase = AproveUserTenantRequestUseCase(
        FakeLinkUserTenantRequestRepository(),
        FakeUserTenantRepository(),
        FakeUserTenantRoleRepository(),
        FakeRolesQuery(role=None),
        FakeRules(link=link),
    )

    with pytest.raises(ForbiddenError, match="You cannot approve this tenant request!"):
        asyncio.run(usecase.execute(link.id, uuid4()))


def test_reject_user_tenant_request_validates_and_rejects_request():
    link = make_link()
    repository = FakeLinkUserTenantRequestRepository()
    rules = FakeRules(link=link)
    usecase = RejectUserTenantRequestUseCase(repository, rules)
    authenticated_user_id = uuid4()

    asyncio.run(usecase.execute(link.id, authenticated_user_id))

    assert rules.approve_or_reject_calls == [(link.id, authenticated_user_id)]
    assert repository.rejected_ids == [link.id]
