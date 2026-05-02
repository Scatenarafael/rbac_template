from abc import abstractmethod
from uuid import UUID

from src.core.pagination import DEFAULT_PER_PAGE, ListResult
from src.modules.auth.domain.entities import Tenant
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class ITenantsQuery(IQueryBase[Tenant, UUID]):
    @abstractmethod
    async def list(self, page: int | None = None, per_page: int = DEFAULT_PER_PAGE, search: str | None = None) -> ListResult[Tenant]:
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Tenant | None:
        pass
