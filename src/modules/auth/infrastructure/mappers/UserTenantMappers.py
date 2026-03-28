from uuid import UUID

from src.modules.auth.domain.entities import UserTenant
from src.modules.auth.infrastructure.models.UserTenant import UserTenantModel


class UserTenantMapper:
    @staticmethod
    def to_entity(model: UserTenantModel) -> UserTenant:
        return UserTenant(
            id=UUID(str(model.id)),
            fk_user_id=UUID(str(model.fk_user_id)),
            fk_tenant_id=UUID(str(model.fk_tenant_id)),
        )

    @staticmethod
    def from_entity(entity: UserTenant) -> UserTenantModel:

        return UserTenantModel(
            id=entity.id,
            fk_user_id=entity.fk_user_id,
            fk_tenant_id=entity.fk_tenant_id,
        )
