"""Add Gmail clinical and PHI suppression guardrail.

Revision ID: 0014_gmail_suppression
Revises: 0013_gmail_messages
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0014_gmail_suppression"
down_revision: str | None = "0013_gmail_messages"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("gmail_message_records") as batch_op:
        batch_op.add_column(
            sa.Column(
                "suppression_status",
                sa.String(length=40),
                nullable=False,
                server_default="not_suppressed",
            ),
        )
        batch_op.add_column(
            sa.Column("suppression_reason_code", sa.String(length=120), nullable=True),
        )
        batch_op.add_column(
            sa.Column("manual_handling_id", sa.String(length=64), nullable=True),
        )
        batch_op.create_foreign_key(
            "fk_gmail_message_manual_handling",
            "manual_handling_records",
            ["manual_handling_id"],
            ["manual_handling_id"],
        )
        batch_op.create_index(
            "ix_gmail_message_records_suppression",
            ["suppression_status"],
        )
        batch_op.alter_column(
            "suppression_status",
            server_default=None,
        )


def downgrade() -> None:
    with op.batch_alter_table("gmail_message_records") as batch_op:
        batch_op.drop_index("ix_gmail_message_records_suppression")
        batch_op.drop_constraint(
            "fk_gmail_message_manual_handling",
            type_="foreignkey",
        )
        batch_op.drop_column("manual_handling_id")
        batch_op.drop_column("suppression_reason_code")
        batch_op.drop_column("suppression_status")
