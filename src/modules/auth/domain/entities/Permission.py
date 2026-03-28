from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from src.modules.auth.domain.value_objects.Permissions import PermissionCode

from .Base import new_uuid


@dataclass(slots=True, kw_only=True)
class Permission:
    id: UUID = field(default_factory=new_uuid)
    code: PermissionCode
    description: str | None = None
