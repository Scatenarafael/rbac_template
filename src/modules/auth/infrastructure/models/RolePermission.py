# src/modules/auth/infrastructure/models/role_permission.py

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from .Base import new_uuid

if TYPE_CHECKING:
    from .Permission import PermissionModel
    from .Role import RoleModel


class RolePermissionModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "role_permissions"
    __table_args__ = (
        UniqueConstraint(
            "fk_role_id",
            "fk_permission_id",
            name="uq_role_permissions_role_permission",
        ),
    )

    id: UUID = Field(default_factory=new_uuid, primary_key=True)
    fk_role_id: UUID = Field(foreign_key="roles.id", index=True, nullable=False)
    fk_permission_id: UUID = Field(
        foreign_key="permissions.id",
        index=True,
        nullable=False,
    )

    role: "RoleModel" = Relationship(back_populates="role_permissions")
    permission: "PermissionModel" = Relationship(back_populates="role_permissions")
