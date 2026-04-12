# pyright: reportArgumentType=false
import asyncio
from uuid import uuid4

import pytest

from src.modules.auth.application.rules.LinkUserTenantRequestsRules import LinkUserTenantRequestsRules
from src.modules.auth.domain.entities import LinkUserTenantRequest, Role, User
from src.modules.auth.domain.entities.UserTenantRole import UserTenantRoleDetailed
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestType
from src.modules.auth.domain.exceptions import (
    ConflictError,
    ForbiddenError,
    LinkUserTenantRequestAlreadyPending,
    NotFoundError,
    ValidationError,
)
from src.modules.auth.domain.value_objects.Emails import Email


class FakeUsersQuery:
    def __init__(self, user: User | None = None) -> None:
        self.user = user
        self.get_by_id_calls = []

    async def get_by_id(self, id):
        self.get_by_id_calls.append(id)
        return self.user


class FakeUserTenantRoleQuery:
    def __init__(self, memberships: dict[tuple[object, object], object] | None = None) -> None:
        self.memberships = memberships or {}
        self.find_calls = []

    async def find_utr_by_user_and_tenant_id(self, user_id, tenant_id):
        self.find_calls.append((user_id, tenant_id))
        return self.memberships.get((user_id, tenant_id))


class FakeLinkUserTenantRequestsQuery:
    def __init__(self, link: LinkUserTenantRequest | None = None, pending_request: LinkUserTenantRequest | None = None) -> None:
        self.link = link
        self.pending_request = pending_request
        self.get_by_id_calls = []
        self.find_pending_calls = []

    async def get_by_id(self, id):
        self.get_by_id_calls.append(id)
        return self.link

    async def find_pending_by_tenant_and_user(self, tenant_id, user_id):
        self.find_pending_calls.append((tenant_id, user_id))
        return self.pending_request


def make_user() -> User:
    return User(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email=Email("john.doe@email.com"),
        hashed_password="hashed-password",
    )


def make_role_entry(name: str) -> list[UserTenantRoleDetailed]:
    return [
        UserTenantRoleDetailed(
            id=uuid4(),
            fk_user_tenant_id=uuid4(),
            fk_role_id=uuid4(),
            role=Role(id=uuid4(), name=name),
            tenant=None,
        )
    ]


def make_rules(*, users_query=None, user_tenant_role_query=None, link_query=None) -> LinkUserTenantRequestsRules:
    return LinkUserTenantRequestsRules(
        users_query or FakeUsersQuery(),
        user_tenant_role_query or FakeUserTenantRoleQuery(),
        link_query or FakeLinkUserTenantRequestsQuery(),
    )


def test_validate_list_link_user_tenant_requests_requires_tenant_admin():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    rules = make_rules(
        user_tenant_role_query=FakeUserTenantRoleQuery(
            {(authenticated_user_id, tenant_id): make_role_entry("tenantadmin")}
        )
    )

    asyncio.run(rules.validate_list_link_user_tenant_requests(tenant_id, authenticated_user_id))


def test_validate_list_link_user_tenant_requests_rejects_non_admin_user():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    rules = make_rules(user_tenant_role_query=FakeUserTenantRoleQuery({(authenticated_user_id, tenant_id): make_role_entry("member")}))

    with pytest.raises(ForbiddenError, match="User does not have rights"):
        asyncio.run(rules.validate_list_link_user_tenant_requests(tenant_id, authenticated_user_id))


def test_validate_invite_user_to_tenant_requires_existing_non_member_user_and_admin_actor():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    requested_user = make_user()
    user_tenant_role_query = FakeUserTenantRoleQuery(
        {
            (authenticated_user_id, tenant_id): make_role_entry("tenantadmin"),
            (requested_user.id, tenant_id): None,
        }
    )
    rules = make_rules(users_query=FakeUsersQuery(requested_user), user_tenant_role_query=user_tenant_role_query)

    asyncio.run(rules.validate_invite_user_to_tenant(tenant_id, authenticated_user_id, requested_user.id))

    assert user_tenant_role_query.find_calls == [
        (authenticated_user_id, tenant_id),
        (requested_user.id, tenant_id),
    ]


def test_validate_invite_user_to_tenant_rejects_missing_user():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    requested_user_id = uuid4()
    rules = make_rules(
        users_query=FakeUsersQuery(user=None),
        user_tenant_role_query=FakeUserTenantRoleQuery(
            {(authenticated_user_id, tenant_id): make_role_entry("tenantadmin")}
        ),
    )

    with pytest.raises(NotFoundError, match="User does not exist"):
        asyncio.run(rules.validate_invite_user_to_tenant(tenant_id, authenticated_user_id, requested_user_id))


def test_validate_invite_user_to_tenant_rejects_user_that_is_already_member():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    requested_user = make_user()
    rules = make_rules(
        users_query=FakeUsersQuery(requested_user),
        user_tenant_role_query=FakeUserTenantRoleQuery(
            {
                (authenticated_user_id, tenant_id): make_role_entry("tenantadmin"),
                (requested_user.id, tenant_id): make_role_entry("member"),
            }
        ),
    )

    with pytest.raises(ValidationError, match="cannot be invited"):
        asyncio.run(rules.validate_invite_user_to_tenant(tenant_id, authenticated_user_id, requested_user.id))


