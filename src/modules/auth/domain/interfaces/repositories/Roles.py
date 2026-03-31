from abc import abstractmethod
from uuid import UUID

from src.modules.auth.domain.entities.Role import Role
from src.modules.auth.domain.interfaces.repositories.Base import IRepositoryBase


class IRolesRepository(IRepositoryBase[Role, UUID]):
    @abstractmethod
    async def find_by_name(self, name: str) -> Role | None:
        pass
