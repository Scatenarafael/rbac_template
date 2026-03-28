# app/domain/value_objects.py
from __future__ import annotations

import re
from dataclasses import dataclass

from ..exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")  # simples e suficiente p/ domínio


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        v = self.value.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValidationError(f"Email inválido: {self.value}")
        object.__setattr__(self, "value", v)
