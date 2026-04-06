from uuid import UUID

from sqlalchemy import select

from src.modules.auth.domain.entities.UserTenant import UserTenant
from src.modules.auth.domain.interfaces.repositories.UserTenants import IUserTenantRepository
from src.modules.auth.infrastructure.mappers.UserTenantMappers import UserTenantMapper
from src.modules.auth.infrastructure.models.UserTenant import UserTenantModel


class UserTenantRepository(IUserTenantRepository):
    async def create(self, data: UserTenant) -> UserTenant:
        usertenant = UserTenantMapper.from_entity(data)

        self._session.add(usertenant)
        await self._session.flush()
        await self._session.refresh(usertenant)
        return UserTenantMapper.to_entity(usertenant)

    async def update(self, id: UUID, data: dict) -> UserTenant | None:
        stmt = select(UserTenantModel).where(UserTenantModel.id == id)  # type: ignore

        result = await self._session.execute(stmt)

        usertenant = result.scalar_one_or_none()

        if usertenant is None:
            return None

        for key, value in data.items():
            setattr(usertenant, key, value)

        await self._session.commit()
        await self._session.refresh(usertenant)
        return UserTenantMapper.to_entity(usertenant)

    async def delete(self, id: UUID) -> None:
        stmt = select(UserTenantModel).where(UserTenantModel.id == id)  # type: ignore

        result = await self._session.execute(stmt)

        usertenant = result.scalar_one_or_none()

        if usertenant is None:
            return None

        await self._session.delete(usertenant)
        await self._session.commit()
        return None
