# app/domain/value_objects.py
from __future__ import annotations

import re
from dataclasses import dataclass

from ..exceptions import ValidationError

_PERM_RE = re.compile(r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*$")  # ex: users:read


@dataclass(frozen=True, slots=True)
class PermissionCode:
    value: str

    def __post_init__(self) -> None:
        v = self.value.strip()
        if not _PERM_RE.match(v):
            raise ValidationError(f"Permission code inválido: {self.value}. Esperado: recurso:acao (ex users:read)")
        object.__setattr__(self, "value", v)
