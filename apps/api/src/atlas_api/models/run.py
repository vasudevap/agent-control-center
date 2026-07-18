from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from atlas_api.db.base import Base, TimestampMixin, prefixed_id


class AgentRun(TimestampMixin, Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "idempotency_key", name="uq_run_idempotency"),
    )

    run_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("run"),
    )
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    agent_id: Mapped[str] = mapped_column(ForeignKey("agent_registrations.agent_id"))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="queued")
    trigger_source: Mapped[str] = mapped_column(String(40), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(80), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    queue_job_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_reason_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class AgentRunStep(TimestampMixin, Base):
    __tablename__ = "agent_run_steps"

    run_step_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("rstep"),
    )
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.run_id"))
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
