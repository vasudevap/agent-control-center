from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from atlas_api.db.base import Base, TimestampMixin, prefixed_id, utc_now


class QueueJob(TimestampMixin, Base):
    __tablename__ = "queue_jobs"
    __table_args__ = (
        UniqueConstraint(
            "job_type", "idempotency_key", name="uq_queue_job_idempotency"
        ),
    )

    queue_job_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: prefixed_id("job")
    )
    job_type: Mapped[str] = mapped_column(String(120), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    state: Mapped[str] = mapped_column(String(40), nullable=False, default="queued")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    payload_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    resource_reference: Mapped[str | None] = mapped_column(String(240), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    leased_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_token: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lease_owner_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    recovery_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
