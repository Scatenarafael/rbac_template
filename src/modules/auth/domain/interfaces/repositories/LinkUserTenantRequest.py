from abc import abstractmethod
from uuid import UUID

from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.interfaces.repositories.Base import IRepositoryBase


class ILinkUserTenantRequestRepository(IRepositoryBase[LinkUserTenantRequest, UUID]):
    @abstractmethod
    async def approve(self, id: UUID) -> LinkUserTenantRequest | None:
        pass

    @abstractmethod
    async def reject(self, id: UUID) -> LinkUserTenantRequest | None:
        pass
