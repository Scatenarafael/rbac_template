from uuid import UUID

from sqlalchemy import select

from src.core.pagination import DEFAULT_PER_PAGE, ListResult, paginate_query
from src.modules.auth.domain.entities import Role
from src.modules.auth.domain.interfaces.queries.Roles import IRolesQuery
from src.modules.auth.infrastructure.mappers.RoleMappers import RoleMapper
from src.modules.auth.infrastructure.models.Role import RoleModel


class RolesQuery(IRolesQuery):
    async def list(self, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[Role]:
        stmt = select(RoleModel)  # type: ignore[arg-type]
        return await paginate_query(self._session, stmt, RoleMapper.to_entity, page, per_page)

    async def get_by_id(self, id: UUID) -> Role | None:
        stmt = select(RoleModel).where(RoleModel.id == id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        role = result.scalar_one_or_none()

        if role is None:
            return None

        return RoleMapper.to_entity(role)

    async def find_by_name(self, name: str) -> Role | None:
        normalized_name = name.strip().lower()
        stmt = select(RoleModel).where(RoleModel.name == normalized_name)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        role = result.scalar_one_or_none()

        if role is None:
            return None

        return RoleMapper.to_entity(role)
