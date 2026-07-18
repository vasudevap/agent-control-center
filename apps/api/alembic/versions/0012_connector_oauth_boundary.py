"""Add connector OAuth boundary.

Revision ID: 0012_connector_oauth
Revises: 0011_run_lifecycle
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0012_connector_oauth"
down_revision: str | None = "0011_run_lifecycle"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "connector_types",
        sa.Column("connector_type", sa.String(length=80), primary_key=True),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("authentication_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("supported_operations", sa.JSON(), nullable=False),
        sa.Column("required_scopes", sa.JSON(), nullable=False),
        sa.Column("risk_by_operation", sa.JSON(), nullable=False),
        sa.Column("supports_health_check", sa.Boolean(), nullable=False),
        sa.Column("supports_revocation", sa.Boolean(), nullable=False),
        sa.Column("supports_refresh", sa.Boolean(), nullable=False),
        sa.Column("provider_docs_reference", sa.String(length=240), nullable=False),
        sa.Column("configuration_schema", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "connector_credential_references",
        sa.Column("credential_reference_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("connector_type", sa.String(length=80), nullable=False),
        sa.Column("reference_label", sa.String(length=160), nullable=False),
        sa.Column("key_version", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("last_rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["connector_type"], ["connector_types.connector_type"]),
    )
    op.create_table(
        "connector_connections",
        sa.Column("connection_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("connector_type", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("account_identifier", sa.String(length=320), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("granted_scopes", sa.JSON(), nullable=False),
        sa.Column("credential_reference_id", sa.String(length=64), nullable=False),
        sa.Column("health_status", sa.String(length=40), nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_health_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["connector_type"], ["connector_types.connector_type"]),
        sa.ForeignKeyConstraint(
            ["credential_reference_id"],
            ["connector_credential_references.credential_reference_id"],
        ),
        sa.UniqueConstraint(
            "owner_user_id",
            "connector_type",
            "account_identifier",
            name="uq_connector_owner_type_account",
        ),
    )
    op.create_index(
        "ix_connector_connections_status",
        "connector_connections",
        ["status"],
    )
    op.create_table(
        "connector_oauth_states",
        sa.Column("oauth_state_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("connector_type", sa.String(length=80), nullable=False),
        sa.Column("state_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("pkce_challenge", sa.String(length=128), nullable=False),
        sa.Column("redirect_uri", sa.String(length=500), nullable=False),
        sa.Column("requested_scopes", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["connector_type"], ["connector_types.connector_type"]),
    )


def downgrade() -> None:
    op.drop_table("connector_oauth_states")
    op.drop_index("ix_connector_connections_status", table_name="connector_connections")
    op.drop_table("connector_connections")
    op.drop_table("connector_credential_references")
    op.drop_table("connector_types")
