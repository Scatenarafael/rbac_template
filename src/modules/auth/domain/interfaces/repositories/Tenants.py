from abc import abstractmethod
from uuid import UUID

from src.modules.auth.domain.entities.Tenant import Tenant
from src.modules.auth.domain.interfaces.repositories.Base import IRepositoryBase


class ITenantRepository(IRepositoryBase[Tenant, UUID]):
    @abstractmethod
    async def find_by_name(self, name: str) -> Tenant | None:
        raise NotImplementedError
