"""update package model

Revision ID: 6974f842ba7d
Revises: 9fe73c9f5947
Create Date: 2026-09-02 03:19:33.228397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6974f842ba7d"
down_revision: Union[str, Sequence[str], None] = "9fe73c9f5947"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade packages table to the new package model."""

    with op.batch_alter_table("packages", recreate="always") as batch_op:
        batch_op.drop_column("duration_days")

        batch_op.alter_column(
            "price",
            existing_type=sa.FLOAT(),
            type_=sa.Numeric(precision=12, scale=3),
            existing_nullable=False,
        )

        batch_op.create_index(
            "ix_packages_company_id",
            ["company_id"],
            unique=False,
        )

        batch_op.create_unique_constraint(
            "uq_package_company_name",
            ["company_id", "name"],
        )


def downgrade() -> None:
    """
    Downgrade to the previous package model.

    The previous model only supports duration in whole days.
    Therefore, downgrade is allowed only when every package uses
    DAY as its duration unit. Otherwise, the downgrade is aborted
    to prevent silent loss or corruption of duration information.
    """

    connection = op.get_bind()

    incompatible_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM packages
            WHERE duration_unit != 'DAY'
            """
        )
    ).scalar_one()

    if incompatible_count:
        raise RuntimeError(
            "Cannot downgrade package model because one or more packages "
            "use a duration unit other than DAY. Downgrade would lose "
            "duration information."
        )

    with op.batch_alter_table("packages", recreate="always") as batch_op:
        batch_op.add_column(
            sa.Column(
                "duration_days",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.drop_constraint(
            "uq_package_company_name",
            type_="unique",
        )

        batch_op.drop_index(
            "ix_packages_company_id",
        )

        batch_op.alter_column(
            "price",
            existing_type=sa.Numeric(precision=12, scale=3),
            type_=sa.FLOAT(),
            existing_nullable=False,
        )

        batch_op.drop_column("duration_unit")
        batch_op.drop_column("duration_value")