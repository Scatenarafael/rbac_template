"""add tenant delete cascades

Revision ID: 2c6d4f4a8f91
Revises: 7f6d1a2b3c4d
Create Date: 2026-04-07 23:59:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2c6d4f4a8f91"
down_revision: Union[str, Sequence[str], None] = "7f6d1a2b3c4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("user_tenants_fk_tenant_id_fkey", "user_tenants", type_="foreignkey")
    op.create_foreign_key(
        "user_tenants_fk_tenant_id_fkey",
        "user_tenants",
        "tenants",
        ["fk_tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("user_tenant_roles_fk_user_tenant_id_fkey", "user_tenant_roles", type_="foreignkey")
    op.create_foreign_key(
        "user_tenant_roles_fk_user_tenant_id_fkey",
        "user_tenant_roles",
        "user_tenants",
        ["fk_user_tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("link_user_tenant_requests_fk_tenant_id_fkey", "link_user_tenant_requests", type_="foreignkey")
    op.create_foreign_key(
        "link_user_tenant_requests_fk_tenant_id_fkey",
        "link_user_tenant_requests",
        "tenants",
        ["fk_tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("link_user_tenant_requests_fk_tenant_id_fkey", "link_user_tenant_requests", type_="foreignkey")
    op.create_foreign_key(
        "link_user_tenant_requests_fk_tenant_id_fkey",
        "link_user_tenant_requests",
        "tenants",
        ["fk_tenant_id"],
        ["id"],
    )

    op.drop_constraint("user_tenant_roles_fk_user_tenant_id_fkey", "user_tenant_roles", type_="foreignkey")
    op.create_foreign_key(
        "user_tenant_roles_fk_user_tenant_id_fkey",
        "user_tenant_roles",
        "user_tenants",
        ["fk_user_tenant_id"],
        ["id"],
    )

    op.drop_constraint("user_tenants_fk_tenant_id_fkey", "user_tenants", type_="foreignkey")
    op.create_foreign_key(
        "user_tenants_fk_tenant_id_fkey",
        "user_tenants",
        "tenants",
        ["fk_tenant_id"],
        ["id"],
    )
