from __future__ import annotations

import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from atlas_api.models.job import QueueJob

TERMINAL_STATES = {"succeeded", "dead_letter", "cancelled"}


class QueueError(ValueError):
    pass


@dataclass(frozen=True)
class LeasedJob:
    queue_job_id: str
    lease_token: str
    lease_expires_at: datetime


@dataclass(frozen=True)
class QueueAuditEvent:
    event_type: str
    job_id: str
    metadata: dict[str, int | str | None]


QueueAuditHook = Callable[[QueueAuditEvent], None]


def enqueue(
    session: Session,
    *,
    job_type: str,
    payload_metadata: dict[str, Any],
    resource_reference: str | None = None,
    idempotency_key: str | None = None,
    priority: int = 50,
    max_attempts: int = 5,
    now: datetime | None = None,
    audit_hook: QueueAuditHook | None = None,
) -> QueueJob:
    _validate_enqueue(job_type, payload_metadata, priority, max_attempts)
    if idempotency_key:
        existing = session.scalar(
            select(QueueJob).where(
                QueueJob.job_type == job_type,
                QueueJob.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            _audit(audit_hook, "queue.job_deduplicated", existing)
            return existing
    job = QueueJob(
        job_type=job_type,
        payload_metadata=payload_metadata,
        resource_reference=resource_reference,
        idempotency_key=idempotency_key,
        priority=priority,
        max_attempts=max_attempts,
        available_at=now or datetime.now(UTC),
    )
    session.add(job)
    session.flush()
    _audit(audit_hook, "queue.job_enqueued", job)
    return job


def claim(
    session: Session,
    *,
    owner_id: str,
    lease_seconds: int = 60,
    now: datetime | None = None,
    audit_hook: QueueAuditHook | None = None,
) -> LeasedJob | None:
    if not 15 <= lease_seconds <= 900:
        raise QueueError("lease_seconds_invalid")
    current = now or datetime.now(UTC)
    _recover_expired_leases(session, current, audit_hook)
    statement: Select[tuple[QueueJob]] = (
        select(QueueJob)
        .where(
            QueueJob.state.in_(("queued", "retry_wait")),
            QueueJob.available_at <= current,
        )
        .order_by(QueueJob.available_at, QueueJob.priority, QueueJob.created_at)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    job = session.scalar(statement)
    if job is None:
        return None
    token = secrets.token_urlsafe(32)
    job.state = "leased"
    job.lease_owner_id = owner_id
    job.lease_token = token
    job.leased_at = current
    job.lease_expires_at = current + timedelta(seconds=lease_seconds)
    job.attempt_count += 1
    session.flush()
    _audit(audit_hook, "queue.job_claimed", job, worker_id=owner_id)
    return LeasedJob(job.queue_job_id, token, job.lease_expires_at)


def succeed(
    session: Session,
    *,
    job_id: str,
    lease_token: str,
    now: datetime,
    audit_hook: QueueAuditHook | None = None,
) -> None:
    job = _leased_job(session, job_id, lease_token, now)
    job.state = "succeeded"
    job.completed_at = now
    _clear_lease(job)
    _audit(audit_hook, "queue.job_succeeded", job)


def extend_lease(
    session: Session,
    *,
    job_id: str,
    lease_token: str,
    lease_seconds: int,
    now: datetime,
    audit_hook: QueueAuditHook | None = None,
) -> datetime:
    if not 15 <= lease_seconds <= 900:
        raise QueueError("lease_seconds_invalid")
    job = _leased_job(session, job_id, lease_token, now)
    job.lease_expires_at = now + timedelta(seconds=lease_seconds)
    _audit(audit_hook, "queue.lease_extended", job)
    return job.lease_expires_at


def retry(
    session: Session,
    *,
    job_id: str,
    lease_token: str,
    delay_seconds: int,
    error_code: str,
    now: datetime,
    audit_hook: QueueAuditHook | None = None,
) -> None:
    job = _leased_job(session, job_id, lease_token, now)
    job.last_error_code = error_code
    _clear_lease(job)
    if job.attempt_count >= job.max_attempts:
        job.state = "dead_letter"
        _audit(audit_hook, "queue.job_dead_lettered", job, error_code=error_code)
        return
    job.state = "retry_wait"
    job.available_at = now + timedelta(seconds=delay_seconds)
    _audit(audit_hook, "queue.job_retry_scheduled", job, error_code=error_code)


def cancel(
    session: Session,
    *,
    job_id: str,
    now: datetime,
    audit_hook: QueueAuditHook | None = None,
) -> None:
    job = session.get(QueueJob, job_id)
    if job is None or job.state in TERMINAL_STATES:
        raise QueueError("job_not_cancellable")
    job.state = "cancelled"
    job.cancelled_at = now
    _clear_lease(job)
    _audit(audit_hook, "queue.job_cancelled", job)


def _recover_expired_leases(
    session: Session, now: datetime, audit_hook: QueueAuditHook | None = None
) -> None:
    expired = session.scalars(
        select(QueueJob).where(
            QueueJob.state == "leased", QueueJob.lease_expires_at < now
        )
    )
    for job in expired:
        job.recovery_count += 1
        job.state = "queued"
        job.available_at = now
        _clear_lease(job)
        _audit(audit_hook, "queue.lease_recovered", job)


def _leased_job(session: Session, job_id: str, token: str, now: datetime) -> QueueJob:
    job = session.get(QueueJob, job_id)
    if (
        job is None
        or job.state != "leased"
        or job.lease_token != token
        or job.lease_expires_at is None
        or job.lease_expires_at <= now
    ):
        raise QueueError("lease_invalid")
    return job


def _clear_lease(job: QueueJob) -> None:
    job.lease_token = None
    job.lease_owner_id = None
    job.lease_expires_at = None
    job.leased_at = None


def _audit(
    audit_hook: QueueAuditHook | None,
    event_type: str,
    job: QueueJob,
    **metadata: int | str | None,
) -> None:
    if audit_hook is not None:
        audit_hook(
            QueueAuditEvent(
                event_type=event_type,
                job_id=job.queue_job_id,
                metadata={
                    "job_type": job.job_type,
                    "state": job.state,
                    "resource_reference": job.resource_reference,
                    "attempt_count": job.attempt_count,
                    **metadata,
                },
            )
        )


def _validate_enqueue(
    job_type: str, payload: dict[str, Any], priority: int, max_attempts: int
) -> None:
    if not job_type or len(job_type) > 120 or not 0 <= priority <= 100:
        raise QueueError("job_input_invalid")
    if not isinstance(payload, dict) or max_attempts < 1 or max_attempts > 10:
        raise QueueError("job_input_invalid")
