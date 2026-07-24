from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from atlas_api.db.base import utc_now
from atlas_api.models.agent import AgentActivityEvent


def record_agent_activity(
    session: Session,
    *,
    agent_id: str | None,
    event_type: str,
    summary: str,
    severity: str = "info",
    source_type: str = "agent",
    source_id: str | None = None,
    actor_type: str = "system",
    actor_id: str | None = None,
    correlation_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    occurred_at: datetime | None = None,
) -> AgentActivityEvent:
    event = AgentActivityEvent(
        agent_id=agent_id,
        source_type=source_type,
        source_id=source_id or agent_id or "atlas",
        event_type=event_type,
        severity=severity,
        summary=summary[:500],
        correlation_id=correlation_id,
        actor_type=actor_type,
        actor_id=actor_id,
        metadata_json=_json_safe(metadata or {}),
        occurred_at=occurred_at or utc_now(),
    )
    session.add(event)
    return event


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value
