# type: ignore

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.pagination import DEFAULT_PER_PAGE, ListResult, paginate_query
from src.core.logging import get_logger
from src.modules.auth.domain.entities import User, UserWithTenantRoles
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.infrastructure.mappers.UserMappers import UserMapper
from src.modules.auth.infrastructure.models.User import UserModel
from src.modules.auth.infrastructure.models.UserTenant import UserTenantModel
from src.modules.auth.infrastructure.models.UserTenantRole import UserTenantRoleModel

logger = get_logger(__name__)


class UsersQuery(IUsersQuery):
    async def list(self, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[User]:
        stmt = select(UserModel)  # type: ignore[arg-type]
        return await paginate_query(self._session, stmt, UserMapper.to_entity, page, per_page)

    async def get_by_id(self, id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return UserMapper.to_entity(user)

    async def find_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return UserMapper.to_entity(user)

    async def me(self, user_id: UUID) -> UserWithTenantRoles | None:
        stmt = (
            select(UserModel)
            .options(
                selectinload(UserModel.user_tenants)
                .selectinload(UserTenantModel.user_tenant_roles)
                .selectinload(UserTenantRoleModel.role),
                selectinload(UserModel.user_tenants).selectinload(UserTenantModel.tenant),
            )
            .where(UserModel.id == user_id)  # type: ignore[arg-type]
        )

        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return UserMapper.to_entity_with_tenant_roles(user)
