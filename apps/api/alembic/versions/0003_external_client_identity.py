"""Add external request nonce persistence.

Revision ID: 0003_external_client_identity
Revises: 0002_owner_sessions
Create Date: 2026-07-17
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_external_client_identity"
down_revision: str | None = "0002_owner_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "external_request_nonces",
        sa.Column("external_request_nonce_id", sa.String(length=64), primary_key=True),
        sa.Column("external_client_id", sa.String(length=64), nullable=False),
        sa.Column("key_id", sa.String(length=160), nullable=False),
        sa.Column("nonce", sa.String(length=160), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "external_client_id", "key_id", "nonce", name="uq_external_request_nonce"
        ),
    )
    op.create_index(
        "ix_external_request_nonces_expires_at",
        "external_request_nonces",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_external_request_nonces_expires_at",
        table_name="external_request_nonces",
    )
    op.drop_table("external_request_nonces")
