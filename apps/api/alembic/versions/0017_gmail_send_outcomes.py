"""Add Gmail send outcome records.

Revision ID: 0017_gmail_send_outcomes
Revises: 0016_gmail_drafts
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0017_gmail_send_outcomes"
down_revision: str | None = "0016_gmail_drafts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gmail_send_outcome_records",
        sa.Column("gmail_send_outcome_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("approval_id", sa.String(length=64), nullable=False),
        sa.Column("gmail_draft_record_id", sa.String(length=64), nullable=False),
        sa.Column("provider_draft_reference", sa.String(length=160), nullable=False),
        sa.Column("provider_send_reference", sa.String(length=160), nullable=True),
        sa.Column("outcome", sa.String(length=40), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("reason_code", sa.String(length=120), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["approval_id"], ["approval_requests.approval_id"]),
        sa.ForeignKeyConstraint(
            ["gmail_draft_record_id"],
            ["gmail_draft_records.gmail_draft_record_id"],
        ),
        sa.UniqueConstraint(
            "owner_user_id",
            "idempotency_key",
            name="uq_gmail_send_owner_idempotency",
        ),
    )
    op.create_index(
        "ix_gmail_send_outcome_records_outcome",
        "gmail_send_outcome_records",
        ["outcome"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_gmail_send_outcome_records_outcome",
        table_name="gmail_send_outcome_records",
    )
    op.drop_table("gmail_send_outcome_records")
