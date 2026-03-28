from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from ..exceptions import ValidationError
from .Base import new_uuid, utcnow


@dataclass(slots=True, kw_only=True)
class Tenant:
    id: UUID = field(default_factory=new_uuid)
    name: str
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValidationError("Tenant name cannot be empty.")
