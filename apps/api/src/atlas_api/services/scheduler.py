from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.models.schedule import JobSchedule, ScheduleOccurrence
from atlas_api.services.queue import QueueError, enqueue

MIN_INTERVAL_SECONDS = 60
MAX_INTERVAL_SECONDS = 30 * 24 * 60 * 60
MAX_CATCH_UP_INTERVALS = 100


class SchedulerError(ValueError):
    pass


@dataclass(frozen=True)
class ScheduleAuditEvent:
    event_type: str
    schedule_id: str
    metadata: dict[str, int | str]


ScheduleAuditHook = Callable[[ScheduleAuditEvent], None]


def create_schedule(
    session: Session,
    *,
    job_type: str,
    payload_metadata: dict[str, Any],
    interval_seconds: int,
    next_due_at: datetime,
    resource_reference: str | None = None,
    audit_hook: ScheduleAuditHook | None = None,
) -> JobSchedule:
    _validate_schedule_input(job_type, payload_metadata, interval_seconds, next_due_at)
    schedule = JobSchedule(
        job_type=job_type,
        payload_metadata=payload_metadata,
        interval_seconds=interval_seconds,
        next_due_at=next_due_at,
        resource_reference=resource_reference,
    )
    session.add(schedule)
    session.flush()
    _audit(audit_hook, "scheduler.schedule_created", schedule)
    return schedule


def update_schedule(
    session: Session,
    *,
    schedule_id: str,
    interval_seconds: int | None = None,
    next_due_at: datetime | None = None,
    enabled: bool | None = None,
    audit_hook: ScheduleAuditHook | None = None,
) -> JobSchedule:
    schedule = session.get(JobSchedule, schedule_id)
    if schedule is None:
        raise SchedulerError("schedule_not_found")
    if interval_seconds is not None:
        _validate_interval(interval_seconds)
        schedule.interval_seconds = interval_seconds
    if next_due_at is not None:
        _validate_utc(next_due_at)
        schedule.next_due_at = next_due_at
    if enabled is not None:
        schedule.enabled = enabled
    if interval_seconds is None and next_due_at is None and enabled is None:
        raise SchedulerError("schedule_update_empty")
    schedule.version += 1
    session.flush()
    _audit(audit_hook, "scheduler.schedule_updated", schedule)
    return schedule


def disable_schedule(
    session: Session,
    *,
    schedule_id: str,
    audit_hook: ScheduleAuditHook | None = None,
) -> JobSchedule:
    schedule = session.get(JobSchedule, schedule_id)
    if schedule is None:
        raise SchedulerError("schedule_not_found")
    if schedule.enabled:
        schedule.enabled = False
        schedule.version += 1
        session.flush()
        _audit(audit_hook, "scheduler.schedule_disabled", schedule)
    return schedule


def sweep_due_schedules(
    session: Session,
    *,
    now: datetime,
    audit_hook: ScheduleAuditHook | None = None,
) -> int:
    """Emit at most one occurrence per due schedule in the caller's transaction."""
    _validate_utc(now)
    schedules = session.scalars(
        select(JobSchedule)
        .where(JobSchedule.enabled, JobSchedule.next_due_at <= now)
        .with_for_update(skip_locked=True)
    ).all()
    triggered = 0
    for schedule in schedules:
        scheduled_for = _as_utc(schedule.next_due_at)
        intervals_behind = int(
            (now - scheduled_for).total_seconds() // schedule.interval_seconds
        )
        if intervals_behind > MAX_CATCH_UP_INTERVALS:
            skipped_count = intervals_behind + 1
            schedule.next_due_at = scheduled_for + timedelta(
                seconds=schedule.interval_seconds * skipped_count
            )
            _audit(
                audit_hook,
                "scheduler.occurrences_skipped",
                schedule,
                skipped_count=skipped_count,
            )
            continue
        try:
            job = enqueue(
                session,
                job_type=schedule.job_type,
                payload_metadata=schedule.payload_metadata,
                resource_reference=schedule.resource_reference,
                idempotency_key=(
                    f"schedule:{schedule.job_schedule_id}:{scheduled_for.isoformat()}"
                ),
                now=now,
            )
        except QueueError as error:
            raise SchedulerError("schedule_enqueue_invalid") from error
        session.add(
            ScheduleOccurrence(
                job_schedule_id=schedule.job_schedule_id,
                scheduled_for=scheduled_for,
                queue_job_id=job.queue_job_id,
                created_at=now,
            )
        )
        schedule.last_triggered_at = now
        schedule.next_due_at = scheduled_for + timedelta(
            seconds=schedule.interval_seconds
        )
        _audit(
            audit_hook,
            "scheduler.schedule_triggered",
            schedule,
            scheduled_for=scheduled_for.isoformat(),
            queue_job_id=job.queue_job_id,
        )
        triggered += 1
    session.flush()
    return triggered


def _validate_schedule_input(
    job_type: str,
    payload_metadata: dict[str, Any],
    interval_seconds: int,
    next_due_at: datetime,
) -> None:
    if not job_type or len(job_type) > 120 or not isinstance(payload_metadata, dict):
        raise SchedulerError("schedule_input_invalid")
    _validate_interval(interval_seconds)
    _validate_utc(next_due_at)


def _validate_interval(interval_seconds: int) -> None:
    if not MIN_INTERVAL_SECONDS <= interval_seconds <= MAX_INTERVAL_SECONDS:
        raise SchedulerError("interval_seconds_invalid")


def _validate_utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise SchedulerError("timestamp_must_be_utc")


def _as_utc(value: datetime) -> datetime:
    """Normalize legacy SQLite test values; PostgreSQL preserves tz-aware UTC."""
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def _audit(
    audit_hook: ScheduleAuditHook | None,
    event_type: str,
    schedule: JobSchedule,
    **metadata: int | str,
) -> None:
    if audit_hook is not None:
        audit_hook(
            ScheduleAuditEvent(
                event_type=event_type,
                schedule_id=schedule.job_schedule_id,
                metadata=metadata,
            )
        )
