from uuid import UUID

from src.modules.auth.application.rules.LinkUserTenantRequestsRules import LinkUserTenantRequestsRules
from src.modules.auth.domain.entities import LinkUserTenantRequest, UserTenant, UserTenantRole
from src.modules.auth.domain.exceptions import ForbiddenError
from src.modules.auth.domain.interfaces.queries.LinkUserTenantRequests import ILinkUserTenantRequestsQuery
from src.modules.auth.domain.interfaces.queries.Roles import IRolesQuery
from src.modules.auth.domain.interfaces.repositories.LinkUserTenantRequest import ILinkUserTenantRequestRepository
from src.modules.auth.domain.interfaces.repositories.UserTenantRoles import IUserTenantRoleRepository
from src.modules.auth.domain.interfaces.repositories.UserTenants import IUserTenantRepository


class ListLinkUserTenantRequestUseCase:
    def __init__(self, link_user_tenant_request_query: ILinkUserTenantRequestsQuery, rules: LinkUserTenantRequestsRules):
        self.link_user_tenant_request_query = link_user_tenant_request_query
        self.rules = rules

    async def execute(self, tenant_id: UUID, authenticated_user_id: UUID):

        await self.rules.validate_list_link_user_tenant_requests(tenant_id, authenticated_user_id)

        return await self.link_user_tenant_request_query.list_by_tenant_id(tenant_id)


class InviteUserToTenantUseCase:
    def __init__(self, link_user_tenant_request_repository: ILinkUserTenantRequestRepository, rules: LinkUserTenantRequestsRules):
        self.link_user_tenant_request_repository = link_user_tenant_request_repository
        self.rules = rules

    async def execute(self, tenant_id: UUID, authenticated_user_id: UUID, requested_user_id: UUID):
        await self.rules.validate_invite_user_to_tenant(tenant_id, authenticated_user_id, requested_user_id)

        link_user_tenant_request = LinkUserTenantRequest(fk_tenant_id=tenant_id, fk_user_id=requested_user_id)

        await self.link_user_tenant_request_repository.create(link_user_tenant_request)


class RequestTenantEntryUseCase:
    def __init__(self, link_user_tenant_request_repository: ILinkUserTenantRequestRepository, rules: LinkUserTenantRequestsRules):
        self.link_user_tenant_request_repository = link_user_tenant_request_repository
        self.rules = rules

    async def execute(self, tenant_id: UUID, authenticated_user_id: UUID):

        await self.rules.validate_request_tenant_entry(tenant_id, authenticated_user_id)

        link_user_tenant_request = LinkUserTenantRequest(fk_tenant_id=tenant_id, fk_user_id=authenticated_user_id)

        await self.link_user_tenant_request_repository.create(link_user_tenant_request)


class AproveUserTenantRequestUseCase:
    def __init__(
        self,
        link_user_tenant_request_repository: ILinkUserTenantRequestRepository,
        user_tenant_repository: IUserTenantRepository,
        user_tenant_role_repository: IUserTenantRoleRepository,
        role_query: IRolesQuery,
        rules: LinkUserTenantRequestsRules,
    ):
        self.link_user_tenant_request_repository = link_user_tenant_request_repository
        self.user_tenant_repository = user_tenant_repository
        self.user_tenant_role_repository = user_tenant_role_repository
        self.role_query = role_query
        self.rules = rules

    async def execute(self, link_user_tenant_request_id: UUID, authenticated_user_id: UUID):

        link = await self.rules.validate_approve_or_reject_link_user_tenant_request(link_user_tenant_request_id, authenticated_user_id)

        if not link:
            raise ForbiddenError("You cannot approve this tenant request!")

        member_role = await self.role_query.find_by_name("member")

        if not member_role:
            raise ForbiddenError("You cannot approve this tenant request!")

        user_tenant = UserTenant(fk_user_id=link.fk_user_id, fk_tenant_id=link.fk_tenant_id)

        user_tenant_instance = await self.user_tenant_repository.create(user_tenant)

        user_tenant_role = UserTenantRole(fk_user_tenant_id=user_tenant_instance.id, fk_role_id=member_role.id)

        await self.user_tenant_role_repository.create(user_tenant_role)

        approved_link = await self.link_user_tenant_request_repository.approve(link_user_tenant_request_id)

        if not approved_link:
            raise ForbiddenError("You cannot approve this tenant request!")


class RejectUserTenantRequestUseCase:
    def __init__(self, link_user_tenant_request_repository: ILinkUserTenantRequestRepository, rules: LinkUserTenantRequestsRules):
        self.link_user_tenant_request_repository = link_user_tenant_request_repository
        self.rules = rules

    async def execute(self, link_user_tenant_request_id: UUID, authenticated_user_id: UUID):

        await self.rules.validate_approve_or_reject_link_user_tenant_request(link_user_tenant_request_id, authenticated_user_id)

        await self.link_user_tenant_request_repository.reject(link_user_tenant_request_id)
