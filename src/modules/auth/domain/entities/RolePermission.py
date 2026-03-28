from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, kw_only=True, frozen=True)
class RolePermission:
    id: UUID
    fk_role_id: UUID
    fk_permission_id: UUID
