"""Add approval and manual-handling contracts.

Revision ID: 0010_approval_manual_handling
Revises: 0009_knowledge_fact_contracts
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0010_approval_manual_handling"
down_revision: str | None = "0009_knowledge_fact_contracts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "approval_requests",
        sa.Column("approval_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=True),
        sa.Column("run_id", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.String(length=120), nullable=False),
        sa.Column("action_reference", sa.String(length=160), nullable=False),
        sa.Column("action_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("evidence_summary", sa.JSON(), nullable=False),
        sa.Column("decision_context_manifest", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_channel", sa.String(length=40), nullable=True),
        sa.Column("external_client_id", sa.String(length=64), nullable=True),
        sa.Column("reviewer_user_id", sa.String(length=64), nullable=True),
        sa.Column("superseded_by_approval_id", sa.String(length=64), nullable=True),
        sa.Column("continuation_status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
    )
    op.create_index("ix_approval_requests_status", "approval_requests", ["status"])
    op.create_table(
        "approval_decisions",
        sa.Column("approval_decision_id", sa.String(length=64), primary_key=True),
        sa.Column("approval_id", sa.String(length=64), nullable=False),
        sa.Column("decision", sa.String(length=40), nullable=False),
        sa.Column("submitted_revision", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=40), nullable=False),
        sa.Column("external_client_id", sa.String(length=64), nullable=True),
        sa.Column("reviewer_user_id", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("edited_action_payload_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["approval_id"], ["approval_requests.approval_id"]),
    )
    op.create_table(
        "manual_handling_records",
        sa.Column("manual_handling_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=True),
        sa.Column("run_id", sa.String(length=64), nullable=True),
        sa.Column("source_reference", sa.String(length=240), nullable=False),
        sa.Column("reason_category", sa.String(length=80), nullable=False),
        sa.Column("sensitivity_classification", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("held_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
    )
    op.create_index(
        "ix_manual_handling_records_status",
        "manual_handling_records",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_manual_handling_records_status",
        table_name="manual_handling_records",
    )
    op.drop_table("manual_handling_records")
    op.drop_table("approval_decisions")
    op.drop_index("ix_approval_requests_status", table_name="approval_requests")
    op.drop_table("approval_requests")
