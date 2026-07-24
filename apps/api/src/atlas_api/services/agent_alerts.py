from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.agent import AgentAlert
from atlas_api.services.agent_activity import record_agent_activity

SECURITY_INGESTION_QUIET_PERIOD = timedelta(hours=24)


def active_alert_for_condition(
    session: Session,
    *,
    agent_id: str,
    condition_key: str,
) -> AgentAlert | None:
    return session.scalar(
        select(AgentAlert).where(
            AgentAlert.agent_id == agent_id,
            AgentAlert.condition_key == condition_key,
            AgentAlert.status.in_(("open", "acknowledged")),
        )
    )


def open_or_update_alert(
    session: Session,
    *,
    agent_id: str,
    condition_key: str,
    severity: str,
    evidence: dict[str, Any],
    summary: str,
    now: datetime | None = None,
) -> tuple[AgentAlert, bool]:
    observed_at = now or utc_now()
    existing = active_alert_for_condition(
        session,
        agent_id=agent_id,
        condition_key=condition_key,
    )
    if existing is not None:
        existing.severity = severity
        existing.last_seen_at = observed_at
        existing.evidence_json = _json_safe(evidence)
        return existing, False

    alert = AgentAlert(
        agent_id=agent_id,
        condition_key=condition_key,
        status="open",
        severity=severity,
        first_seen_at=observed_at,
        last_seen_at=observed_at,
        evidence_json=_json_safe(evidence),
    )
    session.add(alert)
    session.flush()
    record_agent_activity(
        session,
        agent_id=agent_id,
        event_type="agent.alert.opened",
        severity=severity,
        summary=summary,
        source_type="agent_alert",
        source_id=condition_key,
        metadata={"condition_key": condition_key, "evidence": evidence},
        occurred_at=observed_at,
    )
    return alert, True


def resolve_active_alert(
    session: Session,
    *,
    agent_id: str,
    condition_key: str,
    reason: str,
    now: datetime | None = None,
) -> AgentAlert | None:
    observed_at = now or utc_now()
    alert = active_alert_for_condition(
        session,
        agent_id=agent_id,
        condition_key=condition_key,
    )
    if alert is None:
        return None
    alert.status = "resolved"
    alert.resolved_at = observed_at
    alert.resolved_reason = reason
    record_agent_activity(
        session,
        agent_id=agent_id,
        event_type="agent.alert.resolved",
        severity="info",
        summary=f"Resolved alert {condition_key}.",
        source_type="agent_alert",
        source_id=alert.alert_id,
        metadata={"condition_key": condition_key, "reason": reason},
        occurred_at=observed_at,
    )
    return alert


def acknowledge_alert(
    session: Session,
    *,
    alert_id: str,
    acknowledged_by_user_id: str,
    now: datetime | None = None,
) -> AgentAlert:
    observed_at = now or utc_now()
    alert = session.get(AgentAlert, alert_id)
    if alert is None:
        raise ApiError(404, "agent_alert_not_found", "Agent alert was not found.")
    if alert.status == "resolved":
        raise ApiError(409, "agent_alert_already_resolved", "Alert is resolved.")
    alert.status = "acknowledged"
    alert.acknowledged_at = observed_at
    alert.acknowledged_by_user_id = acknowledged_by_user_id
    record_agent_activity(
        session,
        agent_id=alert.agent_id,
        event_type="agent.alert.acknowledged",
        severity="info",
        summary=f"Acknowledged alert {alert.condition_key}.",
        source_type="agent_alert",
        source_id=alert.alert_id,
        actor_type="owner",
        actor_id=acknowledged_by_user_id,
        metadata={"condition_key": alert.condition_key},
        occurred_at=observed_at,
    )
    return alert


def record_security_ingestion_alert(
    session: Session,
    *,
    agent_id: str,
    category: str,
    reason_code: str,
    now: datetime | None = None,
) -> AgentAlert:
    observed_at = now or utc_now()
    condition_key = f"agent:{agent_id}:security-ingestion"
    alert, _ = open_or_update_alert(
        session,
        agent_id=agent_id,
        condition_key=condition_key,
        severity="critical",
        evidence={"category": category, "reason_code": reason_code},
        summary="Rejected security-sensitive agent telemetry.",
        now=observed_at,
    )
    record_agent_activity(
        session,
        agent_id=agent_id,
        event_type="agent.telemetry.rejected",
        severity="warning",
        summary=f"Rejected agent telemetry: {category}.",
        source_type="agent_alert",
        source_id=condition_key,
        metadata={"category": category, "reason_code": reason_code},
        occurred_at=observed_at,
    )
    return alert


def maybe_resolve_security_ingestion_alerts(
    session: Session,
    *,
    agent_id: str,
    now: datetime,
) -> None:
    condition_key = f"agent:{agent_id}:security-ingestion"
    alert = active_alert_for_condition(
        session,
        agent_id=agent_id,
        condition_key=condition_key,
    )
    if (
        alert is not None
        and alert.status == "acknowledged"
        and _aware_utc(alert.last_seen_at)
        <= _aware_utc(now) - SECURITY_INGESTION_QUIET_PERIOD
    ):
        resolve_active_alert(
            session,
            agent_id=agent_id,
            condition_key=condition_key,
            reason="security_ingestion_quiet_period_elapsed",
            now=now,
        )


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
