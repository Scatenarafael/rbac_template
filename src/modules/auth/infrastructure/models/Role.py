# src/modules/auth/infrastructure/models/role.py

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlalchemy import Column, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from .Base import new_uuid

if TYPE_CHECKING:
    from .RolePermission import RolePermissionModel
    from .UserTenantRole import UserTenantRoleModel


class RoleModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "roles"
    __table_args__ = (UniqueConstraint("name", name="uq_roles_name"),)

    id: UUID = Field(default_factory=new_uuid, primary_key=True)
    name: str = Field(sa_column=Column(String(100), nullable=False, index=True))
    description: str | None = Field(default=None, sa_column=Column(String(255), nullable=True))

    user_tenant_roles: list["UserTenantRoleModel"] = Relationship(back_populates="role")
    role_permissions: list["RolePermissionModel"] = Relationship(back_populates="role")
