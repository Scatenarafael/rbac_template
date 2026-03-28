# src/modules/auth/infrastructure/models/permission.py

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlalchemy import Column, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from .Base import new_uuid

if TYPE_CHECKING:
    from .RolePermission import RolePermissionModel


class PermissionModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "permissions"
    __table_args__ = (UniqueConstraint("code", name="uq_permissions_code"),)

    id: UUID = Field(default_factory=new_uuid, primary_key=True)
    code: str = Field(sa_column=Column(String(100), nullable=False, index=True))
    description: str | None = Field(default=None, sa_column=Column(String(255), nullable=True))

    role_permissions: list["RolePermissionModel"] = Relationship(back_populates="permission")
