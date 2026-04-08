# src/modules/auth/infrastructure/models/user_tenant_role.py

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from .Base import new_uuid

if TYPE_CHECKING:
    from .Role import RoleModel
    from .UserTenant import UserTenantModel


class UserTenantRoleModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "user_tenant_roles"
    __table_args__ = (
        UniqueConstraint(
            "fk_user_tenant_id",
            "fk_role_id",
            name="uq_user_tenant_roles_user_tenant_role",
        ),
    )

    id: UUID = Field(default_factory=new_uuid, primary_key=True)
    fk_user_tenant_id: UUID = Field(
        foreign_key="user_tenants.id",
        ondelete="CASCADE",
        index=True,
        nullable=False,
    )
    fk_role_id: UUID = Field(
        foreign_key="roles.id",
        index=True,
        nullable=False,
    )

    user_tenant: "UserTenantModel" = Relationship(back_populates="user_tenant_roles")
    role: "RoleModel" = Relationship(back_populates="user_tenant_roles")
