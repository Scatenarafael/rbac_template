from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from .Base import new_uuid


@dataclass(slots=True, kw_only=True)
class UserTenantRole:
    id: UUID = field(default_factory=new_uuid)
    fk_user_tenant_id: UUID
    fk_role_id: UUID