def test_validate_invite_user_to_tenant_rejects_existing_pending_request():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    requested_user = make_user()
    pending_request = LinkUserTenantRequest(fk_tenant_id=tenant_id, fk_user_id=requested_user.id)
    link_query = FakeLinkUserTenantRequestsQuery(pending_request=pending_request)
    rules = make_rules(
        users_query=FakeUsersQuery(requested_user),
        user_tenant_role_query=FakeUserTenantRoleQuery(
            {
                (authenticated_user_id, tenant_id): make_role_entry("tenantadmin"),
                (requested_user.id, tenant_id): None,
            }
        ),
        link_query=link_query,
    )

    with pytest.raises(LinkUserTenantRequestAlreadyPending, match="already a pending tenant request"):
        asyncio.run(rules.validate_invite_user_to_tenant(tenant_id, authenticated_user_id, requested_user.id))

    assert link_query.find_pending_calls == [(tenant_id, requested_user.id)]


def test_validate_request_tenant_entry_rejects_user_that_is_already_member():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    rules = make_rules(
        user_tenant_role_query=FakeUserTenantRoleQuery(
            {(authenticated_user_id, tenant_id): make_role_entry("member")}
        )
    )

    with pytest.raises(ValidationError, match="already a member"):
        asyncio.run(rules.validate_request_tenant_entry(tenant_id, authenticated_user_id))


def test_validate_request_tenant_entry_rejects_existing_pending_request():
    tenant_id = uuid4()
    authenticated_user_id = uuid4()
    pending_request = LinkUserTenantRequest(fk_tenant_id=tenant_id, fk_user_id=authenticated_user_id)
    link_query = FakeLinkUserTenantRequestsQuery(pending_request=pending_request)
    rules = make_rules(
        user_tenant_role_query=FakeUserTenantRoleQuery({(authenticated_user_id, tenant_id): None}),
        link_query=link_query,
    )

    with pytest.raises(LinkUserTenantRequestAlreadyPending, match="already a pending tenant request"):
        asyncio.run(rules.validate_request_tenant_entry(tenant_id, authenticated_user_id))

    assert link_query.find_pending_calls == [(tenant_id, authenticated_user_id)]


def test_validate_approve_or_reject_invite_allows_only_invited_user():
    authenticated_user_id = uuid4()
    link = LinkUserTenantRequest(
        fk_tenant_id=uuid4(),
        fk_user_id=uuid4(),
        type=LinkUserTenantRequestType.INVITE,
    )
    rules = make_rules(
        user_tenant_role_query=FakeUserTenantRoleQuery({(authenticated_user_id, link.fk_tenant_id): None}),
        link_query=FakeLinkUserTenantRequestsQuery(link),
    )

    with pytest.raises(ForbiddenError, match="tenant invite request"):
        asyncio.run(rules.validate_approve_or_reject_link_user_tenant_request(link.id, authenticated_user_id))


def test_validate_approve_or_reject_invite_rejects_user_already_in_tenant():
    authenticated_user_id = uuid4()
    link = LinkUserTenantRequest(
        fk_tenant_id=uuid4(),
        fk_user_id=authenticated_user_id,
        type=LinkUserTenantRequestType.INVITE,
    )
    rules = make_rules(
        user_tenant_role_query=FakeUserTenantRoleQuery({(authenticated_user_id, link.fk_tenant_id): make_role_entry("member")}),
        link_query=FakeLinkUserTenantRequestsQuery(link),
    )

    with pytest.raises(ConflictError, match="already a member"):
        asyncio.run(rules.validate_approve_or_reject_link_user_tenant_request(link.id, authenticated_user_id))


def test_validate_approve_or_reject_request_entry_requires_tenant_admin():
    authenticated_user_id = uuid4()
    link = LinkUserTenantRequest(
        fk_tenant_id=uuid4(),
        fk_user_id=uuid4(),
        type=LinkUserTenantRequestType.REQUEST_ENTRY,
    )
    rules = make_rules(
        user_tenant_role_query=FakeUserTenantRoleQuery({(authenticated_user_id, link.fk_tenant_id): make_role_entry("member")}),
        link_query=FakeLinkUserTenantRequestsQuery(link),
    )

    with pytest.raises(ForbiddenError, match="User does not have rights"):
        asyncio.run(rules.validate_approve_or_reject_link_user_tenant_request(link.id, authenticated_user_id))


def test_validate_approve_or_reject_request_raises_not_found_when_link_does_not_exist():
    rules = make_rules(link_query=FakeLinkUserTenantRequestsQuery(link=None))

    with pytest.raises(NotFoundError, match="Link user tenant request not found"):
        asyncio.run(rules.validate_approve_or_reject_link_user_tenant_request(uuid4(), uuid4()))
