# src/modules/auth/infrastructure/models/tenant.py

from datetime import datetime
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from .Base import new_uuid, utcnow

if TYPE_CHECKING:
    from .LinkUserTenantRequest import LinkUserTenantRequestModel
    from .UserTenant import UserTenantModel


class TenantModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "tenants"
    __table_args__ = (UniqueConstraint("name", name="uq_tenants_name"),)

    id: UUID = Field(default_factory=new_uuid, primary_key=True)
    name: str = Field(sa_column=Column(String(120), nullable=False, index=True))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=utcnow),
    )

    user_tenants: list["UserTenantModel"] = Relationship(back_populates="tenant")
    link_user_tenant_requests: list["LinkUserTenantRequestModel"] = Relationship(back_populates="tenant")
