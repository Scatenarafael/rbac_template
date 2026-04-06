from abc import abstractmethod
from uuid import UUID

from src.modules.auth.domain.entities import Role
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class IRolesQuery(IQueryBase[Role, UUID]):
    @abstractmethod
    async def find_by_name(self, name: str) -> Role | None:
        pass
