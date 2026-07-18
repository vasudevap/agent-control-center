from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from atlas_api.core.correlation import get_correlation_id
from atlas_api.core.observability import sanitize_metadata
from atlas_api.db.base import utc_now
from atlas_api.models.audit import AuditEvent
from atlas_api.services.queue import QueueAuditEvent
from atlas_api.services.scheduler import ScheduleAuditEvent
from atlas_api.services.webhook_delivery import WebhookAuditEvent


class AuditError(ValueError):
    pass


@dataclass(frozen=True)
class AuditEventInput:
    event_type: str
    actor_type: str
    channel: str
    action: str
    resource_type: str
    result: str
    actor_id: str | None = None
    resource_id: str | None = None
    reason_code: str | None = None
    correlation_id: str | None = None
    metadata: Mapping[str, Any] | None = None
    occurred_at: datetime | None = None


def record_audit_event(session: Session, event: AuditEventInput) -> AuditEvent:
    _validate(event)
    audit_event = AuditEvent(
        event_type=event.event_type,
        actor_type=event.actor_type,
        actor_id=event.actor_id,
        channel=event.channel,
        action=event.action,
        resource_type=event.resource_type,
        resource_id=event.resource_id,
        result=event.result,
        reason_code=event.reason_code,
        correlation_id=event.correlation_id
        or get_correlation_id()
        or "correlation_unavailable",
        redaction_state="metadata_only",
        metadata_json=sanitize_metadata(event.metadata),
        occurred_at=event.occurred_at or utc_now(),
    )
    session.add(audit_event)
    session.flush()
    return audit_event


def record_queue_audit_event(
    session: Session,
    event: QueueAuditEvent,
    *,
    correlation_id: str | None = None,
) -> AuditEvent:
    return record_audit_event(
        session,
        AuditEventInput(
            event_type=event.event_type,
            actor_type="service",
            actor_id="queue",
            channel="service",
            action=_action_from_event_type(event.event_type),
            resource_type="queue_job",
            resource_id=event.job_id,
            result="succeeded",
            correlation_id=correlation_id,
            metadata={"queue_job_id": event.job_id, **event.metadata},
        ),
    )


def record_schedule_audit_event(
    session: Session,
    event: ScheduleAuditEvent,
    *,
    correlation_id: str | None = None,
) -> AuditEvent:
    return record_audit_event(
        session,
        AuditEventInput(
            event_type=event.event_type,
            actor_type="service",
            actor_id="scheduler",
            channel="service",
            action=_action_from_event_type(event.event_type),
            resource_type="job_schedule",
            resource_id=event.schedule_id,
            result="succeeded",
            correlation_id=correlation_id,
            metadata={"schedule_id": event.schedule_id, **event.metadata},
        ),
    )


def record_webhook_audit_event(
    session: Session,
    event: WebhookAuditEvent,
    *,
    correlation_id: str | None = None,
) -> AuditEvent:
    result = "succeeded" if event.event_type.endswith("_delivered") else "pending"
    if event.event_type.endswith("_failed"):
        result = "failed"
    error_code = event.metadata.get("error_code")
    reason_code = error_code if isinstance(error_code, str) else None
    return record_audit_event(
        session,
        AuditEventInput(
            event_type=event.event_type,
            actor_type="service",
            actor_id="webhook_delivery",
            channel="service",
            action=_action_from_event_type(event.event_type),
            resource_type="webhook_delivery_attempt",
            resource_id=event.delivery_attempt_id,
            result=result,
            reason_code=reason_code,
            correlation_id=correlation_id,
            metadata=event.metadata,
        ),
    )


def _action_from_event_type(event_type: str) -> str:
    return event_type.rsplit(".", maxsplit=1)[-1]


def _validate(event: AuditEventInput) -> None:
    for field_name in (
        "event_type",
        "actor_type",
        "channel",
        "action",
        "resource_type",
        "result",
    ):
        value = getattr(event, field_name)
        if not isinstance(value, str) or not value or len(value) > 120:
            raise AuditError("audit_event_invalid")
    if event.reason_code is not None and len(event.reason_code) > 120:
        raise AuditError("audit_event_invalid")
