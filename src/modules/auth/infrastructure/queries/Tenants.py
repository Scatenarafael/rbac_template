from uuid import UUID

from sqlalchemy import select
from sqlmodel import col

from src.core.pagination import DEFAULT_PER_PAGE, ListResult, paginate_query
from src.modules.auth.domain.entities import Tenant
from src.modules.auth.domain.interfaces.queries.Tenants import ITenantsQuery
from src.modules.auth.infrastructure.mappers.TenantMappers import TenantMapper
from src.modules.auth.infrastructure.models.Tenant import TenantModel


class TenantsQuery(ITenantsQuery):
    async def list(self, page: int | None = None, per_page: int = DEFAULT_PER_PAGE, search: str | None = None) -> ListResult[Tenant]:
        stmt = select(TenantModel).order_by(TenantModel.name)  # type: ignore[arg-type]
        search_term = self._normalize_search(search)

        if search_term is not None:
            stmt = stmt.where(col(TenantModel.name).ilike(f"%{search_term}%", escape="\\"))

        return await paginate_query(self._session, stmt, TenantMapper.to_entity, page, per_page)

    def _normalize_search(self, search: str | None) -> str | None:
        if search is None:
            return None

        search_term = search.strip()
        if not search_term:
            return None

        return search_term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

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
