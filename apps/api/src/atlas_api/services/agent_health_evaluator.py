from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from atlas_api.db.base import utc_now
from atlas_api.models.agent import (
    AgentAlert,
    AgentExecution,
    AgentHealthEvaluatorLease,
    AgentHeartbeat,
    AgentRegistration,
)
from atlas_api.services.agent_activity import record_agent_activity
from atlas_api.services.agent_alerts import (
    maybe_resolve_security_ingestion_alerts,
    open_or_update_alert,
    resolve_active_alert,
)

EVALUATOR_LEASE_NAME = "agent-health-evaluator"
EVALUATOR_TICK_INTERVAL_SECONDS = 30
EVALUATOR_LEASE_TTL_SECONDS = 90
EVALUATOR_BATCH_SIZE = 100
EVALUATOR_STALE_AFTER_SECONDS = 180


@dataclass(frozen=True)
class AgentHealthEvaluationResult:
    acquired: bool
    processed_count: int
    opened_alerts: int
    resolved_alerts: int


def record_evaluator_error(
    session: Session,
    *,
    holder_id: str,
    error_code: str,
    now: datetime | None = None,
) -> None:
    observed_at = now or utc_now()
    lease = session.get(AgentHealthEvaluatorLease, EVALUATOR_LEASE_NAME)
    if lease is None:
        lease = AgentHealthEvaluatorLease(
            lease_name=EVALUATOR_LEASE_NAME,
            holder_id=holder_id,
            lease_expires_at=observed_at
            + timedelta(seconds=EVALUATOR_LEASE_TTL_SECONDS),
            last_processed_count=0,
        )
        session.add(lease)
    lease.holder_id = holder_id
    lease.last_error_at = observed_at
    lease.last_error_code = error_code[:120]
    session.flush()


def evaluate_agent_health_once(
    session: Session,
    *,
    holder_id: str,
    now: datetime | None = None,
) -> AgentHealthEvaluationResult:
    observed_at = now or utc_now()
    lease = _acquire_lease(session, holder_id=holder_id, now=observed_at)
    if lease is None:
        return AgentHealthEvaluationResult(
            acquired=False,
            processed_count=0,
            opened_alerts=0,
            resolved_alerts=0,
        )

    agents = list(
        session.scalars(
            select(AgentRegistration)
            .where(AgentRegistration.active_surface_visible.is_(True))
            .order_by(AgentRegistration.display_name)
            .limit(EVALUATOR_BATCH_SIZE)
        )
    )
    opened_alerts = 0
    resolved_alerts = 0
    for agent in agents:
        previous_observed_health = agent.observed_health
        observed_health = derive_observed_health(agent, now=observed_at)
        if previous_observed_health != observed_health:
            agent.observed_health = observed_health
            agent.health_status = observed_health
            agent.health_checked_at = observed_at
            record_agent_activity(
                session,
                agent_id=agent.agent_id,
                event_type="agent.observed_health.transition",
                severity=_health_transition_severity(observed_health),
                summary=(
                    f"Observed health changed from {previous_observed_health} "
                    f"to {observed_health}."
                ),
                metadata={
                    "from": previous_observed_health,
                    "to": observed_health,
                },
                occurred_at=observed_at,
            )
        else:
            agent.health_checked_at = observed_at

        opened, resolved = _evaluate_alerts_for_agent(
            session,
            agent=agent,
            observed_health=observed_health,
            now=observed_at,
        )
        opened_alerts += opened
        resolved_alerts += resolved

    lease.last_completed_at = observed_at
    lease.last_error_code = None
    lease.last_error_at = None
    lease.last_processed_count = len(agents)
    lease.lease_expires_at = observed_at + timedelta(
        seconds=EVALUATOR_LEASE_TTL_SECONDS
    )
    session.flush()
    return AgentHealthEvaluationResult(
        acquired=True,
        processed_count=len(agents),
        opened_alerts=opened_alerts,
        resolved_alerts=resolved_alerts,
    )


