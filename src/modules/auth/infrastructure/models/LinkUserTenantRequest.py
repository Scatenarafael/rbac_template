# src/modules/auth/infrastructure/db/models/link_user_tenant_request.py

from datetime import datetime
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import (
    LinkUserTenantRequestStatus,
)

from .Base import new_uuid, utcnow

if TYPE_CHECKING:
    from .Tenant import TenantModel
    from .User import UserModel


class LinkUserTenantRequestModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "link_user_tenant_requests"
    __table_args__ = (
        UniqueConstraint(
            "fk_tenant_id",
            "fk_user_id",
            "status",
            name="uq_link_user_tenant_requests_tenant_user_status",
        ),
    )

    id: UUID = Field(default_factory=new_uuid, primary_key=True)

    fk_tenant_id: UUID = Field(
        foreign_key="tenants.id",
        ondelete="CASCADE",
        index=True,
        nullable=False,
    )
    fk_user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
    )

    status: LinkUserTenantRequestStatus = Field(
        default=LinkUserTenantRequestStatus.PENDING,
        sa_column=Column(
            SAEnum(
                LinkUserTenantRequestStatus,
                name="link_user_tenant_request_status",
                native_enum=False,
            ),
            nullable=False,
        ),
    )

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=utcnow),
    )

    tenant: "TenantModel" = Relationship(back_populates="link_user_tenant_requests")
    user: "UserModel" = Relationship(back_populates="link_user_tenant_requests")
