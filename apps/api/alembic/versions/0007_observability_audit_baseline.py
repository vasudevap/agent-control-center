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
    op.alter_column("audit_events", "channel", server_default=None)
    op.alter_column("audit_events", "action", server_default=None)
    op.alter_column("audit_events", "result", server_default=None)


def downgrade() -> None:
    op.drop_column("audit_events", "reason_code")
    op.drop_column("audit_events", "result")
    op.drop_column("audit_events", "action")
    op.drop_column("audit_events", "channel")
