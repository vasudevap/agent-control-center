from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.agent import (
    AgentCredential,
    AgentExecution,
    AgentHeartbeat,
    AgentIngestionRateLimit,
    AgentRegistration,
)
from atlas_api.services.agent_activity import record_agent_activity

MAX_TELEMETRY_BODY_BYTES = 64 * 1024
SUPPORTED_CONTRACT_VERSION = "2026-07-24"
SECRET_KEY_PATTERN = re.compile(
    r"(secret|token|password|credential|api[_-]?key|oauth|private[_-]?key)",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERN = re.compile(
    r"(sk-"
    r"[A-Za-z0-9]{12,}|BEGIN "
    r"PRIVATE KEY|nt"
    r"n_"
    r"[A-Za-z0-9]{8,})"
)
TERMINAL_EXECUTION_STATUSES = frozenset(
    {"succeeded", "failed", "cancelled", "timed_out"}
)
RUNNING_EXECUTION_STATUSES = frozenset({"accepted", "running"})


@dataclass(frozen=True)
class AcceptedHeartbeat:
    heartbeat: AgentHeartbeat
    replayed: bool


@dataclass(frozen=True)
class AcceptedExecution:
    execution: AgentExecution
    created: bool


def require_credential_for_agent(
    session: Session,
    *,
    credential: AgentCredential | None,
    agent_id: str,
) -> tuple[AgentCredential, AgentRegistration]:
    if credential is None:
        raise ApiError(401, "agent_credential_invalid", "Agent credential invalid.")
    if credential.agent_id != agent_id:
        raise ApiError(403, "agent_credential_agent_mismatch", "Agent mismatch.")
    agent = session.get(AgentRegistration, agent_id)
    if agent is None or not agent.active_surface_visible:
        raise ApiError(404, "agent_not_found", "Agent was not found.")
    if agent.lifecycle_status in {"disconnected", "archived"}:
        raise ApiError(
            401,
            "agent_lifecycle_rejects_telemetry",
            "Agent lifecycle rejects telemetry.",
        )
    return credential, agent


def accept_heartbeat(
    session: Session,
    *,
    agent: AgentRegistration,
    credential: AgentCredential,
    event_id: str,
    contract_version: str,
    sent_at: datetime,
    environment: str,
    reported_status: Literal["healthy", "degraded", "unhealthy"],
    checks: list[dict[str, Any]],
    agent_version: str | None,
    build_sha: str | None,
    payload: dict[str, Any],
) -> AcceptedHeartbeat:
    _validate_contract_version(contract_version)
    _reject_secret_bearing_payload(payload)
    _consume_rate_limit(session, credential=credential, route_key="telemetry", limit=60)
    _consume_rate_limit(
        session,
        credential=credential,
        route_key="heartbeats",
        limit=30,
    )
    fingerprint = _fingerprint(payload)
    existing = session.scalar(
        select(AgentHeartbeat).where(
            AgentHeartbeat.agent_id == agent.agent_id,
            AgentHeartbeat.event_id == event_id,
        )
    )
    if existing is not None:
        if existing.event_fingerprint != fingerprint:
            raise ApiError(
                409,
                "agent_heartbeat_replay_conflict",
                "Heartbeat event id conflicts with existing telemetry.",
            )
        return AcceptedHeartbeat(heartbeat=existing, replayed=True)

    now = utc_now()
    previous_reported_health = agent.reported_health
    was_pending = agent.lifecycle_status == "pending"
    heartbeat = AgentHeartbeat(
        agent_id=agent.agent_id,
        credential_id=credential.credential_id,
        event_id=event_id,
        event_fingerprint=fingerprint,
        contract_version=contract_version,
        sent_at=sent_at,
        received_at=now,
        agent_version=agent_version,
        build_sha=build_sha,
        environment=environment,
        reported_status=reported_status,
        checks_json=checks,
    )
    session.add(heartbeat)
    agent.last_heartbeat_received_at = now
    agent.last_activity_at = now
    agent.reported_health = reported_status
    agent.last_agent_version = agent_version
    agent.last_build_sha = build_sha
    if was_pending:
        agent.lifecycle_status = "connected"
        agent.first_connected_at = now
        record_agent_activity(
            session,
            agent_id=agent.agent_id,
            event_type="agent.first_connected",
            summary="Agent sent its first accepted heartbeat.",
            severity="info",
            source_type="agent_heartbeat",
            source_id=event_id,
            occurred_at=now,
        )
    if previous_reported_health != reported_status and reported_status in {
        "degraded",
        "unhealthy",
    }:
        record_agent_activity(
            session,
            agent_id=agent.agent_id,
            event_type="agent.reported_health.transition",
            summary=(
                f"Reported health changed from {previous_reported_health} "
                f"to {reported_status}."
            ),
            severity="critical" if reported_status == "unhealthy" else "warning",
            source_type="agent_heartbeat",
            source_id=event_id,
            metadata={
                "from": previous_reported_health,
                "to": reported_status,
            },
            occurred_at=now,
        )
    session.flush()
    return AcceptedHeartbeat(heartbeat=heartbeat, replayed=False)


def accept_execution(
    session: Session,
    *,
    agent: AgentRegistration,
    credential: AgentCredential,
    external_execution_id: str,
    contract_version: str,
    representation_hash: str,
    status: str,
    trigger: str,
    payload: dict[str, Any],
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
    duration_ms: int | None = None,
    summary: str | None = None,
    error_code: str | None = None,
    correlation_id: str | None = None,
    agent_version: str | None = None,
    build_sha: str | None = None,
) -> AcceptedExecution:
    _validate_contract_version(contract_version)
    _reject_secret_bearing_payload(payload)
    _consume_rate_limit(session, credential=credential, route_key="telemetry", limit=60)
    now = utc_now()
    terminal_at = now if status in TERMINAL_EXECUTION_STATUSES else None
    existing = session.scalar(
        select(AgentExecution).where(
            AgentExecution.agent_id == agent.agent_id,
            AgentExecution.external_execution_id == external_execution_id,
        )
    )
    if existing is not None:
        if existing.representation_hash == representation_hash:
            return AcceptedExecution(execution=existing, created=False)
        if (
            existing.status in TERMINAL_EXECUTION_STATUSES
            and status in RUNNING_EXECUTION_STATUSES
        ):
            raise ApiError(
                409,
                "agent_execution_terminal_regression",
                "Terminal executions cannot return to running states.",
            )
        if (
            existing.started_at is not None
            and started_at is not None
            and not _same_instant(started_at, existing.started_at)
        ):
            raise ApiError(
                409,
                "agent_execution_immutable_timestamp_conflict",
                "Execution immutable timestamps conflict.",
            )
        if existing.started_at is None and started_at is not None:
            existing.started_at = started_at
        previous_status = existing.status
        existing.representation_hash = representation_hash
        existing.status = status
        existing.trigger = trigger
        existing.finished_at = finished_at
        existing.duration_ms = duration_ms
        existing.summary = summary
        existing.error_code = error_code
        existing.correlation_id = correlation_id
        existing.agent_version = agent_version
        existing.build_sha = build_sha
        existing.last_reported_at = now
        existing.terminal_at = terminal_at
        agent.last_activity_at = now
        if (
            previous_status not in TERMINAL_EXECUTION_STATUSES
            and status in TERMINAL_EXECUTION_STATUSES
        ):
            record_agent_activity(
                session,
                agent_id=agent.agent_id,
                event_type="agent.execution.terminal",
                summary=f"Agent execution {external_execution_id} ended as {status}.",
                severity="error" if status in {"failed", "timed_out"} else "info",
                source_type="agent_execution",
                source_id=external_execution_id,
                correlation_id=correlation_id,
                metadata={"status": status, "trigger": trigger},
                occurred_at=now,
            )
        session.flush()
        return AcceptedExecution(execution=existing, created=False)

    execution = AgentExecution(
        agent_id=agent.agent_id,
        external_execution_id=external_execution_id,
        representation_hash=representation_hash,
        status=status,
        trigger=trigger,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        summary=summary,
        error_code=error_code,
        correlation_id=correlation_id,
        agent_version=agent_version,
        build_sha=build_sha,
        first_reported_at=now,
        last_reported_at=now,
        terminal_at=terminal_at,
    )
    session.add(execution)
    agent.last_activity_at = now
    if status in TERMINAL_EXECUTION_STATUSES:
        record_agent_activity(
            session,
            agent_id=agent.agent_id,
            event_type="agent.execution.terminal",
            summary=f"Agent execution {external_execution_id} ended as {status}.",
            severity="error" if status in {"failed", "timed_out"} else "info",
            source_type="agent_execution",
            source_id=external_execution_id,
            correlation_id=correlation_id,
            metadata={"status": status, "trigger": trigger},
            occurred_at=now,
        )
    session.flush()
    return AcceptedExecution(execution=execution, created=True)


def _validate_contract_version(contract_version: str) -> None:
    if contract_version != SUPPORTED_CONTRACT_VERSION:
        raise ApiError(
            422,
            "agent_contract_version_unsupported",
            "Agent contract version is unsupported.",
        )


def _consume_rate_limit(
    session: Session,
    *,
    credential: AgentCredential,
    route_key: str,
    limit: int,
) -> None:
    now = utc_now()
    window = now.replace(second=0, microsecond=0)
    record = session.get(
        AgentIngestionRateLimit,
        (credential.credential_id, route_key, window),
    )
    if record is None:
        session.add(
            AgentIngestionRateLimit(
                credential_id=credential.credential_id,
                route_key=route_key,
                window_start=window,
                request_count=1,
            )
        )
        return
    if record.request_count >= limit:
        raise ApiError(429, "agent_ingestion_rate_limited", "Rate limit exceeded.")
    record.request_count += 1


def _fingerprint(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def _same_instant(left: datetime, right: datetime) -> bool:
    return _comparable_datetime(left) == _comparable_datetime(right)


def _comparable_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _reject_secret_bearing_payload(payload: Any) -> None:
    if _contains_secret(payload):
        raise ApiError(
            422,
            "agent_telemetry_secret_rejected",
            "Telemetry contains secret-bearing content.",
        )


def _contains_secret(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            SECRET_KEY_PATTERN.search(str(key)) is not None or _contains_secret(nested)
            for key, nested in value.items()
        )
    if isinstance(value, list):
        return any(_contains_secret(item) for item in value)
    if isinstance(value, str):
        return SECRET_VALUE_PATTERN.search(value) is not None
    return False
