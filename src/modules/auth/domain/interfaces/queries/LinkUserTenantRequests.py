from abc import abstractmethod
from typing import Sequence
from uuid import UUID

from src.modules.auth.domain.entities.LinkUserTenantRequest import LinkUserTenantRequest, LinkUserTenantRequestDetailed
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class ILinkUserTenantRequestsQuery(IQueryBase[LinkUserTenantRequest, UUID]):
    @abstractmethod
    async def list_by_tenant_id(self, tenant_id: UUID) -> Sequence[LinkUserTenantRequestDetailed]:
        pass
