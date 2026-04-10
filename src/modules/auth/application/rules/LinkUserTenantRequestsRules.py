from uuid import UUID

from src.modules.auth.application.rules.common.utils import CommonRules
from src.modules.auth.domain.exceptions import NotFoundError, ValidationError
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.domain.interfaces.queries.UserTenantRoles import IUserTenantRoleQuery


class LinkUserTenantRequestsRules:
    def __init__(self, users_query: IUsersQuery, user_tenant_role_query: IUserTenantRoleQuery):
        self.users_query = users_query
        self.user_tenant_role_query = user_tenant_role_query

    async def validate_list_link_user_tenant_requests(self, tenant_id: UUID, logged_user_id: UUID):
        await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, logged_user_id, tenant_id)

    async def validate_invite_user_to_tenant(self, tenant_id: UUID, logged_user_id: UUID, requested_user_id: UUID):
        await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, logged_user_id, tenant_id)

        user = await self.users_query.get_by_id(requested_user_id)

        if not user:
            raise NotFoundError("User does not exist!")

        is_requested_user_member = await CommonRules().validates_if_user_is_tenant_member(self.user_tenant_role_query, requested_user_id, tenant_id)

        if is_requested_user_member:
            raise ValidationError("This user cannot be invited to the tenant!")
