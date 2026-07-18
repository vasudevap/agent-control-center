from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from atlas_api.db.base import Base, TimestampMixin, prefixed_id


class JobSchedule(TimestampMixin, Base):
    __tablename__ = "job_schedules"
    job_schedule_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: prefixed_id("sch")
    )
    job_type: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_reference: Mapped[str | None] = mapped_column(String(240))
    payload_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    next_due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class ScheduleOccurrence(Base):
    __tablename__ = "schedule_occurrences"
    __table_args__ = (
        UniqueConstraint(
            "job_schedule_id", "scheduled_for", name="uq_schedule_occurrence"
        ),
    )
    schedule_occurrence_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: prefixed_id("soc")
    )
    job_schedule_id: Mapped[str] = mapped_column(
        ForeignKey("job_schedules.job_schedule_id"), nullable=False
    )
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    queue_job_id: Mapped[str] = mapped_column(
        ForeignKey("queue_jobs.queue_job_id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
