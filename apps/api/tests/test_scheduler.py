from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from atlas_api.cli.sweep_schedules import run_once
from atlas_api.db.base import Base
from atlas_api.models import (  # noqa: F401
    audit as _audit,
)
from atlas_api.models.job import QueueJob
from atlas_api.models.schedule import ScheduleOccurrence
from atlas_api.services.scheduler import (
    MAX_CATCH_UP_INTERVALS,
    ScheduleAuditEvent,
    SchedulerError,
    create_schedule,
    disable_schedule,
    sweep_due_schedules,
    update_schedule,
)


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as database:
        yield database


def test_sweep_enqueues_one_deterministic_occurrence_per_sweep(
    session: Session,
) -> None:
    now = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)
    schedule = create_schedule(
        session,
        job_type="platform.maintenance",
        payload_metadata={"resource": "test"},
        interval_seconds=60,
        next_due_at=now - timedelta(minutes=2),
    )

    events: list[ScheduleAuditEvent] = []
    assert sweep_due_schedules(session, now=now, audit_hook=events.append) == 1
    occurrence = session.scalar(select(ScheduleOccurrence))
    job = session.scalar(select(QueueJob))
    assert occurrence is not None and job is not None
    assert occurrence.queue_job_id == job.queue_job_id
    assert occurrence.scheduled_for.replace(tzinfo=UTC) == now - timedelta(minutes=2)
    assert schedule.next_due_at == now - timedelta(minutes=1)
    assert job.idempotency_key == (
        "schedule:"
        f"{schedule.job_schedule_id}:{occurrence.scheduled_for.replace(tzinfo=UTC).isoformat()}"
    )
    assert sweep_due_schedules(session, now=now) == 1
    assert len(session.scalars(select(ScheduleOccurrence)).all()) == 2
    assert len(events) == 1


def test_skip_ahead_audits_when_more_than_100_intervals_behind(
    session: Session,
) -> None:
    now = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)
    scheduled_for = now - timedelta(seconds=60 * (MAX_CATCH_UP_INTERVALS + 1))
    schedule = create_schedule(
        session,
        job_type="platform.maintenance",
        payload_metadata={},
        interval_seconds=60,
        next_due_at=scheduled_for,
    )
    events: list[ScheduleAuditEvent] = []

    assert sweep_due_schedules(session, now=now, audit_hook=events.append) == 0
    assert schedule.next_due_at == now + timedelta(seconds=60)
    assert session.scalar(select(QueueJob)) is None
    event = events[0]
    assert event.event_type == "scheduler.occurrences_skipped"
    assert event.metadata["skipped_count"] == MAX_CATCH_UP_INTERVALS + 2


def test_update_disable_and_validation_boundaries(session: Session) -> None:
    now = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)
    with pytest.raises(SchedulerError, match="interval_seconds_invalid"):
        create_schedule(
            session,
            job_type="platform.maintenance",
            payload_metadata={},
            interval_seconds=59,
            next_due_at=now,
        )
    with pytest.raises(SchedulerError, match="timestamp_must_be_utc"):
        create_schedule(
            session,
            job_type="platform.maintenance",
            payload_metadata={},
            interval_seconds=60,
            next_due_at=datetime(2026, 7, 17, 12, 0),
        )
    schedule = create_schedule(
        session,
        job_type="platform.maintenance",
        payload_metadata={},
        interval_seconds=60,
        next_due_at=now,
    )
    update_schedule(
        session,
        schedule_id=schedule.job_schedule_id,
        interval_seconds=120,
        next_due_at=now + timedelta(minutes=5),
    )
    assert schedule.interval_seconds == 120
    assert schedule.version == 2
    disable_schedule(session, schedule_id=schedule.job_schedule_id)
    assert schedule.enabled is False
    assert sweep_due_schedules(session, now=now + timedelta(days=1)) == 0
    with pytest.raises(SchedulerError, match="schedule_update_empty"):
        update_schedule(session, schedule_id=schedule.job_schedule_id)


def test_schedule_changes_roll_back_with_enqueue_failure(session: Session) -> None:
    now = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)
    schedule = create_schedule(
        session,
        job_type="platform.maintenance",
        payload_metadata={},
        interval_seconds=60,
        next_due_at=now,
    )
    session.commit()

    def reject_audit(_: ScheduleAuditEvent) -> None:
        raise RuntimeError("audit storage unavailable")

    with pytest.raises(RuntimeError, match="audit storage unavailable"):
        sweep_due_schedules(session, now=now, audit_hook=reject_audit)
    session.rollback()
    session.refresh(schedule)
    assert schedule.next_due_at.replace(tzinfo=UTC) == now
    assert session.scalar(select(ScheduleOccurrence)) is None
    assert session.scalar(select(QueueJob)) is None


def test_one_shot_command_uses_a_single_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    with factory.begin() as session:
        create_schedule(
            session,
            job_type="platform.maintenance",
            payload_metadata={},
            interval_seconds=60,
            next_due_at=now,
        )
    monkeypatch.setattr("atlas_api.cli.sweep_schedules.utc_now", lambda: now)

    assert run_once(factory) == 1
    with factory() as session:
        assert session.scalar(select(ScheduleOccurrence)) is not None
