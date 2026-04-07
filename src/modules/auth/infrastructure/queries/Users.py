# type: ignore

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.modules.auth.domain.entities import User, UserWithTenantRoles
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.infrastructure.mappers.UserMappers import UserMapper
from src.modules.auth.infrastructure.models.User import UserModel
from src.modules.auth.infrastructure.models.UserTenant import UserTenantModel
from src.modules.auth.infrastructure.models.UserTenantRole import UserTenantRoleModel


class UsersQuery(IUsersQuery):
    async def list(self) -> list[User]:
        stmt = select(UserModel)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        users = result.scalars().all()
        return [UserMapper.to_entity(user) for user in users]

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
        stmt = select(UserModel).options(selectinload(UserModel.user_tenants).selectinload(UserTenantModel.user_tenant_roles).selectinload(UserTenantRoleModel.role)).where(UserModel.id == user_id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return UserMapper.to_entity_with_tenant_roles(user)
