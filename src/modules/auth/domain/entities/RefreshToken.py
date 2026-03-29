from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RefreshToken:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    token_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    revoked: bool = False
    replaced_by: Optional[str] = None

    fk_user_id: uuid.UUID | None = None

    def revoke(self, *, replaced_by: str | None = None) -> None:
        self.revoked = True
        self.replaced_by = replaced_by

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return self.expires_at is not None and now >= self.expires_at
