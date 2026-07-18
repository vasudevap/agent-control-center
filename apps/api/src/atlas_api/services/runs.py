from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from atlas_api.core.contracts import PaginationParameters, decode_cursor, encode_cursor
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.agent import AgentRegistration
from atlas_api.models.run import AgentRun, AgentRunStep
from atlas_api.services.queue import QueueError, enqueue
from atlas_api.services.queue import cancel as cancel_queue_job

ALLOWED_RUN_STATUSES = frozenset(
    {"queued", "running", "succeeded", "failed", "cancelled"}
)
ALLOWED_TRIGGER_SOURCES = frozenset({"manual", "scheduled"})
TERMINAL_RUN_STATUSES = frozenset({"succeeded", "failed", "cancelled"})
_SENSITIVE_PAYLOAD_KEYS = frozenset({"body", "content", "text", "token", "secret"})
_ALLOWED_STEP_STATUSES = frozenset({"succeeded", "failed", "skipped", "blocked"})


@dataclass(frozen=True)
class RunPage:
    runs: list[AgentRun]
    next_cursor: str | None


def create_manual_run(
    session: Session,
    *,
    owner_user_id: str,
    agent_id: str,
    idempotency_key: str,
    correlation_id: str,
    timeout_seconds: int = 300,
) -> AgentRun:
    _validate_timeout(timeout_seconds)
    existing = session.scalar(
        select(AgentRun).where(
            AgentRun.owner_user_id == owner_user_id,
            AgentRun.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        return existing
    agent = session.get(AgentRegistration, agent_id)
    if agent is None or agent.status != "active":
        raise ApiError(404, "agent_not_found", "Agent was not found.")
    if not agent.supports_manual_run:
        raise ApiError(
            409,
            "agent_manual_run_unsupported",
            "Agent does not support manual runs.",
        )
    run = AgentRun(
        owner_user_id=owner_user_id,
        agent_id=agent_id,
        status="queued",
        trigger_source="manual",
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
        timeout_seconds=timeout_seconds,
    )
    session.add(run)
    session.flush()
    payload_metadata = {
        "run_id": run.run_id,
        "agent_id": run.agent_id,
        "trigger_source": run.trigger_source,
    }
    _validate_reference_payload(payload_metadata)
    try:
        job = enqueue(
            session,
            job_type="agent.run",
            payload_metadata=payload_metadata,
            resource_reference=run.run_id,
            idempotency_key=f"run:{run.run_id}",
        )
    except QueueError as exc:
        raise ApiError(
            500,
            "run_queue_enqueue_failed",
            "Run could not be queued.",
        ) from exc
    run.queue_job_id = job.queue_job_id
    session.flush()
    return run


def create_scheduled_run(
    session: Session,
    *,
    owner_user_id: str,
    agent_id: str,
    idempotency_key: str,
    correlation_id: str,
    scheduled_for: datetime,
    schedule_id: str | None = None,
    timeout_seconds: int = 300,
) -> AgentRun:
    _validate_timeout(timeout_seconds)
    existing = session.scalar(
        select(AgentRun).where(
            AgentRun.owner_user_id == owner_user_id,
            AgentRun.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        return existing
    agent = session.get(AgentRegistration, agent_id)
    if agent is None or agent.status != "active":
        raise ApiError(404, "agent_not_found", "Agent was not found.")
    if not agent.supports_scheduled_run:
        raise ApiError(
            409,
            "agent_scheduled_run_unsupported",
            "Agent does not support scheduled runs.",
        )
    run = AgentRun(
        owner_user_id=owner_user_id,
        agent_id=agent_id,
        status="queued",
        trigger_source="scheduled",
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
        timeout_seconds=timeout_seconds,
    )
    session.add(run)
    session.flush()
    payload_metadata = {
        "run_id": run.run_id,
        "agent_id": run.agent_id,
        "trigger_source": run.trigger_source,
        "scheduled_for": scheduled_for.isoformat(),
    }
    if schedule_id is not None:
        payload_metadata["schedule_id"] = schedule_id
    _validate_reference_payload(payload_metadata)
    try:
        job = enqueue(
            session,
            job_type="agent.run",
            payload_metadata=payload_metadata,
            resource_reference=run.run_id,
            idempotency_key=f"run:{run.run_id}",
        )
    except QueueError as exc:
        raise ApiError(
            500,
            "run_queue_enqueue_failed",
            "Run could not be queued.",
        ) from exc
    run.queue_job_id = job.queue_job_id
    session.flush()
    return run


def list_runs(
    session: Session,
    *,
    owner_user_id: str,
    pagination: PaginationParameters,
    status: str | None = None,
) -> RunPage:
    if status is not None and status not in ALLOWED_RUN_STATUSES:
        raise ApiError(422, "run_status_invalid", "Run status is invalid.")
    query = select(AgentRun).where(AgentRun.owner_user_id == owner_user_id)
    if status is not None:
        query = query.where(AgentRun.status == status)
    query = _apply_cursor(query, pagination.cursor)
    query = query.order_by(AgentRun.created_at, AgentRun.run_id)
    runs = list(session.scalars(query.limit(pagination.limit + 1)))
    next_cursor = None
    if len(runs) > pagination.limit:
        runs = runs[: pagination.limit]
        last = runs[-1]
        next_cursor = encode_cursor(
            {"created_at": last.created_at.isoformat(), "run_id": last.run_id}
        )
    return RunPage(runs=runs, next_cursor=next_cursor)


def get_run(session: Session, *, owner_user_id: str, run_id: str) -> AgentRun:
    run = session.get(AgentRun, run_id)
    if run is None or run.owner_user_id != owner_user_id:
        raise ApiError(404, "run_not_found", "Run was not found.")
    return run


def start_run(
    session: Session,
    *,
    owner_user_id: str,
    run_id: str,
    now: datetime | None = None,
) -> AgentRun:
    run = get_run(session, owner_user_id=owner_user_id, run_id=run_id)
    if run.status in TERMINAL_RUN_STATUSES:
        raise ApiError(409, "run_not_startable", "Run is not startable.")
    if run.status == "running":
        return run
    run.status = "running"
    run.started_at = now or utc_now()
    session.flush()
    return run


def complete_run(
    session: Session,
    *,
    owner_user_id: str,
    run_id: str,
    now: datetime | None = None,
) -> AgentRun:
    run = get_run(session, owner_user_id=owner_user_id, run_id=run_id)
    if run.status in TERMINAL_RUN_STATUSES:
        raise ApiError(409, "run_already_terminal", "Run is already terminal.")
    run.status = "succeeded"
    run.completed_at = now or utc_now()
    session.flush()
    return run


def fail_run(
    session: Session,
    *,
    owner_user_id: str,
    run_id: str,
    reason_code: str,
    now: datetime | None = None,
) -> AgentRun:
    run = get_run(session, owner_user_id=owner_user_id, run_id=run_id)
    if run.status in TERMINAL_RUN_STATUSES:
        raise ApiError(409, "run_already_terminal", "Run is already terminal.")
    if not reason_code or len(reason_code) > 120:
        raise ApiError(422, "run_failure_reason_invalid", "Failure reason is invalid.")
    run.status = "failed"
    run.failure_reason_code = reason_code
    run.completed_at = now or utc_now()
    session.flush()
    return run


def record_run_step(
    session: Session,
    *,
    run_id: str,
    step_name: str,
    status: str,
    metadata: dict[str, Any] | None = None,
) -> AgentRunStep:
    if status not in _ALLOWED_STEP_STATUSES:
        raise ApiError(422, "run_step_status_invalid", "Run step status is invalid.")
    if not step_name or len(step_name) > 120:
        raise ApiError(422, "run_step_name_invalid", "Run step name is invalid.")
    metadata_json = metadata or {}
    _validate_step_metadata(metadata_json)
    next_sequence = (
        session.scalar(
            select(func.max(AgentRunStep.sequence_number)).where(
                AgentRunStep.run_id == run_id
            )
        )
        or 0
    ) + 1
    step = AgentRunStep(
        run_id=run_id,
        sequence_number=next_sequence,
        step_name=step_name,
        status=status,
        metadata_json=metadata_json,
    )
    session.add(step)
    session.flush()
    return step


def cancel_run(session: Session, *, owner_user_id: str, run_id: str) -> AgentRun:
    run = get_run(session, owner_user_id=owner_user_id, run_id=run_id)
    if run.status in TERMINAL_RUN_STATUSES:
        raise ApiError(409, "run_not_cancellable", "Run is not cancellable.")
    run.status = "cancelled"
    run.cancelled_at = utc_now()
    if run.queue_job_id is not None:
        try:
            cancel_queue_job(session, job_id=run.queue_job_id, now=run.cancelled_at)
        except QueueError:
            run.failure_reason_code = "queue_cancel_unavailable"
    session.flush()
    return run


def _validate_timeout(timeout_seconds: int) -> None:
    if not 30 <= timeout_seconds <= 3600:
        raise ApiError(422, "run_timeout_invalid", "Run timeout is invalid.")


def _validate_reference_payload(payload: dict[str, Any]) -> None:
    for key, value in payload.items():
        if any(fragment in key.lower() for fragment in _SENSITIVE_PAYLOAD_KEYS):
            raise ApiError(500, "run_payload_not_minimized", "Run payload is not safe.")
        if not isinstance(value, str) or len(value) > 160:
            raise ApiError(500, "run_payload_not_minimized", "Run payload is not safe.")


def _validate_step_metadata(metadata: dict[str, Any]) -> None:
    for key, value in metadata.items():
        if any(fragment in key.lower() for fragment in _SENSITIVE_PAYLOAD_KEYS):
            raise ApiError(
                500,
                "run_step_metadata_not_minimized",
                "Run step metadata is not safe.",
            )
        if not isinstance(value, str | int | bool | type(None)):
            raise ApiError(
                500,
                "run_step_metadata_not_minimized",
                "Run step metadata is not safe.",
            )
        if isinstance(value, str) and len(value) > 160:
            raise ApiError(
                500,
                "run_step_metadata_not_minimized",
                "Run step metadata is not safe.",
            )


def _apply_cursor(query: Any, cursor: str | None) -> Any:
    if cursor is None:
        return query
    values = decode_cursor(cursor)
    created_at = datetime.fromisoformat(values["created_at"])
    run_id = values["run_id"]
    return query.where(
        (AgentRun.created_at > created_at)
        | ((AgentRun.created_at == created_at) & (AgentRun.run_id > run_id))
    )
