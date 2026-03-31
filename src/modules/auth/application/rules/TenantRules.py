from uuid import UUID

from src.modules.auth.domain.entities import User
from src.modules.auth.domain.interfaces.repositories.Tenants import ITenantRepository
from src.modules.auth.domain.interfaces.repositories.Users import IUserRepository


class TenantRules:
    def __init__(self, tenant_repository: ITenantRepository, user_repository: IUserRepository) -> None:
        self.tenant_repository = tenant_repository
        self.user_repository = user_repository

    async def validate_tenant_creation(self, name: str, user_id: UUID) -> User:
        # Check if tenant name is already taken
        if await self.tenant_repository.find_by_name(name):
            raise ValueError("Tenant name already exists!")

        user = await self.user_repository.get_by_id(id=user_id)

        # Check if user exists
        if not user:
            raise ValueError("User does not exist!")

        return user
