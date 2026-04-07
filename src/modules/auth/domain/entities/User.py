from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Sequence

from src.modules.auth.domain.entities.Base import utcnow
from src.modules.auth.domain.entities.UserTenantRole import UserTenantRoleDetailed
from src.modules.auth.domain.value_objects.Emails import Email


@dataclass(slots=True, kw_only=True)
class User:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    first_name: str = ""
    last_name: str = ""
    email: Email
    hashed_password: str
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True, kw_only=True)
class UserWithTenantRoles:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    first_name: str = ""
    last_name: str = ""
    email: str
    user_tenant_roles: Sequence[UserTenantRoleDetailed]
