from uuid import UUID

from src.modules.auth.domain.entities import UserTenantRole, UserTenantRoleDetailed
from src.modules.auth.infrastructure.mappers.RoleMappers import RoleMapper
from src.modules.auth.infrastructure.mappers.TenantMappers import TenantMapper
from src.modules.auth.infrastructure.models.Tenant import TenantModel
from src.modules.auth.infrastructure.models.UserTenantRole import UserTenantRoleModel


class UserTenantRoleMapper:
    @staticmethod
    def to_entity(model: UserTenantRoleModel) -> UserTenantRole:
        return UserTenantRole(
            id=UUID(str(model.id)),
            fk_user_tenant_id=UUID(str(model.fk_user_tenant_id)),
            fk_role_id=UUID(str(model.fk_role_id)),
        )

    @staticmethod
    def from_entity(entity: UserTenantRole) -> UserTenantRoleModel:

        return UserTenantRoleModel(
            id=entity.id,
            fk_user_tenant_id=entity.fk_user_tenant_id,
            fk_role_id=entity.fk_role_id,
        )


class UserTenantRoleDetailedMapper:
    @staticmethod
    def to_entity(model: UserTenantRoleModel, tenant_model: TenantModel | None = None) -> UserTenantRoleDetailed:
        return UserTenantRoleDetailed(
            id=UUID(str(model.id)),
            fk_user_tenant_id=UUID(str(model.fk_user_tenant_id)),
            fk_role_id=UUID(str(model.fk_role_id)),
            tenant=TenantMapper.to_entity(tenant_model) if tenant_model is not None else None,
            role=RoleMapper.to_entity(model.role),
        )
