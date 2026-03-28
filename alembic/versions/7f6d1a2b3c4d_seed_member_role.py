"""seed default roles

Revision ID: 7f6d1a2b3c4d
Revises: 4a534f31fb13
Create Date: 2026-03-27 00:40:00.000000

"""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f6d1a2b3c4d"
down_revision: Union[str, Sequence[str], None] = "374a0d5cbd39"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLES = (
    {
        "name": "sysadmin",
        "description": "System-wide administrative role.",
    },
    {
        "name": "member",
        "description": "Default role for new user-tenant links.",
    },
    {
        "name": "tenantadmin",
        "description": "Administrative role for new user-tenant links.",
    },
)


def upgrade() -> None:
    """Seed the default roles."""
    roles = sa.table(
        "roles",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String(length=100)),
        sa.column("description", sa.String(length=255)),
    )

    connection = op.get_bind()
    for role in ROLES:
        existing_role = connection.execute(sa.select(roles.c.id).where(roles.c.name == role["name"])).scalar_one_or_none()

        if existing_role is None:
            connection.execute(
                sa.insert(roles).values(
                    id=uuid4(),
                    name=role["name"],
                    description=role["description"],
                )
            )


def downgrade() -> None:
    """Remove the seeded roles."""
    roles = sa.table(
        "roles",
        sa.column("name", sa.String(length=100)),
    )

    connection = op.get_bind()
    connection.execute(sa.delete(roles).where(roles.c.name.in_(tuple(role["name"] for role in ROLES))))
