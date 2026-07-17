"""Add PostgreSQL queue foundation.

Revision ID: 0004_queue_foundation
Revises: 0003_external_client_identity
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_queue_foundation"
down_revision: str | None = "0003_external_client_identity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "queue_jobs",
        sa.Column("queue_job_id", sa.String(64), primary_key=True),
        sa.Column("job_type", sa.String(120), nullable=False),
        sa.Column("idempotency_key", sa.String(128)),
        sa.Column("state", sa.String(40), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("payload_metadata", sa.JSON(), nullable=False),
        sa.Column("resource_reference", sa.String(240)),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("leased_at", sa.DateTime(timezone=True)),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True)),
        sa.Column("lease_token", sa.String(128)),
        sa.Column("lease_owner_id", sa.String(120)),
        sa.Column("recovery_count", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.Column("last_error_code", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "job_type", "idempotency_key", name="uq_queue_job_idempotency"
        ),
    )
    op.create_index(
        "ix_queue_jobs_claim",
        "queue_jobs",
        ["state", "available_at", "priority", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_queue_jobs_claim", table_name="queue_jobs")
    op.drop_table("queue_jobs")
