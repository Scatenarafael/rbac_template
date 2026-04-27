from uuid import UUID

from sqlalchemy import select

from src.core.pagination import DEFAULT_PER_PAGE, ListResult, paginate_query
from src.modules.auth.domain.entities import Tenant
from src.modules.auth.domain.interfaces.queries.Tenants import ITenantsQuery
from src.modules.auth.infrastructure.mappers.TenantMappers import TenantMapper
from src.modules.auth.infrastructure.models.Tenant import TenantModel


class TenantsQuery(ITenantsQuery):
    async def list(self, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[Tenant]:
        stmt = select(TenantModel)  # type: ignore[arg-type]
        return await paginate_query(self._session, stmt, TenantMapper.to_entity, page, per_page)

    async def get_by_id(self, id: UUID) -> Tenant | None:
        stmt = select(TenantModel).where(TenantModel.id == id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        tenant = result.scalar_one_or_none()

        if tenant is None:
            return None

        return TenantMapper.to_entity(tenant)

    async def find_by_name(self, name: str) -> Tenant | None:
        stmt = select(TenantModel).where(TenantModel.name == name)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        tenant = result.scalar_one_or_none()

        if tenant is None:
            return None

        return TenantMapper.to_entity(tenant)
