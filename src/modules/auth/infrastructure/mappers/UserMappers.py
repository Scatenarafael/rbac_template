from uuid import UUID

from src.modules.auth.domain.entities.Role import Role
from src.modules.auth.domain.entities.Tenant import Tenant
from src.modules.auth.domain.entities.User import User, UserWithTenantRoles
from src.modules.auth.domain.entities.UserTenantRole import UserTenantRoleDetailed
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.infrastructure.models.User import UserModel


class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=UUID(str(model.id)),
            first_name=str(model.first_name),
            last_name=str(model.last_name),
            email=Email(str(model.email)),
            hashed_password=str(model.hashed_password),
        )

    @staticmethod
    def to_entity_with_tenant_roles(model: UserModel) -> UserWithTenantRoles:
        user_tenant_roles = [
            UserTenantRoleDetailed(
                id=UUID(str(user_tenant_role.id)),
                fk_user_tenant_id=UUID(str(user_tenant_role.fk_user_tenant_id)),
                fk_role_id=UUID(str(user_tenant_role.fk_role_id)),
                tenant=Tenant(
                    id=UUID(str(user_tenant.tenant.id)),
                    name=str(user_tenant.tenant.name),
                ),
                role=Role(
                    id=UUID(str(user_tenant_role.role.id)),
                    name=str(user_tenant_role.role.name),
                ),
            )
            for user_tenant in model.user_tenants
            for user_tenant_role in user_tenant.user_tenant_roles
        ]

        return UserWithTenantRoles(
            id=UUID(str(model.id)),
            first_name=str(model.first_name),
            last_name=str(model.last_name),
            email=str(model.email),
            user_tenant_roles=user_tenant_roles,
        )

    @staticmethod
    def from_entity(entity: User) -> UserModel:

        if entity.id is None or entity.first_name is None or entity.last_name is None or entity.email is None:
            raise ValueError("For creating a new user, all fields except id and created_at should be empty or default.")

        return UserModel(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email.value,
            hashed_password=entity.hashed_password,
        )
