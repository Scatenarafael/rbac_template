from uuid import UUID

from src.modules.auth.domain.exceptions import ForbiddenError
from src.modules.auth.domain.interfaces.queries.UserTenantRoles import IUserTenantRoleQuery


class CommonRules:
    @staticmethod
    async def validates_if_user_is_tenant_admin(user_tenant_role_query: IUserTenantRoleQuery, user_id: UUID, tenant_id: UUID):
        utr = await user_tenant_role_query.find_utr_by_user_and_tenant_id(user_id, tenant_id)

        if not utr or utr[0].role.name != "tenantadmin":
            raise ForbiddenError("User does not have rights to perform this action!")

    @staticmethod
    async def validates_if_user_is_tenant_member(user_tenant_role_query: IUserTenantRoleQuery, user_id: UUID, tenant_id: UUID) -> bool:
        utr = await user_tenant_role_query.find_utr_by_user_and_tenant_id(user_id, tenant_id)

        return utr is not None
