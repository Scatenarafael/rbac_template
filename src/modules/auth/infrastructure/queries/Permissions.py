from uuid import UUID

from sqlalchemy import select

from src.modules.auth.domain.entities import Permission
from src.modules.auth.domain.interfaces.queries.Permissions import IPermissionsQuery
from src.modules.auth.infrastructure.mappers.PermissionMappers import PermissionMapper
from src.modules.auth.infrastructure.models.Permission import PermissionModel


class PermissionsQuery(IPermissionsQuery):
    async def list(self) -> list[Permission]:
        stmt = select(PermissionModel)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        permissions = result.scalars().all()
        return [PermissionMapper.to_entity(permission) for permission in permissions]

    async def get_by_id(self, id: UUID) -> Permission | None:
        stmt = select(PermissionModel).where(PermissionModel.id == id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        permission = result.scalar_one_or_none()

        if permission is None:
            return None

        return PermissionMapper.to_entity(permission)
