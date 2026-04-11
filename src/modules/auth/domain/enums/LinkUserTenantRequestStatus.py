from __future__ import annotations

from enum import Enum


class LinkUserTenantRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LinkUserTenantRequestType(str, Enum):
    INVITE = "invite"
    REQUEST_ENTRY = "request_entry"
