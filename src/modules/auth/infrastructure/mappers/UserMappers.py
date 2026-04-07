from uuid import UUID

from src.modules.auth.domain.entities.User import User, UserWithTenantRoles
from src.modules.auth.infrastructure.mappers.UserTenantRoleMappers import UserTenantRoleDetailedMapper
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
            UserTenantRoleDetailedMapper.to_entity(user_tenant_role)
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
