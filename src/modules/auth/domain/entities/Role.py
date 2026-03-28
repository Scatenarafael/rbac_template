from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from ..exceptions import ValidationError
from .Base import new_uuid


@dataclass(slots=True, kw_only=True)
class Role:
    id: UUID = field(default_factory=new_uuid)
    name: str
    description: str | None = None

    def __post_init__(self) -> None:
        self.name = self.name.strip().lower()
        if not self.name:
            raise ValidationError("Role name cannot be empty.")
