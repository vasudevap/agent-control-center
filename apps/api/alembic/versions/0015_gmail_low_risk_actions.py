"""Add Gmail low-risk action operation records.

Revision ID: 0015_gmail_actions
Revises: 0014_gmail_suppression
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0015_gmail_actions"
down_revision: str | None = "0014_gmail_suppression"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gmail_action_operations",
        sa.Column("gmail_action_operation_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("gmail_message_record_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("drive_connection_id", sa.String(length=64), nullable=True),
        sa.Column("operation_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("provider_operation_reference", sa.String(length=160), nullable=True),
        sa.Column("provider_message_reference", sa.String(length=160), nullable=False),
        sa.Column(
            "provider_attachment_reference",
            sa.String(length=160),
            nullable=True,
        ),
        sa.Column("target_reference", sa.String(length=240), nullable=True),
        sa.Column("reason_code", sa.String(length=120), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(
            ["gmail_message_record_id"],
            ["gmail_message_records.gmail_message_record_id"],
        ),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["connector_connections.connection_id"],
        ),
        sa.ForeignKeyConstraint(
            ["drive_connection_id"],
            ["connector_connections.connection_id"],
        ),
        sa.UniqueConstraint(
            "owner_user_id",
            "operation_type",
            "idempotency_key",
            name="uq_gmail_action_owner_operation_idempotency",
        ),
    )
    op.create_index(
        "ix_gmail_action_operations_status",
        "gmail_action_operations",
        ["status"],
    )
    op.create_index(
        "ix_gmail_action_operations_message",
        "gmail_action_operations",
        ["gmail_message_record_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_gmail_action_operations_message",
        table_name="gmail_action_operations",
    )
    op.drop_index(
        "ix_gmail_action_operations_status",
        table_name="gmail_action_operations",
    )
    op.drop_table("gmail_action_operations")
