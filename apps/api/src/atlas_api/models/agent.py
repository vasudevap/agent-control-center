from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from atlas_api.db.base import Base, TimestampMixin, prefixed_id, utc_now


class AgentRegistration(TimestampMixin, Base):
    __tablename__ = "agent_registrations"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_agent_registration_slug"),
        CheckConstraint(
            "registration_source in "
            "('owner_enrolled', 'legacy_descriptor', 'synthetic_smoke')",
            name="ck_agent_registrations_registration_source",
        ),
        CheckConstraint(
            "lifecycle_status in "
            "('pending', 'connected', 'disconnected', 'archived')",
            name="ck_agent_registrations_lifecycle_status",
        ),
        CheckConstraint(
            "monitoring_mode in ('heartbeat', 'activity_only')",
            name="ck_agent_registrations_monitoring_mode",
        ),
        CheckConstraint(
            "("
            "monitoring_mode = 'activity_only' "
            "and heartbeat_interval_seconds is null"
            ") or ("
            "monitoring_mode = 'heartbeat' "
            "and heartbeat_interval_seconds between 30 and 3600"
            ")",
            name="ck_agent_registrations_heartbeat_interval",
        ),
        CheckConstraint(
            "observed_health in "
            "('never_seen', 'online', 'late', 'offline', 'not_monitored', "
            "'disconnected', 'archived')",
            name="ck_agent_registrations_observed_health",
        ),
        CheckConstraint(
            "reported_health in ('unknown', 'healthy', 'degraded', 'unhealthy')",
            name="ck_agent_registrations_reported_health",
        ),
        Index(
            "ix_agent_registrations_active_fleet",
            "active_surface_visible",
            "lifecycle_status",
            "display_name",
        ),
        Index(
            "ix_agent_registrations_owner_lifecycle",
            "owner_user_id",
            "lifecycle_status",
        ),
        Index(
            "ix_agent_registrations_observed_health",
            "observed_health",
        ),
        Index(
            "ix_agent_registrations_last_contact",
            "last_heartbeat_received_at",
        ),
    )

    agent_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("agt"),
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    descriptor_version: Mapped[int] = mapped_column(nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    risk_level: Mapped[str] = mapped_column(String(40), nullable=False)
    capabilities: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allowed_tools: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    required_connectors: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    configuration_schema_ref: Mapped[str | None] = mapped_column(
        String(240),
        nullable=True,
    )
    configuration_schema: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    supports_manual_run: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    supports_scheduled_run: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    health_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="unknown",
    )
    health_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    owner_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
    )
    registration_source: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="owner_enrolled",
    )
    active_surface_visible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    lifecycle_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="pending",
    )
    environment: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        default="production",
    )
    monitoring_mode: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="heartbeat",
    )
    heartbeat_interval_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=60,
    )
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    repository_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    deployment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expected_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    first_connected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    disconnected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_heartbeat_received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    observed_health: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="never_seen",
    )
    reported_health: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="unknown",
    )
    last_agent_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_build_sha: Mapped[str | None] = mapped_column(String(80), nullable=True)


class AgentCredential(TimestampMixin, Base):
    __tablename__ = "agent_credentials"
    __table_args__ = (
        UniqueConstraint(
            "credential_lookup_id",
            name="uq_agent_credentials_lookup_id",
        ),
        CheckConstraint(
            "status in ('active', 'overlap', 'revoked', 'expired')",
            name="ck_agent_credentials_status",
        ),
        CheckConstraint(
            "scope = 'telemetry_write'",
            name="ck_agent_credentials_scope",
        ),
        Index("ix_agent_credentials_agent_status", "agent_id", "status"),
    )

    credential_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("agc"),
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agent_registrations.agent_id"),
        nullable=False,
    )
    credential_lookup_id: Mapped[str] = mapped_column(String(80), nullable=False)
    verifier_hmac_sha256: Mapped[str] = mapped_column(String(128), nullable=False)
    verifier_key_id: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    scope: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="telemetry_write",
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    overlap_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class AgentHeartbeat(Base):
    __tablename__ = "agent_heartbeats"
    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "event_id",
            name="uq_agent_heartbeats_agent_event",
        ),
        CheckConstraint(
            "reported_status in ('healthy', 'degraded', 'unhealthy')",
            name="ck_agent_heartbeats_reported_status",
        ),
        Index("ix_agent_heartbeats_agent_received", "agent_id", "received_at"),
        Index(
            "ix_agent_heartbeats_credential_received",
            "credential_id",
            "received_at",
        ),
    )

    heartbeat_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("ahb"),
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agent_registrations.agent_id"),
        nullable=False,
    )
    credential_id: Mapped[str] = mapped_column(
        ForeignKey("agent_credentials.credential_id"),
        nullable=False,
    )
    event_id: Mapped[str] = mapped_column(String(120), nullable=False)
    event_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(40), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    agent_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    build_sha: Mapped[str | None] = mapped_column(String(80), nullable=True)
    environment: Mapped[str] = mapped_column(String(80), nullable=False)
    reported_status: Mapped[str] = mapped_column(String(40), nullable=False)
    checks_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )


