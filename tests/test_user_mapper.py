from uuid import uuid4

from src.modules.auth.infrastructure.mappers.UserMappers import UserMapper
from src.modules.auth.infrastructure.models.Role import RoleModel
from src.modules.auth.infrastructure.models.User import UserModel
from src.modules.auth.infrastructure.models.UserTenant import UserTenantModel
from src.modules.auth.infrastructure.models.UserTenantRole import UserTenantRoleModel


def test_user_mapper_to_entity_with_tenant_roles_flattens_roles_from_all_tenants():
    user_id = uuid4()
    first_user_tenant_id = uuid4()
    second_user_tenant_id = uuid4()

    admin_role = RoleModel(id=uuid4(), name="tenantadmin", description=None)
    member_role = RoleModel(id=uuid4(), name="member", description="Default role")

    first_user_tenant_role = UserTenantRoleModel(
        id=uuid4(),
        fk_user_tenant_id=first_user_tenant_id,
        fk_role_id=admin_role.id,
        role=admin_role,
    )
    second_user_tenant_role = UserTenantRoleModel(
        id=uuid4(),
        fk_user_tenant_id=second_user_tenant_id,
        fk_role_id=member_role.id,
        role=member_role,
    )

    user = UserModel(
        id=user_id,
        first_name="John",
        last_name="Doe",
        email="john.doe@email.com",
        hashed_password="hashed-password",
        user_tenants=[
            UserTenantModel(
                id=first_user_tenant_id,
                fk_user_id=user_id,
                fk_tenant_id=uuid4(),
                user_tenant_roles=[first_user_tenant_role],
            ),
            UserTenantModel(
                id=second_user_tenant_id,
                fk_user_id=user_id,
                fk_tenant_id=uuid4(),
                user_tenant_roles=[second_user_tenant_role],
            ),
        ],
    )

    result = UserMapper.to_entity_with_tenant_roles(user)

    assert result.id == user_id
    assert result.email == "john.doe@email.com"
    assert len(result.user_tenant_roles) == 2
    assert result.user_tenant_roles[0].role.name == "tenantadmin"
    assert result.user_tenant_roles[0].role.description is None
    assert result.user_tenant_roles[1].role.name == "member"
