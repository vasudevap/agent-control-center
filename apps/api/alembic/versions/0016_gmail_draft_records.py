"""Add Gmail draft records.

Revision ID: 0016_gmail_drafts
Revises: 0015_gmail_actions
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0016_gmail_drafts"
down_revision: str | None = "0015_gmail_actions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gmail_draft_records",
        sa.Column("gmail_draft_record_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("gmail_message_record_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("provider_message_reference", sa.String(length=160), nullable=False),
        sa.Column("provider_draft_reference", sa.String(length=160), nullable=False),
        sa.Column("scenario", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("subject_preview", sa.String(length=240), nullable=False),
        sa.Column("body_hash", sa.String(length=64), nullable=False),
        sa.Column("facts_used", sa.JSON(), nullable=False),
        sa.Column("evidence_summary", sa.JSON(), nullable=False),
        sa.Column("decision_context_manifest", sa.JSON(), nullable=False),
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
        sa.UniqueConstraint(
            "owner_user_id",
            "idempotency_key",
            name="uq_gmail_draft_owner_idempotency",
        ),
    )
    op.create_index(
        "ix_gmail_draft_records_status",
        "gmail_draft_records",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_gmail_draft_records_status",
        table_name="gmail_draft_records",
    )
    op.drop_table("gmail_draft_records")
