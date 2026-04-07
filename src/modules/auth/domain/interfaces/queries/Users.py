from abc import abstractmethod
from uuid import UUID

from src.modules.auth.domain.entities import User, UserWithTenantRoles
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class IUsersQuery(IQueryBase[User, UUID]):
    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def me(self, user_id: UUID) -> UserWithTenantRoles | None:
        pass