def derive_observed_health(agent: AgentRegistration, *, now: datetime) -> str:
    if agent.lifecycle_status == "disconnected":
        return "disconnected"
    if agent.lifecycle_status == "archived":
        return "archived"
    if agent.monitoring_mode == "activity_only":
        return "not_monitored"
    if agent.last_heartbeat_received_at is None:
        return "never_seen"

    interval = agent.heartbeat_interval_seconds or 60
    online_after = timedelta(seconds=max(2 * interval, 120))
    offline_after = timedelta(seconds=max(5 * interval, 300))
    last_contact = _aware_utc(agent.last_heartbeat_received_at)
    if now <= last_contact + online_after:
        return "online"
    if now <= last_contact + offline_after:
        return "late"
    return "offline"


def evaluator_freshness(
    session: Session,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    observed_at = now or utc_now()
    lease = session.get(AgentHealthEvaluatorLease, EVALUATOR_LEASE_NAME)
    if lease is None or lease.last_completed_at is None:
        return {
            "status": "never_completed",
            "last_completed_at": None,
            "stale_after_seconds": EVALUATOR_STALE_AFTER_SECONDS,
        }
    last_completed_at = _aware_utc(lease.last_completed_at)
    stale = last_completed_at < observed_at - timedelta(
        seconds=EVALUATOR_STALE_AFTER_SECONDS
    )
    return {
        "status": "stale" if stale else "fresh",
        "last_completed_at": lease.last_completed_at,
        "stale_after_seconds": EVALUATOR_STALE_AFTER_SECONDS,
    }


def _acquire_lease(
    session: Session,
    *,
    holder_id: str,
    now: datetime,
) -> AgentHealthEvaluatorLease | None:
    lease = session.get(AgentHealthEvaluatorLease, EVALUATOR_LEASE_NAME)
    if lease is None:
        lease = AgentHealthEvaluatorLease(
            lease_name=EVALUATOR_LEASE_NAME,
            holder_id=holder_id,
            lease_expires_at=now + timedelta(seconds=EVALUATOR_LEASE_TTL_SECONDS),
            last_started_at=now,
            last_processed_count=0,
        )
        session.add(lease)
        session.flush()
        return lease

    expires_at = _aware_utc(lease.lease_expires_at) if lease.lease_expires_at else None
    if lease.holder_id not in {None, holder_id} and (
        expires_at is not None and expires_at > now
    ):
        return None
    lease.holder_id = holder_id
    lease.lease_expires_at = now + timedelta(seconds=EVALUATOR_LEASE_TTL_SECONDS)
    lease.last_started_at = now
    return lease


def _evaluate_alerts_for_agent(
    session: Session,
    *,
    agent: AgentRegistration,
    observed_health: str,
    now: datetime,
) -> tuple[int, int]:
    opened = 0
    resolved = 0
    opened += _evaluate_missed_heartbeat_alert(
        session,
        agent=agent,
        observed_health=observed_health,
        now=now,
    )
    resolved += _resolve_missed_heartbeat_alert(
        session,
        agent=agent,
        observed_health=observed_health,
        now=now,
    )
    check_opened, check_resolved = _evaluate_failed_check_alerts(
        session,
        agent=agent,
        now=now,
    )
    opened += check_opened
    resolved += check_resolved
    execution_opened, execution_resolved = _evaluate_repeated_failure_alert(
        session,
        agent=agent,
        now=now,
    )
    opened += execution_opened
    resolved += execution_resolved
    opened += _evaluate_version_mismatch_alert(session, agent=agent, now=now)
    resolved += _resolve_version_mismatch_alert(session, agent=agent, now=now)
    opened += _evaluate_environment_mismatch_alert(session, agent=agent, now=now)
    resolved += _resolve_environment_mismatch_alert(session, agent=agent, now=now)
    before = _active_alert_count(session, agent.agent_id)
    maybe_resolve_security_ingestion_alerts(session, agent_id=agent.agent_id, now=now)
    after = _active_alert_count(session, agent.agent_id)
    if after < before:
        resolved += before - after
    return opened, resolved


def _evaluate_missed_heartbeat_alert(
    session: Session,
    *,
    agent: AgentRegistration,
    observed_health: str,
    now: datetime,
) -> int:
    if observed_health not in {"late", "offline"}:
        return 0
    _, opened = open_or_update_alert(
        session,
        agent_id=agent.agent_id,
        condition_key=f"agent:{agent.agent_id}:missed-heartbeat",
        severity="critical" if observed_health == "offline" else "warning",
        evidence={
            "observed_health": observed_health,
            "last_heartbeat_received_at": agent.last_heartbeat_received_at,
        },
        summary=f"Agent heartbeat is {observed_health}.",
        now=now,
    )
    return int(opened)


def _resolve_missed_heartbeat_alert(
    session: Session,
    *,
    agent: AgentRegistration,
    observed_health: str,
    now: datetime,
) -> int:
    if observed_health not in {"online", "disconnected", "archived"}:
        return 0
    resolved = resolve_active_alert(
        session,
        agent_id=agent.agent_id,
        condition_key=f"agent:{agent.agent_id}:missed-heartbeat",
        reason=f"observed_health_{observed_health}",
        now=now,
    )
    return int(resolved is not None)


def _evaluate_failed_check_alerts(
    session: Session,
    *,
    agent: AgentRegistration,
    now: datetime,
) -> tuple[int, int]:
    latest = _latest_heartbeat(session, agent.agent_id)
    if latest is None:
        return 0, 0
    opened = 0
    resolved = 0
    failing_checks = {
        str(check.get("name")): check
        for check in latest.checks_json
        if check.get("status") in {"degraded", "unhealthy"}
    }
    for check_name, check in failing_checks.items():
        _, was_opened = open_or_update_alert(
            session,
            agent_id=agent.agent_id,
            condition_key=f"agent:{agent.agent_id}:check:{check_name}",
            severity="error" if check.get("status") == "unhealthy" else "warning",
            evidence={"check": check, "heartbeat_id": latest.heartbeat_id},
            summary=f"Agent check {check_name} is {check.get('status')}.",
            now=now,
        )
        opened += int(was_opened)

    active_check_alerts = list(
        session.scalars(
            select(AgentAlert).where(
                AgentAlert.agent_id == agent.agent_id,
                AgentAlert.status.in_(("open", "acknowledged")),
                AgentAlert.condition_key.like(f"agent:{agent.agent_id}:check:%"),
            )
        )
    )
    for alert in active_check_alerts:
        check_name = alert.condition_key.rsplit(":check:", 1)[-1]
        if check_name in failing_checks:
            continue
        if _latest_check_is_healthy(latest, check_name) or _check_absent_for_last_three(
            session,
            agent.agent_id,
            check_name,
        ):
            resolved += int(
                resolve_active_alert(
                    session,
                    agent_id=agent.agent_id,
                    condition_key=alert.condition_key,
                    reason="check_recovered_or_absent",
                    now=now,
                )
                is not None
            )
    return opened, resolved


def _evaluate_repeated_failure_alert(
    session: Session,
    *,
    agent: AgentRegistration,
    now: datetime,
) -> tuple[int, int]:
    recent_failed = list(
        session.scalars(
            select(AgentExecution)
            .where(
                AgentExecution.agent_id == agent.agent_id,
                AgentExecution.status == "failed",
                AgentExecution.terminal_at >= now - timedelta(minutes=30),
            )
            .order_by(AgentExecution.terminal_at.desc())
        )
    )
    condition_key = f"agent:{agent.agent_id}:execution:repeated-failure"
    opened = 0
    if len(recent_failed) >= 3:
        _, was_opened = open_or_update_alert(
            session,
            agent_id=agent.agent_id,
            condition_key=condition_key,
            severity="error",
            evidence={
                "failed_execution_count": len(recent_failed),
                "window_minutes": 30,
            },
            summary="Agent reported repeated failed executions.",
            now=now,
        )
        opened = int(was_opened)

    latest_failed = session.scalar(
        select(AgentExecution)
        .where(
            AgentExecution.agent_id == agent.agent_id,
            AgentExecution.status == "failed",
        )
        .order_by(AgentExecution.terminal_at.desc())
    )
    resolved = 0
    if latest_failed is None or (
        latest_failed.terminal_at is not None
        and _aware_utc(latest_failed.terminal_at) < now - timedelta(minutes=60)
    ):
        resolved = int(
            resolve_active_alert(
                session,
                agent_id=agent.agent_id,
                condition_key=condition_key,
                reason="no_failed_execution_for_60_minutes",
                now=now,
            )
            is not None
        )
    return opened, resolved


def _evaluate_version_mismatch_alert(
    session: Session,
    *,
    agent: AgentRegistration,
    now: datetime,
) -> int:
    if not agent.expected_version or not agent.last_agent_version:
        return 0
    if agent.expected_version == agent.last_agent_version:
        return 0
    _, opened = open_or_update_alert(
        session,
        agent_id=agent.agent_id,
        condition_key=f"agent:{agent.agent_id}:version-mismatch",
        severity="warning",
        evidence={
            "expected_version": agent.expected_version,
            "last_agent_version": agent.last_agent_version,
        },
        summary="Agent reported a version different from the owner expectation.",
        now=now,
    )
    return int(opened)


def _resolve_version_mismatch_alert(
    session: Session,
    *,
    agent: AgentRegistration,
    now: datetime,
) -> int:
    if agent.expected_version and agent.last_agent_version != agent.expected_version:
        return 0
    return int(
        resolve_active_alert(
            session,
            agent_id=agent.agent_id,
            condition_key=f"agent:{agent.agent_id}:version-mismatch",
            reason="version_matches_or_expectation_cleared",
            now=now,
        )
        is not None
    )


def _evaluate_environment_mismatch_alert(
    session: Session,
    *,
    agent: AgentRegistration,
    now: datetime,
) -> int:
    latest = _latest_heartbeat(session, agent.agent_id)
    if latest is None or latest.environment == agent.environment:
        return 0
    _, opened = open_or_update_alert(
        session,
        agent_id=agent.agent_id,
        condition_key=f"agent:{agent.agent_id}:environment-mismatch",
        severity="warning",
        evidence={
            "expected_environment": agent.environment,
            "reported_environment": latest.environment,
        },
        summary="Agent reported telemetry from a different environment.",
        now=now,
    )
    return int(opened)


def _resolve_environment_mismatch_alert(
    session: Session,
    *,
    agent: AgentRegistration,
    now: datetime,
) -> int:
    latest = _latest_heartbeat(session, agent.agent_id)
    if latest is not None and latest.environment != agent.environment:
        return 0
    return int(
        resolve_active_alert(
            session,
            agent_id=agent.agent_id,
            condition_key=f"agent:{agent.agent_id}:environment-mismatch",
            reason="environment_matches",
            now=now,
        )
        is not None
    )


def _latest_heartbeat(session: Session, agent_id: str) -> AgentHeartbeat | None:
    return session.scalar(
        select(AgentHeartbeat)
        .where(AgentHeartbeat.agent_id == agent_id)
        .order_by(AgentHeartbeat.received_at.desc())
    )


def _latest_check_is_healthy(heartbeat: AgentHeartbeat, check_name: str) -> bool:
    return any(
        check.get("name") == check_name and check.get("status") == "healthy"
        for check in heartbeat.checks_json
    )


def _check_absent_for_last_three(
    session: Session,
    agent_id: str,
    check_name: str,
) -> bool:
    recent = list(
        session.scalars(
            select(AgentHeartbeat)
            .where(AgentHeartbeat.agent_id == agent_id)
            .order_by(AgentHeartbeat.received_at.desc())
            .limit(3)
        )
    )
    if len(recent) < 3:
        return False
    return all(
        all(check.get("name") != check_name for check in heartbeat.checks_json)
        for heartbeat in recent
    )


def _active_alert_count(session: Session, agent_id: str) -> int:
    return session.scalar(
        select(func.count(AgentAlert.alert_id)).where(
            AgentAlert.agent_id == agent_id,
            AgentAlert.status.in_(("open", "acknowledged")),
        )
    ) or 0


def _health_transition_severity(observed_health: str) -> str:
    if observed_health == "offline":
        return "critical"
    if observed_health == "late":
        return "warning"
    return "info"


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
