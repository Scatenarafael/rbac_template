from uuid import UUID

from src.modules.auth.domain.entities import User
from src.modules.auth.domain.exceptions import ForbiddenError, TenantAlreadyExists, UserNotFound, ValidationError
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

        utr = await self.user_tenant_role_query.find_utr_by_user_and_tenant_id(logged_user_id, tenant_id)

        if not utr or utr[0].role.name != "tenantadmin":
            raise ForbiddenError("User does not have rights to update this tenant!")

        tenant = await self.tenants_query.get_by_id(tenant_id)

        if not tenant:
            raise TenantAlreadyExists("Tenant does not exist!")

        new_name = payload.get("name")

        if not new_name:
            raise ValidationError("Paylod is not valid! Missing required fields")

        if tenant.name != new_name and await self.tenants_query.find_by_name(new_name):
            raise TenantAlreadyExists("Tenant name already exists!")

    async def validate_tenant_deletion(self, tenant_id: UUID, logged_user_id: UUID) -> None:

        utr = await self.user_tenant_role_query.find_utr_by_user_and_tenant_id(logged_user_id, tenant_id)

        if not utr or utr[0].role.name != "tenantadmin":
            raise ForbiddenError("User does not have rights to delete this tenant!")

        tenant = await self.tenants_query.get_by_id(tenant_id)

        if not tenant:
            raise TenantAlreadyExists("Tenant does not exist!")
