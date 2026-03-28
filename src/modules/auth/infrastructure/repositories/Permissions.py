from uuid import UUID

from sqlalchemy import select

from src.modules.auth.domain.entities.Permission import Permission
from src.modules.auth.domain.interfaces.repositories.Permissions import IPermissionsRepository
from src.modules.auth.infrastructure.mappers.PermissionMappers import PermissionMapper
from src.modules.auth.infrastructure.models.Permission import PermissionModel


class PermissionsRepository(IPermissionsRepository):
    async def get_by_id(self, id: UUID) -> Permission:
        stmt = select(PermissionModel).where(PermissionModel.id == id)  # type: ignore

        result = await self._session.execute(stmt)

        permission = result.scalar_one_or_none()

        return PermissionMapper.to_entity(permission)  # type: ignore

    async def create(self, data: Permission) -> Permission:
        permission_model = PermissionMapper.from_entity(data)

        self._session.add(permission_model)
        await self._session.commit()
        await self._session.refresh(permission_model)
        return PermissionMapper.to_entity(permission_model)
