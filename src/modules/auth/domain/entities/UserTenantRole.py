from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from src.modules.auth.domain.entities.Role import Role
from src.modules.auth.domain.entities.Tenant import Tenant

from .Base import new_uuid


@dataclass(slots=True, kw_only=True)
class UserTenantRole:
    id: UUID = field(default_factory=new_uuid)
    fk_user_tenant_id: UUID
    fk_role_id: UUID


@dataclass(slots=True, kw_only=True)
class UserTenantRoleDetailed(UserTenantRole):
    id: UUID = field(default_factory=new_uuid)
    fk_user_tenant_id: UUID
    tenant: Tenant | None = None
    role: Role
