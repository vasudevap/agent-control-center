from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from atlas_api.db.base import Base
from atlas_api.models import (  # noqa: F401
    audit,
    external_client,
    external_request_nonce,
    knowledge,
    owner_session,
    webhook,
)
from atlas_api.services.queue import (
    QueueError,
    cancel,
    claim,
    enqueue,
    extend_lease,
    retry,
    succeed,
)


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as database:
        yield database


def test_queue_lifecycle_idempotency_and_stale_lease_rejection(
    session: Session,
) -> None:
    now = datetime(2026, 7, 17, tzinfo=UTC)
    job = enqueue(
        session,
        job_type="platform.maintenance",
        payload_metadata={"resource": "test"},
        idempotency_key="test-key",
        now=now,
    )
    assert (
        enqueue(
            session,
            job_type="platform.maintenance",
            payload_metadata={"resource": "test"},
            idempotency_key="test-key",
            now=now,
        ).queue_job_id
        == job.queue_job_id
    )

    lease = claim(session, owner_id="worker-1", now=now)
    assert lease is not None
    with pytest.raises(QueueError):
        succeed(session, job_id=job.queue_job_id, lease_token="stale", now=now)
    retry(
        session,
        job_id=job.queue_job_id,
        lease_token=lease.lease_token,
        delay_seconds=1,
        error_code="transient",
        now=now,
    )
    recovered = claim(session, owner_id="worker-2", now=now + timedelta(seconds=1))
    assert recovered is not None
    succeed(
        session,
        job_id=job.queue_job_id,
        lease_token=recovered.lease_token,
        now=now + timedelta(seconds=1),
    )
    assert job.state == "succeeded"


def test_claim_prioritizes_and_recovers_expired_leases(session: Session) -> None:
    now = datetime(2026, 7, 17, tzinfo=UTC)
    slow = enqueue(
        session, job_type="test.slow", payload_metadata={}, priority=80, now=now
    )
    fast = enqueue(
        session, job_type="test.fast", payload_metadata={}, priority=10, now=now
    )
    lease = claim(session, owner_id="worker-1", now=now)
    assert lease is not None and lease.queue_job_id == fast.queue_job_id
    assert extend_lease(
        session,
        job_id=fast.queue_job_id,
        lease_token=lease.lease_token,
        lease_seconds=15,
        now=now,
    ) == now + timedelta(seconds=15)
    next_lease = claim(session, owner_id="worker-2", now=now + timedelta(seconds=16))
    assert next_lease is not None and next_lease.queue_job_id == slow.queue_job_id
    recovered = claim(session, owner_id="worker-3", now=now + timedelta(seconds=16))
    assert recovered is not None and recovered.queue_job_id == fast.queue_job_id
    assert fast.recovery_count == 1
    cancel(session, job_id=slow.queue_job_id, now=now)
    assert slow.state == "cancelled"
