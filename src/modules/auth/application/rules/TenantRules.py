from uuid import UUID

from src.modules.auth.domain.entities import User
from src.modules.auth.domain.exceptions import TenantAlreadyExists, UserNotFound
from src.modules.auth.domain.interfaces.queries.Tenants import ITenantsQuery
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery


class TenantRules:
    def __init__(self, tenants_query: ITenantsQuery, users_query: IUsersQuery) -> None:
        self.tenants_query = tenants_query
        self.users_query = users_query

    async def validate_tenant_creation(self, name: str, user_id: UUID) -> User:
        # Check if tenant name is already taken
        if await self.tenants_query.find_by_name(name):
            raise TenantAlreadyExists("Tenant name already exists!")

        user = await self.users_query.get_by_id(id=user_id)

        # Check if user exists
        if not user:
            raise UserNotFound("User does not exist!")

        return user
