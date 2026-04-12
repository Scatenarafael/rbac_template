from uuid import UUID

from src.core.logging import get_logger
from src.modules.auth.domain.exceptions import ForbiddenError
from src.modules.auth.domain.interfaces.queries.UserTenantRoles import IUserTenantRoleQuery

logger = get_logger(__name__)


class CommonRules:
    @staticmethod
    async def validates_if_user_is_tenant_admin(user_tenant_role_query: IUserTenantRoleQuery, user_id: UUID, tenant_id: UUID):
        utr = await user_tenant_role_query.find_utr_by_user_and_tenant_id(user_id, tenant_id)
        role_name = getattr(getattr(utr[0], "role", None), "name", None) if utr else None

        if role_name != "tenantadmin":
            logger.debug(
                "Tenant admin validation failed",
                user_id=user_id,
                tenant_id=tenant_id,
                role_name=role_name,
            )
            raise ForbiddenError("User does not have rights to perform this action!")

    @staticmethod
    async def validates_if_user_is_tenant_member(user_tenant_role_query: IUserTenantRoleQuery, user_id: UUID, tenant_id: UUID) -> bool:
        utr = await user_tenant_role_query.find_utr_by_user_and_tenant_id(user_id, tenant_id)

        return bool(utr)
