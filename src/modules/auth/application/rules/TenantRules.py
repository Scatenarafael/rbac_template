from uuid import UUID

from src.modules.auth.application.rules.common.utils import CommonRules
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.exceptions import NotFoundError, TenantAlreadyExists, UserNotFound, ValidationError
from src.modules.auth.domain.interfaces.queries.Tenants import ITenantsQuery
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.domain.interfaces.queries.UserTenantRoles import IUserTenantRoleQuery


class TenantRules:
    def __init__(self, tenants_query: ITenantsQuery, users_query: IUsersQuery, user_tenant_role_query: IUserTenantRoleQuery) -> None:
        self.tenants_query = tenants_query
        self.users_query = users_query
        self.user_tenant_role_query = user_tenant_role_query

    async def validate_tenant_creation(self, name: str, user_id: UUID) -> User:
        # Check if tenant name is already taken
        if await self.tenants_query.find_by_name(name):
            raise TenantAlreadyExists("Tenant name already exists!")

        user = await self.users_query.get_by_id(id=user_id)

        # Check if user exists
        if not user:
            raise UserNotFound("User does not exist!")

        return user

    async def validate_tenant_update(self, tenant_id: UUID, payload: dict, logged_user_id: UUID) -> None:

        await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, logged_user_id, tenant_id)

        tenant = await self.tenants_query.get_by_id(tenant_id)

        if not tenant:
            raise NotFoundError("Tenant does not exist!")

        new_name = payload.get("name")

        if not new_name:
            raise ValidationError("Payload is not valid! Missing required fields")

        if tenant.name != new_name and await self.tenants_query.find_by_name(new_name):
            raise TenantAlreadyExists("Tenant name already exists!")

    async def validate_tenant_deletion(self, tenant_id: UUID, logged_user_id: UUID) -> None:

        await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, logged_user_id, tenant_id)

        tenant = await self.tenants_query.get_by_id(tenant_id)

        if not tenant:
            raise NotFoundError("Tenant does not exist!")
