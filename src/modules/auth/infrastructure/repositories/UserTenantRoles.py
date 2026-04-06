from uuid import UUID

from sqlalchemy import select

from src.modules.auth.domain.entities.UserTenantRole import UserTenantRole
from src.modules.auth.domain.interfaces.repositories.UserTenantRoles import IUserTenantRoleRepository
from src.modules.auth.infrastructure.mappers.UserTenantRoleMappers import UserTenantRoleMapper
from src.modules.auth.infrastructure.models.UserTenantRole import UserTenantRoleModel


class UserTenantRoleRepository(IUserTenantRoleRepository):
    async def create(self, data: UserTenantRole) -> UserTenantRole:
        usertenantrole = UserTenantRoleMapper.from_entity(data)

        self._session.add(usertenantrole)
        await self._session.flush()
        await self._session.refresh(usertenantrole)
        return UserTenantRoleMapper.to_entity(usertenantrole)

    async def update(self, id: UUID, data: dict) -> UserTenantRole | None:
        stmt = select(UserTenantRoleModel).where(UserTenantRoleModel.id == id)  # type: ignore

        result = await self._session.execute(stmt)

        usertenantrole = result.scalar_one_or_none()

        if usertenantrole is None:
            return None

        for key, value in data.items():
            setattr(usertenantrole, key, value)

        await self._session.commit()
        await self._session.refresh(usertenantrole)
        return UserTenantRoleMapper.to_entity(usertenantrole)

    async def delete(self, id: UUID) -> None:
        stmt = select(UserTenantRoleModel).where(UserTenantRoleModel.id == id)  # type: ignore

        result = await self._session.execute(stmt)

        usertenantrole = result.scalar_one_or_none()

        if usertenantrole is None:
            return None

        await self._session.delete(usertenantrole)
        await self._session.commit()
