from abc import abstractmethod
from typing import overload
from uuid import UUID

from src.core.pagination import DEFAULT_PER_PAGE, ListResult
from src.modules.auth.domain.entities.LinkUserTenantRequest import LinkTenantRequestDetailed, LinkUserTenantRequest, LinkUserTenantRequestDetailed
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class ILinkUserTenantRequestsQuery(IQueryBase[LinkUserTenantRequest, UUID]):
    @abstractmethod
    async def list_by_tenant_id(self, tenant_id: UUID, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[LinkUserTenantRequestDetailed]:
        pass

    @overload
    async def find_pending_by_tenant_and_user(self, tenant_id: UUID, user_id: UUID, page: None = None) -> LinkUserTenantRequest | None:
        ...

    @overload
    async def find_pending_by_tenant_and_user(self, tenant_id: UUID, user_id: UUID, page: int, per_page: int = DEFAULT_PER_PAGE) -> ListResult[LinkUserTenantRequest]:
        ...

    @abstractmethod
    async def find_pending_by_tenant_and_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        page: int | None = None,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> LinkUserTenantRequest | None | ListResult[LinkUserTenantRequest]:
        pass

    @abstractmethod
    async def find_pending_by_user(self, user_id: UUID, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[LinkTenantRequestDetailed]:
        pass
