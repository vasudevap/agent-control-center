"""Add Gmail message retrieval and classification records.

Revision ID: 0013_gmail_messages
Revises: 0012_connector_oauth
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0013_gmail_messages"
down_revision: str | None = "0012_connector_oauth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gmail_message_records",
        sa.Column("gmail_message_record_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("provider_message_reference", sa.String(length=160), nullable=False),
        sa.Column("provider_thread_reference", sa.String(length=160), nullable=False),
        sa.Column("sender_address", sa.String(length=320), nullable=False),
        sa.Column("sender_domain", sa.String(length=160), nullable=False),
        sa.Column("subject_preview", sa.String(length=240), nullable=False),
        sa.Column("content_excerpt_hash", sa.String(length=64), nullable=False),
        sa.Column("attachment_metadata", sa.JSON(), nullable=False),
        sa.Column("label_names", sa.JSON(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("eligibility_reason", sa.String(length=120), nullable=False),
        sa.Column("classification_category", sa.String(length=80), nullable=False),
        sa.Column("classification_confidence", sa.Integer(), nullable=False),
        sa.Column("classification_status", sa.String(length=40), nullable=False),
        sa.Column("review_reason_code", sa.String(length=120), nullable=True),
        sa.Column("source_integrity_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["connector_connections.connection_id"],
        ),
        sa.UniqueConstraint(
            "owner_user_id",
            "connection_id",
            "provider_message_reference",
            name="uq_gmail_message_owner_connection_provider_ref",
        ),
    )
    op.create_index(
        "ix_gmail_message_records_classification",
        "gmail_message_records",
        ["classification_category"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_gmail_message_records_classification",
        table_name="gmail_message_records",
    )
    op.drop_table("gmail_message_records")
