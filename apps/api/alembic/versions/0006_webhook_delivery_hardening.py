"""Harden outbound webhook delivery records.

Revision ID: 0006_webhook_delivery_hardening
Revises: 0005_scheduler_foundation
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_webhook_delivery_hardening"
down_revision: str | None = "0005_scheduler_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "webhook_delivery_attempts", sa.Column("event_id", sa.String(64), nullable=True)
    )
    op.add_column(
        "webhook_delivery_attempts", sa.Column("key_id", sa.String(160), nullable=True)
    )
    op.execute(
        "UPDATE webhook_delivery_attempts SET event_id = webhook_delivery_attempt_id"
    )
    op.execute("UPDATE webhook_delivery_attempts SET key_id = 'legacy-unconfigured'")
    op.alter_column("webhook_delivery_attempts", "event_id", nullable=False)
    op.alter_column("webhook_delivery_attempts", "key_id", nullable=False)
    op.create_unique_constraint(
        "uq_webhook_delivery_event",
        "webhook_delivery_attempts",
        ["webhook_subscription_id", "event_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_webhook_delivery_event", "webhook_delivery_attempts", type_="unique"
    )
    op.drop_column("webhook_delivery_attempts", "key_id")
    op.drop_column("webhook_delivery_attempts", "event_id")
