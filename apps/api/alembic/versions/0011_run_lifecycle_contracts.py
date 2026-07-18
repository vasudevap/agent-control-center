"""Add run lifecycle contracts.

Revision ID: 0011_run_lifecycle
Revises: 0010_approval_manual_handling
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0011_run_lifecycle"
down_revision: str | None = "0010_approval_manual_handling"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_runs",
        sa.Column("run_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("trigger_source", sa.String(length=40), nullable=False),
        sa.Column("correlation_id", sa.String(length=80), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("queue_job_id", sa.String(length=64), nullable=True),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("failure_reason_code", sa.String(length=120), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["agent_id"], ["agent_registrations.agent_id"]),
        sa.UniqueConstraint(
            "owner_user_id",
            "idempotency_key",
            name="uq_run_idempotency",
        ),
    )
    op.create_index("ix_agent_runs_status", "agent_runs", ["status"])
    op.create_table(
        "agent_run_steps",
        sa.Column("run_step_id", sa.String(length=64), primary_key=True),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("step_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_runs.run_id"]),
    )


def downgrade() -> None:
    op.drop_table("agent_run_steps")
    op.drop_index("ix_agent_runs_status", table_name="agent_runs")
    op.drop_table("agent_runs")
