# src/modules/auth/domain/entities/link_user_tenant_request.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import (
    LinkUserTenantRequestStatus,
    LinkUserTenantRequestType,
)
from src.modules.auth.domain.exceptions import ValidationError

from .Base import new_uuid, utcnow


@dataclass(slots=True, kw_only=True)
class UserToLinkUserTenantRequestList:
    id: UUID
    first_name: str
    last_name: str
    email: str


@dataclass(slots=True, kw_only=True)
class LinkUserTenantRequest:
    id: UUID = field(default_factory=new_uuid)
    fk_tenant_id: UUID
    fk_user_id: UUID
    status: LinkUserTenantRequestStatus = LinkUserTenantRequestStatus.PENDING
    type: LinkUserTenantRequestType = LinkUserTenantRequestType.REQUEST_ENTRY
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.fk_tenant_id == self.fk_user_id:
            # tecnicamente são domínios diferentes, então essa checagem
            # não é obrigatória. Pode remover se preferir.
            pass

    def approve(self) -> None:
        if self.status != LinkUserTenantRequestStatus.PENDING:
            raise ValidationError("Only pending requests can be approved.")
        self.status = LinkUserTenantRequestStatus.APPROVED
        self.updated_at = utcnow()

    def reject(self) -> None:
        if self.status != LinkUserTenantRequestStatus.PENDING:
            raise ValidationError("Only pending requests can be rejected.")
        self.status = LinkUserTenantRequestStatus.REJECTED
        self.updated_at = utcnow()


@dataclass(slots=True, kw_only=True)
class LinkUserTenantRequestDetailed:
    id: UUID = field(default_factory=new_uuid)
    user: UserToLinkUserTenantRequestList
    status: LinkUserTenantRequestStatus
    updated_at: datetime = field(default_factory=utcnow)
