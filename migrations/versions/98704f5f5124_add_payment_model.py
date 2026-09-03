"""add payment model

Revision ID: 98704f5f5124
Revises: 3e6dfa3d1eea
Create Date: 2026-09-03 22:01:48.564476

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "98704f5f5124"
down_revision: Union[str, Sequence[str], None] = "3e6dfa3d1eea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the payments table."""

    payment_method = sa.Enum(
        "CASH",
        "BANK_TRANSFER",
        "CARD",
        "MOBILE_MONEY",
        "QR_CODE",
        "ONLINE_GATEWAY",
        name="paymentmethod",
    )

    payment_status = sa.Enum(
        "PENDING",
        "SUCCESS",
        "FAILED",
        "CANCELLED",
        name="paymentstatus",
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("subscription_id", sa.Integer(), nullable=False),
        sa.Column(
            "amount",
            sa.Numeric(precision=12, scale=3),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
        ),
        sa.Column(
            "payment_method",
            payment_method,
            nullable=False,
        ),
        sa.Column(
            "provider",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "status",
            payment_status,
            nullable=False,
        ),
        sa.Column(
            "transaction_reference",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "provider_reference",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "paid_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "failure_reason",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id",
            "provider",
            "provider_reference",
            name="uq_payment_company_provider_reference",
        ),
    )

    op.create_index(
        "ix_payments_id",
        "payments",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_payments_company_id",
        "payments",
        ["company_id"],
        unique=False,
    )

    op.create_index(
        "ix_payments_customer_id",
        "payments",
        ["customer_id"],
        unique=False,
    )

    op.create_index(
        "ix_payments_subscription_id",
        "payments",
        ["subscription_id"],
        unique=False,
    )

    op.create_index(
        "ix_payments_payment_method",
        "payments",
        ["payment_method"],
        unique=False,
    )

    op.create_index(
        "ix_payments_status",
        "payments",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_payments_provider_reference",
        "payments",
        ["provider_reference"],
        unique=False,
    )

    op.create_index(
        "ix_payments_paid_at",
        "payments",
        ["paid_at"],
        unique=False,
    )

    op.create_index(
        "ix_payments_transaction_reference",
        "payments",
        ["transaction_reference"],
        unique=True,
    )


def downgrade() -> None:
    """Remove the payments table."""

    op.drop_index(
        "ix_payments_transaction_reference",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_paid_at",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_provider_reference",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_status",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_payment_method",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_subscription_id",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_customer_id",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_company_id",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_id",
        table_name="payments",
    )

    op.drop_table("payments")