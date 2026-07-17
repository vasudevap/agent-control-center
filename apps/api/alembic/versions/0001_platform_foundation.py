"""Create platform foundation tables.

Revision ID: 0001_platform_foundation
Revises:
Create Date: 2026-07-17
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_platform_foundation"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column[sa.DateTime]]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=64), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("identity_provider", sa.String(length=80), nullable=False),
        sa.Column("identity_subject", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        *timestamps(),
        sa.UniqueConstraint(
            "identity_provider",
            "identity_subject",
            name="uq_users_identity",
        ),
    )

    op.create_table(
        "external_product_clients",
        sa.Column("external_client_id", sa.String(length=64), primary_key=True),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column(
            "authentication_key_reference",
            sa.String(length=160),
            nullable=False,
        ),
        sa.Column("human_owner_user_id", sa.String(length=64), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["human_owner_user_id"], ["users.user_id"]),
    )

    op.create_table(
        "audit_events",
        sa.Column("audit_event_id", sa.String(length=64), primary_key=True),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("actor_type", sa.String(length=80), nullable=False),
        sa.Column("actor_id", sa.String(length=120), nullable=True),
        sa.Column("resource_type", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.String(length=120), nullable=True),
        sa.Column("correlation_id", sa.String(length=80), nullable=False),
        sa.Column("redaction_state", sa.String(length=40), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_audit_events_correlation_id",
        "audit_events",
        ["correlation_id"],
    )

    op.create_table(
        "webhook_subscriptions",
        sa.Column("webhook_subscription_id", sa.String(length=64), primary_key=True),
        sa.Column("external_client_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("target_url", sa.String(length=2048), nullable=False),
        sa.Column("secret_reference", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["external_client_id"],
            ["external_product_clients.external_client_id"],
        ),
    )

    op.create_table(
        "knowledge_facts",
        sa.Column("knowledge_fact_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("fact_key", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("classification", sa.String(length=40), nullable=False),
        sa.Column("current_revision_id", sa.String(length=64), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
        sa.UniqueConstraint("owner_user_id", "fact_key", name="uq_fact_owner_key"),
    )

    op.create_table(
        "knowledge_fact_revisions",
        sa.Column("knowledge_fact_revision_id", sa.String(length=64), primary_key=True),
        sa.Column("knowledge_fact_id", sa.String(length=64), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("display_value", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("source_reference", sa.String(length=240), nullable=True),
        sa.Column("provenance_summary", sa.Text(), nullable=False),
        sa.Column("is_volatile", sa.Boolean(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("prohibited_content_reason", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_fact_id"],
            ["knowledge_facts.knowledge_fact_id"],
        ),
        sa.UniqueConstraint(
            "knowledge_fact_id",
            "revision_number",
            name="uq_fact_revision_number",
        ),
    )

    op.create_table(
        "knowledge_questions",
        sa.Column("knowledge_question_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("required_fact_key", sa.String(length=160), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("source_reference", sa.String(length=240), nullable=True),
        sa.Column("correlation_id", sa.String(length=80), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
    )

    op.create_table(
        "knowledge_answers",
        sa.Column("knowledge_answer_id", sa.String(length=64), primary_key=True),
        sa.Column("knowledge_question_id", sa.String(length=64), nullable=False),
        sa.Column("answered_by_user_id", sa.String(length=64), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("validation_status", sa.String(length=40), nullable=False),
        sa.Column("rejected_reason", sa.String(length=80), nullable=True),
        sa.Column("created_fact_revision_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_question_id"],
            ["knowledge_questions.knowledge_question_id"],
        ),
        sa.ForeignKeyConstraint(["answered_by_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(
            ["created_fact_revision_id"],
            ["knowledge_fact_revisions.knowledge_fact_revision_id"],
        ),
        sa.UniqueConstraint(
            "knowledge_question_id",
            name="uq_answer_question",
        ),
    )

    op.create_table(
        "webhook_delivery_attempts",
        sa.Column(
            "webhook_delivery_attempt_id",
            sa.String(length=64),
            primary_key=True,
        ),
        sa.Column("webhook_subscription_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("payload_summary", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(length=80), nullable=True),
        sa.Column("correlation_id", sa.String(length=80), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["webhook_subscription_id"],
            ["webhook_subscriptions.webhook_subscription_id"],
        ),
    )
    op.create_index(
        "ix_webhook_delivery_attempts_status",
        "webhook_delivery_attempts",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_webhook_delivery_attempts_status",
        table_name="webhook_delivery_attempts",
    )
    op.drop_table("webhook_delivery_attempts")
    op.drop_table("knowledge_answers")
    op.drop_table("knowledge_questions")
    op.drop_table("knowledge_fact_revisions")
    op.drop_table("knowledge_facts")
    op.drop_table("webhook_subscriptions")
    op.drop_index("ix_audit_events_correlation_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("external_product_clients")
    op.drop_table("users")
