"""Add governed knowledge fact contract fields.

Revision ID: 0009_knowledge_fact_contracts
Revises: 0008_agent_registry_contracts
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009_knowledge_fact_contracts"
down_revision: str | None = "0008_agent_registry_contracts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "knowledge_facts",
        sa.Column("last_confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "api_idempotency_records",
        sa.Column(
            "api_idempotency_record_id",
            sa.String(length=64),
            primary_key=True,
        ),
        sa.Column("actor_id", sa.String(length=120), nullable=False),
        sa.Column("operation", sa.String(length=120), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "actor_id",
            "operation",
            "idempotency_key",
            name="uq_api_idempotency_actor_operation_key",
        ),
    )
    op.create_index(
        "ix_knowledge_facts_status",
        "knowledge_facts",
        ["status"],
    )
    op.create_index(
        "ix_knowledge_facts_last_confirmed_at",
        "knowledge_facts",
        ["last_confirmed_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_facts_last_confirmed_at",
        table_name="knowledge_facts",
    )
    op.drop_index("ix_knowledge_facts_status", table_name="knowledge_facts")
    op.drop_table("api_idempotency_records")
    op.drop_column("knowledge_facts", "last_confirmed_at")
