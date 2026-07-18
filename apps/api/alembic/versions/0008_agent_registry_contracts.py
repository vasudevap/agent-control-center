"""Add generic agent registry contracts.

Revision ID: 0008_agent_registry_contracts
Revises: 0007_observability_audit
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_agent_registry_contracts"
down_revision: str | None = "0007_observability_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_registrations",
        sa.Column("agent_id", sa.String(length=64), primary_key=True),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("descriptor_version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("risk_level", sa.String(length=40), nullable=False),
        sa.Column("capabilities", sa.JSON(), nullable=False),
        sa.Column("allowed_tools", sa.JSON(), nullable=False),
        sa.Column("required_connectors", sa.JSON(), nullable=False),
        sa.Column("configuration_schema_ref", sa.String(length=240), nullable=True),
        sa.Column("configuration_schema", sa.JSON(), nullable=False),
        sa.Column("supports_manual_run", sa.Boolean(), nullable=False),
        sa.Column("supports_scheduled_run", sa.Boolean(), nullable=False),
        sa.Column("health_status", sa.String(length=40), nullable=False),
        sa.Column("health_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug", name="uq_agent_registration_slug"),
    )
    op.create_index(
        "ix_agent_registrations_status",
        "agent_registrations",
        ["status"],
    )
    op.create_index(
        "ix_agent_registrations_health_status",
        "agent_registrations",
        ["health_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_registrations_health_status",
        table_name="agent_registrations",
    )
    op.drop_index("ix_agent_registrations_status", table_name="agent_registrations")
    op.drop_table("agent_registrations")
