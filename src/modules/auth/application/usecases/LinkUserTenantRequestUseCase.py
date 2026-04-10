from uuid import UUID

from src.modules.auth.application.rules.LinkUserTenantRequestsRules import LinkUserTenantRequestsRules
from src.modules.auth.domain.interfaces.queries.LinkUserTenantRequests import ILinkUserTenantRequestsQuery
from src.modules.auth.domain.interfaces.repositories.LinkUserTenantRequest import ILinkUserTenantRequestRepository


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

        await self.link_user_tenant_request_repository.create_link_user_tenant_request(tenant_id, requested_user_id)
