from __future__ import annotations

from enum import Enum


class LinkUserTenantRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
