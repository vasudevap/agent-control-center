"""Add Agent Visibility lifecycle MVP schema.

Revision ID: 0018_agent_visibility_lifecycle_mvp
Revises: 0017_gmail_send_outcomes
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0018_agent_visibility_lifecycle_mvp"
down_revision: str | None = "0017_gmail_send_outcomes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _expand_alembic_version_identifier()
    _extend_agent_registrations()
    _backfill_agent_registration_visibility()
    _add_agent_registration_constraints_and_indexes()
    _create_agent_visibility_tables()


def downgrade() -> None:
    op.drop_table("agent_ingestion_rate_limits")
    op.drop_index(
        "ix_agent_activity_events_agent_occurred",
        table_name="agent_activity_events",
    )
    op.drop_index(
        "ix_agent_activity_events_occurred",
        table_name="agent_activity_events",
    )
    op.drop_table("agent_activity_events")
    op.drop_index("uq_agent_alerts_active_condition", table_name="agent_alerts")
    op.drop_index("ix_agent_alerts_last_seen", table_name="agent_alerts")
    op.drop_index("ix_agent_alerts_agent_status", table_name="agent_alerts")
    op.drop_table("agent_alerts")
    op.drop_table("agent_health_evaluator_leases")
    op.drop_index("ix_agent_executions_last_reported", table_name="agent_executions")
    op.drop_index("ix_agent_executions_agent_status", table_name="agent_executions")
    op.drop_table("agent_executions")
    op.drop_index(
        "ix_agent_heartbeats_credential_received",
        table_name="agent_heartbeats",
    )
    op.drop_index("ix_agent_heartbeats_agent_received", table_name="agent_heartbeats")
    op.drop_table("agent_heartbeats")
    op.drop_index("ix_agent_credentials_agent_status", table_name="agent_credentials")
    op.drop_table("agent_credentials")
    _drop_agent_registration_constraints_and_indexes()
    _drop_agent_registration_columns()


def _expand_alembic_version_identifier() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.alter_column(
            "alembic_version",
            "version_num",
            type_=sa.String(length=64),
            existing_type=sa.String(length=32),
            existing_nullable=False,
        )


def _extend_agent_registrations() -> None:
    op.add_column(
        "agent_registrations",
        sa.Column("owner_user_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "registration_source",
            sa.String(length=40),
            nullable=False,
            server_default="owner_enrolled",
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "active_surface_visible",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "lifecycle_status",
            sa.String(length=40),
            nullable=False,
            server_default="pending",
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "environment",
            sa.String(length=80),
            nullable=False,
            server_default="production",
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "monitoring_mode",
            sa.String(length=40),
            nullable=False,
            server_default="heartbeat",
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "heartbeat_interval_seconds",
            sa.Integer(),
            nullable=True,
            server_default="60",
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "tags",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column("repository_url", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "agent_registrations",
        sa.Column("deployment_url", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "agent_registrations",
        sa.Column("expected_version", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "agent_registrations",
        sa.Column("first_connected_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "agent_registrations",
        sa.Column("disconnected_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "agent_registrations",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "last_heartbeat_received_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "observed_health",
            sa.String(length=40),
            nullable=False,
            server_default="never_seen",
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column(
            "reported_health",
            sa.String(length=40),
            nullable=False,
            server_default="unknown",
        ),
    )
    op.add_column(
        "agent_registrations",
        sa.Column("last_agent_version", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "agent_registrations",
        sa.Column("last_build_sha", sa.String(length=80), nullable=True),
    )
    if op.get_bind().dialect.name != "sqlite":
        op.create_foreign_key(
            "fk_agent_registrations_owner_user_id_users",
            "agent_registrations",
            "users",
            ["owner_user_id"],
            ["user_id"],
        )


def _backfill_agent_registration_visibility() -> None:
    op.execute(
        sa.text(
            "UPDATE agent_registrations "
            "SET registration_source = 'legacy_descriptor', "
            "active_surface_visible = false, "
            "lifecycle_status = 'pending', "
            "environment = 'legacy', "
            "monitoring_mode = 'heartbeat', "
            "heartbeat_interval_seconds = 60, "
            "observed_health = 'never_seen', "
            "reported_health = 'unknown'"
        )
    )
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            sa.text(
                "UPDATE agent_registrations "
                "SET registration_source = 'synthetic_smoke' "
                "WHERE slug = 'hosted-runtime-smoke-agent' "
                "OR capabilities::jsonb ? 'synthetic.smoke'"
            )
        )
    else:
        op.execute(
            sa.text(
                "UPDATE agent_registrations "
                "SET registration_source = 'synthetic_smoke' "
                "WHERE slug = 'hosted-runtime-smoke-agent' "
                "OR capabilities LIKE '%synthetic.smoke%'"
            )
        )
    if bind.dialect.name != "sqlite":
        op.alter_column(
            "agent_registrations",
            "active_surface_visible",
            server_default=sa.true(),
            existing_type=sa.Boolean(),
        )


def _add_agent_registration_constraints_and_indexes() -> None:
    if op.get_bind().dialect.name != "sqlite":
        op.create_check_constraint(
            "ck_agent_registrations_registration_source",
            "agent_registrations",
            "registration_source in "
            "('owner_enrolled', 'legacy_descriptor', 'synthetic_smoke')",
        )
        op.create_check_constraint(
            "ck_agent_registrations_lifecycle_status",
            "agent_registrations",
            "lifecycle_status in "
            "('pending', 'connected', 'disconnected', 'archived')",
        )
        op.create_check_constraint(
            "ck_agent_registrations_monitoring_mode",
            "agent_registrations",
            "monitoring_mode in ('heartbeat', 'activity_only')",
        )
        op.create_check_constraint(
            "ck_agent_registrations_heartbeat_interval",
            "agent_registrations",
            "("
            "monitoring_mode = 'activity_only' "
            "and heartbeat_interval_seconds is null"
            ") or ("
            "monitoring_mode = 'heartbeat' "
            "and heartbeat_interval_seconds between 30 and 3600"
            ")",
        )
        op.create_check_constraint(
            "ck_agent_registrations_observed_health",
            "agent_registrations",
            "observed_health in "
            "('never_seen', 'online', 'late', 'offline', 'not_monitored', "
            "'disconnected', 'archived')",
        )
        op.create_check_constraint(
            "ck_agent_registrations_reported_health",
            "agent_registrations",
            "reported_health in ('unknown', 'healthy', 'degraded', 'unhealthy')",
        )
    op.create_index(
        "ix_agent_registrations_active_fleet",
        "agent_registrations",
        ["active_surface_visible", "lifecycle_status", "display_name"],
    )
    op.create_index(
        "ix_agent_registrations_owner_lifecycle",
        "agent_registrations",
        ["owner_user_id", "lifecycle_status"],
    )
    op.create_index(
        "ix_agent_registrations_observed_health",
        "agent_registrations",
        ["observed_health"],
    )
    op.create_index(
        "ix_agent_registrations_last_contact",
        "agent_registrations",
        ["last_heartbeat_received_at"],
    )


def _create_agent_visibility_tables() -> None:
    op.create_table(
        "agent_credentials",
        sa.Column("credential_id", sa.String(length=64), primary_key=True),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("credential_lookup_id", sa.String(length=80), nullable=False),
        sa.Column("verifier_hmac_sha256", sa.String(length=128), nullable=False),
        sa.Column("verifier_key_id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("scope", sa.String(length=40), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("overlap_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('active', 'overlap', 'revoked', 'expired')",
            name="ck_agent_credentials_status",
        ),
        sa.CheckConstraint(
            "scope = 'telemetry_write'",
            name="ck_agent_credentials_scope",
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agent_registrations.agent_id"]),
        sa.UniqueConstraint(
            "credential_lookup_id",
            name="uq_agent_credentials_lookup_id",
        ),
    )
    op.create_index(
        "ix_agent_credentials_agent_status",
        "agent_credentials",
        ["agent_id", "status"],
    )
    op.create_table(
        "agent_heartbeats",
        sa.Column("heartbeat_id", sa.String(length=64), primary_key=True),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("credential_id", sa.String(length=64), nullable=False),
        sa.Column("event_id", sa.String(length=120), nullable=False),
        sa.Column("event_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("contract_version", sa.String(length=40), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("agent_version", sa.String(length=80), nullable=True),
        sa.Column("build_sha", sa.String(length=80), nullable=True),
        sa.Column("environment", sa.String(length=80), nullable=False),
        sa.Column("reported_status", sa.String(length=40), nullable=False),
        sa.Column("checks_json", sa.JSON(), nullable=False),
        sa.CheckConstraint(
            "reported_status in ('healthy', 'degraded', 'unhealthy')",
            name="ck_agent_heartbeats_reported_status",
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agent_registrations.agent_id"]),
        sa.ForeignKeyConstraint(["credential_id"], ["agent_credentials.credential_id"]),
        sa.UniqueConstraint(
            "agent_id",
            "event_id",
            name="uq_agent_heartbeats_agent_event",
        ),
    )
    op.create_index(
        "ix_agent_heartbeats_agent_received",
        "agent_heartbeats",
        ["agent_id", "received_at"],
    )
    op.create_index(
        "ix_agent_heartbeats_credential_received",
        "agent_heartbeats",
        ["credential_id", "received_at"],
    )
    op.create_table(
        "agent_executions",
        sa.Column("agent_execution_id", sa.String(length=64), primary_key=True),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("external_execution_id", sa.String(length=160), nullable=False),
        sa.Column("representation_hash", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("trigger", sa.String(length=80), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("summary", sa.String(length=500), nullable=True),
        sa.Column("error_code", sa.String(length=120), nullable=True),
        sa.Column("correlation_id", sa.String(length=160), nullable=True),
        sa.Column("agent_version", sa.String(length=80), nullable=True),
        sa.Column("build_sha", sa.String(length=80), nullable=True),
        sa.Column("first_reported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_reported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("terminal_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('accepted', 'running', 'succeeded', 'failed', "
            "'cancelled', 'timed_out')",
            name="ck_agent_executions_status",
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agent_registrations.agent_id"]),
        sa.UniqueConstraint(
            "agent_id",
            "external_execution_id",
            name="uq_agent_executions_agent_external",
        ),
    )
    op.create_index(
        "ix_agent_executions_agent_status",
        "agent_executions",
        ["agent_id", "status"],
    )
    op.create_index(
        "ix_agent_executions_last_reported",
        "agent_executions",
        ["last_reported_at"],
    )
    op.create_table(
        "agent_health_evaluator_leases",
        sa.Column("lease_name", sa.String(length=80), primary_key=True),
        sa.Column("holder_id", sa.String(length=120), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(length=120), nullable=True),
        sa.Column("last_processed_count", sa.Integer(), nullable=False),
    )
    op.create_table(
        "agent_alerts",
        sa.Column("alert_id", sa.String(length=64), primary_key=True),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("condition_key", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by_user_id", sa.String(length=64), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_reason", sa.String(length=120), nullable=True),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('open', 'acknowledged', 'resolved')",
            name="ck_agent_alerts_status",
        ),
        sa.CheckConstraint(
            "severity in ('info', 'warning', 'error', 'critical')",
            name="ck_agent_alerts_severity",
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agent_registrations.agent_id"]),
        sa.ForeignKeyConstraint(["acknowledged_by_user_id"], ["users.user_id"]),
    )
    op.create_index(
        "ix_agent_alerts_agent_status",
        "agent_alerts",
        ["agent_id", "status"],
    )
    op.create_index(
        "ix_agent_alerts_last_seen",
        "agent_alerts",
        ["last_seen_at"],
    )
    op.create_index(
        "uq_agent_alerts_active_condition",
        "agent_alerts",
        ["agent_id", "condition_key"],
        unique=True,
        postgresql_where=sa.text("status in ('open', 'acknowledged')"),
        sqlite_where=sa.text("status in ('open', 'acknowledged')"),
    )
    op.create_table(
        "agent_activity_events",
        sa.Column("activity_event_id", sa.String(length=64), primary_key=True),
        sa.Column("agent_id", sa.String(length=64), nullable=True),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=False),
        sa.Column("correlation_id", sa.String(length=160), nullable=True),
        sa.Column("actor_type", sa.String(length=40), nullable=False),
        sa.Column("actor_id", sa.String(length=160), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "severity in ('info', 'warning', 'error', 'critical')",
            name="ck_agent_activity_events_severity",
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agent_registrations.agent_id"]),
    )
    op.create_index(
        "ix_agent_activity_events_occurred",
        "agent_activity_events",
        ["occurred_at"],
    )
    op.create_index(
        "ix_agent_activity_events_agent_occurred",
        "agent_activity_events",
        ["agent_id", "occurred_at"],
    )
    op.create_table(
        "agent_ingestion_rate_limits",
        sa.Column("credential_id", sa.String(length=64), primary_key=True),
        sa.Column("route_key", sa.String(length=80), primary_key=True),
        sa.Column("window_start", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "request_count >= 0",
            name="ck_agent_ingestion_rate_limits_request_count",
        ),
        sa.ForeignKeyConstraint(["credential_id"], ["agent_credentials.credential_id"]),
    )
    op.create_index(
        "ix_agent_ingestion_rate_limits_window",
        "agent_ingestion_rate_limits",
        ["route_key", "window_start"],
    )


def _drop_agent_registration_constraints_and_indexes() -> None:
    op.drop_index(
        "ix_agent_registrations_last_contact",
        table_name="agent_registrations",
    )
    op.drop_index(
        "ix_agent_registrations_observed_health",
        table_name="agent_registrations",
    )
    op.drop_index(
        "ix_agent_registrations_owner_lifecycle",
        table_name="agent_registrations",
    )
    op.drop_index(
        "ix_agent_registrations_active_fleet",
        table_name="agent_registrations",
    )
    if op.get_bind().dialect.name != "sqlite":
        op.drop_constraint(
            "ck_agent_registrations_reported_health",
            "agent_registrations",
            type_="check",
        )
        op.drop_constraint(
            "ck_agent_registrations_observed_health",
            "agent_registrations",
            type_="check",
        )
        op.drop_constraint(
            "ck_agent_registrations_heartbeat_interval",
            "agent_registrations",
            type_="check",
        )
        op.drop_constraint(
            "ck_agent_registrations_monitoring_mode",
            "agent_registrations",
            type_="check",
        )
        op.drop_constraint(
            "ck_agent_registrations_lifecycle_status",
            "agent_registrations",
            type_="check",
        )
        op.drop_constraint(
            "ck_agent_registrations_registration_source",
            "agent_registrations",
            type_="check",
        )
        op.drop_constraint(
            "fk_agent_registrations_owner_user_id_users",
            "agent_registrations",
            type_="foreignkey",
        )


def _drop_agent_registration_columns() -> None:
    for column_name in (
        "last_build_sha",
        "last_agent_version",
        "reported_health",
        "observed_health",
        "last_activity_at",
        "last_heartbeat_received_at",
        "archived_at",
        "disconnected_at",
        "first_connected_at",
        "expected_version",
        "deployment_url",
        "repository_url",
        "tags",
        "heartbeat_interval_seconds",
        "monitoring_mode",
        "environment",
        "lifecycle_status",
        "active_surface_visible",
        "registration_source",
        "owner_user_id",
    ):
        op.drop_column("agent_registrations", column_name)