class AgentExecution(TimestampMixin, Base):
    __tablename__ = "agent_executions"
    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "external_execution_id",
            name="uq_agent_executions_agent_external",
        ),
        CheckConstraint(
            "status in ('accepted', 'running', 'succeeded', 'failed', "
            "'cancelled', 'timed_out')",
            name="ck_agent_executions_status",
        ),
        Index("ix_agent_executions_agent_status", "agent_id", "status"),
        Index("ix_agent_executions_last_reported", "last_reported_at"),
    )

    agent_execution_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("aex"),
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agent_registrations.agent_id"),
        nullable=False,
    )
    external_execution_id: Mapped[str] = mapped_column(String(160), nullable=False)
    representation_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    trigger: Mapped[str] = mapped_column(String(80), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    agent_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    build_sha: Mapped[str | None] = mapped_column(String(80), nullable=True)
    first_reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    last_reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    terminal_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class AgentHealthEvaluatorLease(Base):
    __tablename__ = "agent_health_evaluator_leases"

    lease_name: Mapped[str] = mapped_column(String(80), primary_key=True)
    holder_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    lease_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_processed_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )


class AgentAlert(TimestampMixin, Base):
    __tablename__ = "agent_alerts"
    __table_args__ = (
        CheckConstraint(
            "status in ('open', 'acknowledged', 'resolved')",
            name="ck_agent_alerts_status",
        ),
        CheckConstraint(
            "severity in ('info', 'warning', 'error', 'critical')",
            name="ck_agent_alerts_severity",
        ),
        Index("ix_agent_alerts_agent_status", "agent_id", "status"),
        Index("ix_agent_alerts_last_seen", "last_seen_at"),
        Index(
            "uq_agent_alerts_active_condition",
            "agent_id",
            "condition_key",
            unique=True,
            sqlite_where=text("status in ('open', 'acknowledged')"),
            postgresql_where=text("status in ('open', 'acknowledged')"),
        ),
    )

    alert_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("aal"),
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agent_registrations.agent_id"),
        nullable=False,
    )
    condition_key: Mapped[str] = mapped_column(String(180), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="open")
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    acknowledged_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolved_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    evidence_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )


class AgentActivityEvent(Base):
    __tablename__ = "agent_activity_events"
    __table_args__ = (
        CheckConstraint(
            "severity in ('info', 'warning', 'error', 'critical')",
            name="ck_agent_activity_events_severity",
        ),
        Index("ix_agent_activity_events_occurred", "occurred_at"),
        Index("ix_agent_activity_events_agent_occurred", "agent_id", "occurred_at"),
    )

    activity_event_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("act"),
    )
    agent_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_registrations.agent_id"),
        nullable=True,
    )
    source_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_id: Mapped[str] = mapped_column(String(160), nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(40), nullable=False, default="info")
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(40), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )


class AgentIngestionRateLimit(Base):
    __tablename__ = "agent_ingestion_rate_limits"
    __table_args__ = (
        CheckConstraint(
            "request_count >= 0",
            name="ck_agent_ingestion_rate_limits_request_count",
        ),
        Index(
            "ix_agent_ingestion_rate_limits_window",
            "route_key",
            "window_start",
        ),
    )

    credential_id: Mapped[str] = mapped_column(
        ForeignKey("agent_credentials.credential_id"),
        primary_key=True,
    )
    route_key: Mapped[str] = mapped_column(String(80), primary_key=True)
    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
    )
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
