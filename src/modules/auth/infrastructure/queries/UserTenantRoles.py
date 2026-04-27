# type: ignore
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.pagination import DEFAULT_PER_PAGE, ListResult, paginate_query
from src.modules.auth.domain.entities import UserTenantRoleDetailed
from src.modules.auth.domain.interfaces.queries.UserTenantRoles import IUserTenantRoleQuery
from src.modules.auth.infrastructure.mappers.UserTenantRoleMappers import UserTenantRoleDetailedMapper
from src.modules.auth.infrastructure.models.UserTenant import UserTenantModel
from src.modules.auth.infrastructure.models.UserTenantRole import UserTenantRoleModel


class UserTenantRolesQuery(IUserTenantRoleQuery):
    async def list(self, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[UserTenantRoleDetailed]:
        stmt = select(UserTenantRoleModel).options(selectinload(UserTenantRoleModel.role))
        return await paginate_query(self._session, stmt, UserTenantRoleDetailedMapper.to_entity, page, per_page)

    async def get_by_id(self, id: UUID) -> UserTenantRoleDetailed | None:
        stmt = select(UserTenantRoleModel).options(selectinload(UserTenantRoleModel.role)).where(UserTenantRoleModel.id == id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return UserTenantRoleDetailedMapper.to_entity(model)

    async def find_utr_by_user_and_tenant_id(self, user_id: UUID, tenant_id: UUID) -> Sequence[UserTenantRoleDetailed]:
        stmt = (
            select(UserTenantRoleModel)
            .join(UserTenantModel, UserTenantModel.id == UserTenantRoleModel.fk_user_tenant_id)
            .options(selectinload(UserTenantRoleModel.role))
            .where(
                UserTenantModel.fk_user_id == user_id,
                UserTenantModel.fk_tenant_id == tenant_id,
            )
        )  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        return [UserTenantRoleDetailedMapper.to_entity(model) for model in result.scalars().all()]
