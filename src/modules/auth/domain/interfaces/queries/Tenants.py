from abc import abstractmethod
from uuid import UUID

from src.modules.auth.domain.entities import Tenant
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class ITenantsQuery(IQueryBase[Tenant, UUID]):
    @abstractmethod
    async def find_by_name(self, name: str) -> Tenant | None:
        pass
