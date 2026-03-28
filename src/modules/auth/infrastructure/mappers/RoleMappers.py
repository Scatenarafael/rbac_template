from uuid import UUID

from src.modules.auth.domain.entities.Role import Role
from src.modules.auth.infrastructure.models.Role import RoleModel


class RoleMapper:
    @staticmethod
    def to_entity(model: RoleModel) -> Role:
        return Role(
            id=UUID(str(model.id)),
            name=str(model.name),
            description=str(model.description),
        )

    @staticmethod
    def from_entity(entity: Role) -> RoleModel:

        return RoleModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
        )
