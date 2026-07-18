"""Add deterministic interval scheduler foundation.

Revision ID: 0005_scheduler_foundation
Revises: 0004_queue_foundation
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_scheduler_foundation"
down_revision: str | None = "0004_queue_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "job_schedules",
        sa.Column("job_schedule_id", sa.String(64), primary_key=True),
        sa.Column("job_type", sa.String(120), nullable=False),
        sa.Column("resource_reference", sa.String(240)),
        sa.Column("payload_metadata", sa.JSON(), nullable=False),
        sa.Column("interval_seconds", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("next_due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True)),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "interval_seconds >= 60 AND interval_seconds <= 2592000",
            name="ck_job_schedules_interval_seconds",
        ),
    )
    op.create_index(
        "ix_job_schedules_due",
        "job_schedules",
        ["enabled", "next_due_at"],
    )
    op.create_table(
        "schedule_occurrences",
        sa.Column("schedule_occurrence_id", sa.String(64), primary_key=True),
        sa.Column(
            "job_schedule_id",
            sa.String(64),
            sa.ForeignKey("job_schedules.job_schedule_id"),
            nullable=False,
        ),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "queue_job_id",
            sa.String(64),
            sa.ForeignKey("queue_jobs.queue_job_id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "job_schedule_id", "scheduled_for", name="uq_schedule_occurrence"
        ),
    )


def downgrade() -> None:
    op.drop_table("schedule_occurrences")
    op.drop_index("ix_job_schedules_due", table_name="job_schedules")
    op.drop_table("job_schedules")
