# src/modules/auth/infrastructure/models/user.py

from datetime import datetime
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from src.modules.auth.infrastructure.models.RefreshToken import RefreshTokenModel

from .Base import new_uuid, utcnow

if TYPE_CHECKING:
    from .LinkUserTenantRequest import LinkUserTenantRequestModel
    from .UserTenant import UserTenantModel


class UserModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: UUID = Field(default_factory=new_uuid, primary_key=True)
    first_name: str = Field(sa_column=Column(String(100), nullable=False))
    last_name: str = Field(sa_column=Column(String(100), nullable=False))
    email: str = Field(sa_column=Column(String(255), nullable=False, index=True))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=utcnow),
    )

    user_tenants: list["UserTenantModel"] = Relationship(back_populates="user")
    link_user_tenant_requests: list["LinkUserTenantRequestModel"] = Relationship(back_populates="user")
    refresh_tokens: list["RefreshTokenModel"] = Relationship(back_populates="user")
