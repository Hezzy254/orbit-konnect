"""add subscription model

Revision ID: 3e6dfa3d1eea
Revises: 6974f842ba7d
Create Date: 2026-09-03 14:19:02.071660

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3e6dfa3d1eea"
down_revision: Union[str, Sequence[str], None] = "6974f842ba7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create subscriptions table."""

    subscription_status = sa.Enum(
        "PENDING",
        "ACTIVE",
        "SUSPENDED",
        "EXPIRED",
        "CANCELLED",
        name="subscriptionstatus",
    )

    package_duration_unit = sa.Enum(
        "MINUTE",
        "HOUR",
        "DAY",
        "WEEK",
        "MONTH",
        name="packagedurationunit",
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            subscription_status,
            nullable=False,
        ),
        sa.Column("package_name", sa.String(length=100), nullable=False),
        sa.Column("download_speed_mbps", sa.Integer(), nullable=False),
        sa.Column("upload_speed_mbps", sa.Integer(), nullable=False),
        sa.Column("duration_value", sa.Integer(), nullable=False),
        sa.Column(
            "duration_unit",
            package_duration_unit,
            nullable=False,
        ),
        sa.Column(
            "price",
            sa.Numeric(precision=12, scale=3),
            nullable=False,
        ),
        sa.Column("start_at", sa.DateTime(), nullable=True),
        sa.Column("end_at", sa.DateTime(), nullable=True),
        sa.Column("auto_renew", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["package_id"],
            ["packages.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_subscriptions_id",
        "subscriptions",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_subscriptions_company_id",
        "subscriptions",
        ["company_id"],
        unique=False,
    )

    op.create_index(
        "ix_subscriptions_customer_id",
        "subscriptions",
        ["customer_id"],
        unique=False,
    )

    op.create_index(
        "ix_subscriptions_package_id",
        "subscriptions",
        ["package_id"],
        unique=False,
    )

    op.create_index(
        "ix_subscriptions_status",
        "subscriptions",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_subscriptions_start_at",
        "subscriptions",
        ["start_at"],
        unique=False,
    )

    op.create_index(
        "ix_subscriptions_end_at",
        "subscriptions",
        ["end_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove subscriptions table."""

    op.drop_index(
        "ix_subscriptions_end_at",
        table_name="subscriptions",
    )

    op.drop_index(
        "ix_subscriptions_start_at",
        table_name="subscriptions",
    )

    op.drop_index(
        "ix_subscriptions_status",
        table_name="subscriptions",
    )

    op.drop_index(
        "ix_subscriptions_package_id",
        table_name="subscriptions",
    )

    op.drop_index(
        "ix_subscriptions_customer_id",
        table_name="subscriptions",
    )

    op.drop_index(
        "ix_subscriptions_company_id",
        table_name="subscriptions",
    )

    op.drop_index(
        "ix_subscriptions_id",
        table_name="subscriptions",
    )

    op.drop_table("subscriptions")