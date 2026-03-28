from uuid import UUID

from src.modules.auth.domain.entities import Permission
from src.modules.auth.domain.value_objects.Permissions import PermissionCode
from src.modules.auth.infrastructure.models.Permission import PermissionModel


class PermissionMapper:
    @staticmethod
    def to_entity(model: PermissionModel) -> Permission:
        return Permission(
            id=UUID(str(model.id)),
            code=PermissionCode(str(model.code)),
            description=str(model.description),
        )

    @staticmethod
    def from_entity(entity: Permission) -> PermissionModel:

        return PermissionModel(
            id=entity.id,
            code=entity.code.value,
            description=entity.description,
        )
