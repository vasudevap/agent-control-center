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
    with op.batch_alter_table("webhook_delivery_attempts") as batch_op:
        batch_op.add_column(sa.Column("event_id", sa.String(64), nullable=True))
        batch_op.add_column(sa.Column("key_id", sa.String(160), nullable=True))
    op.execute(
        "UPDATE webhook_delivery_attempts SET event_id = webhook_delivery_attempt_id"
    )
    op.execute("UPDATE webhook_delivery_attempts SET key_id = 'legacy-unconfigured'")
    with op.batch_alter_table("webhook_delivery_attempts") as batch_op:
        batch_op.alter_column(
            "event_id",
            existing_type=sa.String(64),
            nullable=False,
        )
        batch_op.alter_column(
            "key_id",
            existing_type=sa.String(160),
            nullable=False,
        )
        batch_op.create_unique_constraint(
            "uq_webhook_delivery_event",
            ["webhook_subscription_id", "event_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("webhook_delivery_attempts") as batch_op:
        batch_op.drop_constraint("uq_webhook_delivery_event", type_="unique")
        batch_op.drop_column("key_id")
        batch_op.drop_column("event_id")
