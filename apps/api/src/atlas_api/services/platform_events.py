from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.events import (
    DENIED_WEBHOOK_PAYLOAD_KEY_PARTS,
    PHASE5_WEBHOOK_EVENT_TYPES,
    PHASE5_WEBHOOK_PAYLOAD_SCHEMAS,
    WEBHOOK_EVENT_APPROVAL_DECIDED,
    WEBHOOK_EVENT_APPROVAL_PENDING,
    WEBHOOK_EVENT_KNOWLEDGE_FACT_RECONFIRMATION_REQUIRED,
    WEBHOOK_EVENT_KNOWLEDGE_QUESTION_ANSWERED,
    WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING,
    WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING,
    WEBHOOK_EVENT_RUN_STATE_CHANGED,
)
from atlas_api.models.webhook import WebhookDeliveryAttempt, WebhookSubscription
from atlas_api.services.webhook_delivery import (
    WebhookAuditHook,
    WebhookError,
    enqueue_notification,
)

MAX_PLATFORM_EVENT_VALUE_LENGTH = 240


@dataclass(frozen=True)
class PlatformWebhookEvent:
    event_type: str
    payload: dict[str, str]


def approval_pending_event(
    *,
    approval_id: str,
    status: str = "pending",
) -> PlatformWebhookEvent:
    return build_platform_webhook_event(
        WEBHOOK_EVENT_APPROVAL_PENDING,
        resource_id=approval_id,
        resource_type="approval",
        status=status,
        reconciliation_path=f"/api/v1/approvals/{approval_id}/evidence",
    )


def approval_decided_event(
    *,
    approval_id: str,
    status: str,
    decision_channel: str,
) -> PlatformWebhookEvent:
    return build_platform_webhook_event(
        WEBHOOK_EVENT_APPROVAL_DECIDED,
        decision_channel=decision_channel,
        resource_id=approval_id,
        resource_type="approval",
        status=status,
        reconciliation_path=f"/api/v1/approvals/{approval_id}/evidence",
    )


def message_held_for_manual_handling_event(
    *,
    manual_handling_id: str,
    status: str,
    reason_category: str,
    sensitivity_classification: str,
) -> PlatformWebhookEvent:
    return build_platform_webhook_event(
        WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING,
        reason_category=reason_category,
        resource_id=manual_handling_id,
        resource_type="manual_handling",
        sensitivity_classification=sensitivity_classification,
        status=status,
        reconciliation_path=f"/api/v1/manual-handling/{manual_handling_id}",
    )


def knowledge_question_pending_event(
    *,
    question_id: str,
    fact_key: str,
    status: str = "pending",
) -> PlatformWebhookEvent:
    return build_platform_webhook_event(
        WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING,
        fact_key=fact_key,
        resource_id=question_id,
        resource_type="knowledge_question",
        status=status,
        reconciliation_path=f"/api/v1/knowledge/questions/{question_id}",
    )


def knowledge_question_answered_event(
    *,
    question_id: str,
    fact_key: str,
    revision_id: str,
    status: str = "answered",
) -> PlatformWebhookEvent:
    return build_platform_webhook_event(
        WEBHOOK_EVENT_KNOWLEDGE_QUESTION_ANSWERED,
        fact_key=fact_key,
        resource_id=question_id,
        resource_type="knowledge_question",
        revision_id=revision_id,
        status=status,
        reconciliation_path=f"/api/v1/knowledge/questions/{question_id}",
    )


def knowledge_fact_reconfirmation_required_event(
    *,
    knowledge_fact_id: str,
    fact_key: str,
    reason_category: str,
    status: str = "reconfirmation_required",
) -> PlatformWebhookEvent:
    return build_platform_webhook_event(
        WEBHOOK_EVENT_KNOWLEDGE_FACT_RECONFIRMATION_REQUIRED,
        fact_key=fact_key,
        reason_category=reason_category,
        resource_id=knowledge_fact_id,
        resource_type="knowledge_fact",
        status=status,
        reconciliation_path=f"/api/v1/knowledge/facts/{knowledge_fact_id}",
    )


def run_state_changed_event(
    *,
    run_id: str,
    status: str,
    trigger_source: str,
) -> PlatformWebhookEvent:
    return build_platform_webhook_event(
        WEBHOOK_EVENT_RUN_STATE_CHANGED,
        resource_id=run_id,
        resource_type="agent_run",
        status=status,
        trigger_source=trigger_source,
        reconciliation_path=f"/api/v1/runs/{run_id}",
    )


def build_platform_webhook_event(
    event_type: str,
    **payload: str | None,
) -> PlatformWebhookEvent:
    normalized_payload = {
        key: value for key, value in payload.items() if value is not None
    }
    _validate_platform_event_payload(event_type, normalized_payload)
    return PlatformWebhookEvent(event_type=event_type, payload=normalized_payload)


def enqueue_platform_webhook_event(
    session: Session,
    event: PlatformWebhookEvent,
    *,
    correlation_id: str,
    now: datetime,
    settings: Settings,
    audit_hook: WebhookAuditHook | None = None,
) -> list[WebhookDeliveryAttempt]:
    _validate_platform_event_payload(event.event_type, event.payload)
    subscriptions = session.scalars(
        select(WebhookSubscription).where(
            WebhookSubscription.status == "active",
            WebhookSubscription.event_type == event.event_type,
        )
    ).all()
    return [
        enqueue_notification(
            session,
            subscription_id=subscription.webhook_subscription_id,
            event_type=event.event_type,
            payload=event.payload,
            correlation_id=correlation_id,
            now=now,
            settings=settings,
            audit_hook=audit_hook,
        )
        for subscription in subscriptions
    ]


def _validate_platform_event_payload(
    event_type: str,
    payload: dict[str, str],
) -> None:
    required_keys = PHASE5_WEBHOOK_PAYLOAD_SCHEMAS.get(event_type)
    if event_type not in PHASE5_WEBHOOK_EVENT_TYPES or required_keys is None:
        raise WebhookError("platform_event_type_invalid")
    if set(payload) != required_keys:
        raise WebhookError("platform_event_payload_invalid")
    if any(
        any(fragment in key.lower() for fragment in DENIED_WEBHOOK_PAYLOAD_KEY_PARTS)
        for key in payload
    ):
        raise WebhookError("platform_event_payload_invalid")
    if not all(
        isinstance(value, str)
        and value
        and len(value) <= MAX_PLATFORM_EVENT_VALUE_LENGTH
        for value in payload.values()
    ):
        raise WebhookError("platform_event_payload_invalid")
