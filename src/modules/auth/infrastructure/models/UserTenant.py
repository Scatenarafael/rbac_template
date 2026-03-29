# src/modules/auth/infrastructure/models/user_tenant.py

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from .Base import new_uuid

if TYPE_CHECKING:
    from .Tenant import TenantModel
    from .User import UserModel
    from .UserTenantRole import UserTenantRoleModel


class UserTenantModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "user_tenants"
    __table_args__ = (UniqueConstraint("fk_user_id", "fk_tenant_id", name="uq_user_tenants_user_tenant"),)

    id: UUID = Field(default_factory=new_uuid, primary_key=True)
    fk_user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    fk_tenant_id: UUID = Field(foreign_key="tenants.id", index=True, nullable=False)

    user: "UserModel" = Relationship(back_populates="user_tenants")
    tenant: "TenantModel" = Relationship(back_populates="user_tenants")
    user_tenant_roles: list["UserTenantRoleModel"] = Relationship(back_populates="user_tenant")
