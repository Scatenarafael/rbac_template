from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.modules.auth.domain.entities import LinkUserTenantRequest, RefreshToken, Role, Tenant
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestStatus
from src.modules.auth.domain.exceptions import ValidationError
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.domain.value_objects.Permissions import PermissionCode


def test_email_value_object_normalizes_and_validates_email():
    email = Email("  JOHN.DOE@EMAIL.COM  ")

    assert email.value == "john.doe@email.com"


def test_email_value_object_rejects_invalid_email():
    with pytest.raises(ValidationError, match="Email inválido"):
        Email("not-an-email")


def test_permission_code_accepts_resource_action_format():
    permission = PermissionCode("users:read")

    assert permission.value == "users:read"


def test_permission_code_rejects_invalid_format():
    with pytest.raises(ValidationError, match="Permission code inválido"):
        PermissionCode("users.read")


def test_tenant_normalizes_and_requires_name():
    tenant = Tenant(name="  Acme  ")

    assert tenant.name == "Acme"

    with pytest.raises(ValidationError, match="Tenant name cannot be empty"):
        Tenant(name="   ")


def test_role_normalizes_and_requires_name():
    role = Role(name=" TenantAdmin ")

    assert role.name == "tenantadmin"

    with pytest.raises(ValidationError, match="Role name cannot be empty"):
        Role(name="   ")


def test_refresh_token_revoke_and_expiration_helpers():
    token = RefreshToken(fk_user_id=uuid4(), expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))

    token.revoke(replaced_by="next-jti")

    assert token.revoked is True
    assert token.replaced_by == "next-jti"
    assert token.is_expired() is True


def test_link_user_tenant_request_approve_and_reject_only_pending_requests():
    approved_request = LinkUserTenantRequest(fk_tenant_id=uuid4(), fk_user_id=uuid4())
    approved_request.approve()

    assert approved_request.status == LinkUserTenantRequestStatus.APPROVED

    with pytest.raises(ValidationError, match="Only pending requests can be approved"):
        approved_request.approve()

    rejected_request = LinkUserTenantRequest(fk_tenant_id=uuid4(), fk_user_id=uuid4())
    rejected_request.reject()

    assert rejected_request.status == LinkUserTenantRequestStatus.REJECTED

    with pytest.raises(ValidationError, match="Only pending requests can be rejected"):
        rejected_request.reject()
