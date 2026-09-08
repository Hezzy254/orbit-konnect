"""add network devices

Revision ID: 11dd4fb954a7
Revises: 98704f5f5124
Create Date: 2026-09-09 02:01:57.597331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "11dd4fb954a7"
down_revision: Union[str, Sequence[str], None] = "98704f5f5124"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "network_devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "vendor",
            sa.Enum(
                "MIKROTIK",
                "TP_LINK",
                "UBIQUITI",
                "OTHER",
                name="networkdevicevendor",
            ),
            nullable=False,
        ),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column(
            "device_type",
            sa.Enum(
                "ROUTER",
                "ACCESS_POINT",
                "CPE",
                "SWITCH",
                "OTHER",
                name="networkdevicetype",
            ),
            nullable=False,
        ),
        sa.Column("ip_address", sa.String(length=255), nullable=False),
        sa.Column("api_port", sa.Integer(), nullable=False),
        sa.Column(
            "connection_type",
            sa.Enum(
                "API",
                "API_SSL",
                "REST",
                "SNMP",
                name="networkdeviceconnectiontype",
            ),
            nullable=False,
        ),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("encrypted_password", sa.String(length=500), nullable=False),
        sa.Column("verify_tls", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "UNKNOWN",
                "ONLINE",
                "OFFLINE",
                "ERROR",
                name="networkdevicestatus",
            ),
            nullable=False,
        ),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_network_devices_company_id"),
        "network_devices",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_network_devices_device_type"),
        "network_devices",
        ["device_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_network_devices_id"),
        "network_devices",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_network_devices_last_seen"),
        "network_devices",
        ["last_seen"],
        unique=False,
    )
    op.create_index(
        op.f("ix_network_devices_status"),
        "network_devices",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_network_devices_vendor"),
        "network_devices",
        ["vendor"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_network_devices_vendor"),
        table_name="network_devices",
    )
    op.drop_index(
        op.f("ix_network_devices_status"),
        table_name="network_devices",
    )
    op.drop_index(
        op.f("ix_network_devices_last_seen"),
        table_name="network_devices",
    )
    op.drop_index(
        op.f("ix_network_devices_id"),
        table_name="network_devices",
    )
    op.drop_index(
        op.f("ix_network_devices_device_type"),
        table_name="network_devices",
    )
    op.drop_index(
        op.f("ix_network_devices_company_id"),
        table_name="network_devices",
    )
    op.drop_table("network_devices")