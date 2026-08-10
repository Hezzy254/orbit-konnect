"""add customer company uniqueness constraints

Revision ID: 9fe73c9f5947
Revises: baa5b1cecbe9
Create Date: 2026-08-10 03:49:13.743235
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9fe73c9f5947"
down_revision: Union[str, Sequence[str], None] = "baa5b1cecbe9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""

    with op.batch_alter_table("customers") as batch_op:
        batch_op.create_unique_constraint(
            "uq_customer_company_email",
            ["company_id", "email"],
        )

        batch_op.create_unique_constraint(
            "uq_customer_company_phone",
            ["company_id", "phone"],
        )


def downgrade() -> None:
    """Downgrade database schema."""

    with op.batch_alter_table("customers") as batch_op:
        batch_op.drop_constraint(
            "uq_customer_company_phone",
            type_="unique",
        )

        batch_op.drop_constraint(
            "uq_customer_company_email",
            type_="unique",
        )