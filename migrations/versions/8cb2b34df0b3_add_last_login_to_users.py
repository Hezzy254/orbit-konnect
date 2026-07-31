"""add_last_login_to_users

Revision ID: 8cb2b34df0b3
Revises: 0e7c97d9b64c
Create Date: 2026-07-31 03:18:16.838753

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8cb2b34df0b3"
down_revision: Union[str, Sequence[str], None] = "0e7c97d9b64c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add last_login column to users table."""

    op.add_column(
        "users",
        sa.Column(
            "last_login",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove last_login column from users table."""

    op.drop_column("users", "last_login")