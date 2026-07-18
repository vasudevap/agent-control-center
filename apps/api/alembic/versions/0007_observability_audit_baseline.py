"""Add observability audit baseline fields.

Revision ID: 0007_observability_audit
Revises: 0006_webhook_delivery_hardening
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_observability_audit"
down_revision: str | None = "0006_webhook_delivery_hardening"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "audit_events",
        sa.Column(
            "channel",
            sa.String(length=80),
            nullable=False,
            server_default="service",
        ),
    )
    op.add_column(
        "audit_events",
        sa.Column(
            "action",
            sa.String(length=120),
            nullable=False,
            server_default="unspecified",
        ),
    )
    op.add_column(
        "audit_events",
        sa.Column(
            "result",
            sa.String(length=40),
            nullable=False,
            server_default="unknown",
        ),
    )
    op.add_column(
        "audit_events",
        sa.Column("reason_code", sa.String(length=120), nullable=True),
    )
    with op.batch_alter_table("audit_events") as batch_op:
        batch_op.alter_column(
            "channel",
            existing_type=sa.String(length=80),
            server_default=None,
        )
        batch_op.alter_column(
            "action",
            existing_type=sa.String(length=120),
            server_default=None,
        )
        batch_op.alter_column(
            "result",
            existing_type=sa.String(length=40),
            server_default=None,
        )


def downgrade() -> None:
    op.drop_column("audit_events", "reason_code")
    op.drop_column("audit_events", "result")
    op.drop_column("audit_events", "action")
    op.drop_column("audit_events", "channel")
