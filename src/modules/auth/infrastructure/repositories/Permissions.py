from src.modules.auth.domain.entities.Permission import Permission
from src.modules.auth.domain.interfaces.repositories.Permissions import IPermissionsRepository
from src.modules.auth.infrastructure.mappers.PermissionMappers import PermissionMapper


class PermissionsRepository(IPermissionsRepository):
    async def create(self, data: Permission) -> Permission:
        permission_model = PermissionMapper.from_entity(data)

        self._session.add(permission_model)
        await self._session.commit()
        await self._session.refresh(permission_model)
        return PermissionMapper.to_entity(permission_model)
