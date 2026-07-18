from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.agent import AgentRegistration
from atlas_api.models.gmail_message import GmailSendOutcomeRecord
from atlas_api.models.run import AgentRun, AgentRunStep
from atlas_api.models.webhook import WebhookDeliveryAttempt, WebhookSubscription
from atlas_api.services.agent_registry import create_agent_registration
from atlas_api.services.audit import (
    AuditEventInput,
    record_audit_event,
    record_webhook_audit_event,
)
from atlas_api.services.gmail_messages import (
    GMAIL_AGENT_ID,
    FakeGmailProvider,
    GmailRetrievalPolicy,
    GmailRetrievalResult,
    GmailSuppressionWebhookContext,
    retrieve_and_classify_messages,
)
from atlas_api.services.platform_events import (
    PlatformWebhookEvent,
    approval_pending_event,
    enqueue_platform_webhook_event,
    run_state_changed_event,
)
from atlas_api.services.runs import (
    complete_run,
    create_manual_run,
    create_scheduled_run,
    fail_run,
    record_run_step,
    start_run,
)
from atlas_api.services.webhook_delivery import (
    WebhookAuditEvent,
    enqueue_notification,
)

GMAIL_AGENT_SLUG = "gmail-agent"
GMAIL_AGENT_VERSION = "0.1.0"
WEBHOOK_EVENT_SEND_OUTCOME = "send.outcome"


@dataclass(frozen=True)
class GmailOperationalWebhookContext:
    settings: Settings
    correlation_id: str
    now: datetime | None = None


@dataclass(frozen=True)
class GmailRunExecutionResult:
    run: AgentRun
    steps: list[AgentRunStep]
    webhook_attempts: list[WebhookDeliveryAttempt]


def ensure_gmail_agent_registered(session: Session) -> AgentRegistration:
    existing = session.scalar(
        select(AgentRegistration).where(AgentRegistration.slug == GMAIL_AGENT_SLUG)
    )
    if existing is not None:
        return existing
    return create_agent_registration(
        session,
        slug=GMAIL_AGENT_SLUG,
        display_name="Gmail Agent",
        description=(
            "Triage eligible Gmail messages and prepare safe governed responses."
        ),
        version=GMAIL_AGENT_VERSION,
        risk_level="high",
        capabilities=[
            "gmail.eligibility",
            "gmail.classification",
            "gmail.suppression",
            "gmail.low_risk_actions",
            "gmail.ask_instead_of_guess",
            "gmail.draft_generation",
            "gmail.approval_gates",
            "gmail.send_continuation",
        ],
        allowed_tools=[
            "connector.gmail.modify",
            "connector.drive.file",
            "approval.request",
            "knowledge.question",
            "knowledge.fact",
        ],
        required_connectors=["gmail", "drive"],
        configuration_schema_ref="schemas/agents/gmail-agent-v1.json",
        configuration_schema={
            "type": "object",
            "properties": {
                "eligibility_query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 240,
                },
                "max_messages_per_run": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                },
            },
            "required": ["eligibility_query", "max_messages_per_run"],
            "additionalProperties": False,
        },
        supports_manual_run=True,
        supports_scheduled_run=True,
        health_status="healthy",
    )


def create_gmail_manual_run(
    session: Session,
    *,
    owner_user_id: str,
    idempotency_key: str,
    correlation_id: str,
    timeout_seconds: int = 300,
    webhook_context: GmailOperationalWebhookContext | None = None,
) -> AgentRun:
    agent = ensure_gmail_agent_registered(session)
    run = create_manual_run(
        session,
        owner_user_id=owner_user_id,
        agent_id=agent.agent_id,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        timeout_seconds=timeout_seconds,
    )
    _audit_run(
        session,
        run=run,
        action="queue",
        result="succeeded",
        correlation_id=correlation_id,
    )
    _enqueue_run_state(session, run, webhook_context)
    return run


def create_gmail_scheduled_run(
    session: Session,
    *,
    owner_user_id: str,
    idempotency_key: str,
    correlation_id: str,
    scheduled_for: datetime,
    schedule_id: str | None = None,
    timeout_seconds: int = 300,
    webhook_context: GmailOperationalWebhookContext | None = None,
) -> AgentRun:
    agent = ensure_gmail_agent_registered(session)
    run = create_scheduled_run(
        session,
        owner_user_id=owner_user_id,
        agent_id=agent.agent_id,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        scheduled_for=scheduled_for,
        schedule_id=schedule_id,
        timeout_seconds=timeout_seconds,
    )
    _audit_run(
        session,
        run=run,
        action="queue",
        result="succeeded",
        correlation_id=correlation_id,
    )
    _enqueue_run_state(session, run, webhook_context)
    return run


def execute_gmail_reconciliation_run(
    session: Session,
    *,
    owner_user_id: str,
    run_id: str,
    connection_id: str,
    provider: FakeGmailProvider,
    policy: GmailRetrievalPolicy,
    webhook_context: GmailOperationalWebhookContext | None = None,
    actor_id: str = GMAIL_AGENT_ID,
) -> GmailRunExecutionResult:
    steps: list[AgentRunStep] = []
    webhook_attempts: list[WebhookDeliveryAttempt] = []
    run = start_run(session, owner_user_id=owner_user_id, run_id=run_id)
    webhook_attempts.extend(_enqueue_run_state(session, run, webhook_context))
    _audit_run(
        session,
        run=run,
        action="start",
        result="succeeded",
        correlation_id=run.correlation_id,
    )
    try:
        retrieval = retrieve_and_classify_messages(
            session,
            owner_user_id=owner_user_id,
            connection_id=connection_id,
            provider=provider,
            policy=policy,
            actor_id=actor_id,
            correlation_id=run.correlation_id,
            webhook_context=(
                GmailSuppressionWebhookContext(
                    settings=webhook_context.settings,
                    correlation_id=webhook_context.correlation_id,
                    now=webhook_context.now,
                )
                if webhook_context is not None
                else None
            ),
        )
        steps.extend(_record_gmail_run_steps(session, run=run, retrieval=retrieval))
        run = complete_run(session, owner_user_id=owner_user_id, run_id=run.run_id)
        webhook_attempts.extend(_enqueue_run_state(session, run, webhook_context))
        _audit_run(
            session,
            run=run,
            action="complete",
            result="succeeded",
            correlation_id=run.correlation_id,
        )
    except ApiError as exc:
        steps.append(
            record_run_step(
                session,
                run_id=run.run_id,
                step_name="failure",
                status="failed",
                metadata={"reason_code": exc.code},
            )
        )
        run = fail_run(
            session,
            owner_user_id=owner_user_id,
            run_id=run.run_id,
            reason_code=exc.code,
        )
        webhook_attempts.extend(_enqueue_run_state(session, run, webhook_context))
        _audit_run(
            session,
            run=run,
            action="complete",
            result="failed",
            reason_code=exc.code,
            correlation_id=run.correlation_id,
        )
    session.flush()
    return GmailRunExecutionResult(
        run=run,
        steps=steps,
        webhook_attempts=webhook_attempts,
    )


def enqueue_gmail_approval_pending_event(
    session: Session,
    *,
    approval_id: str,
    webhook_context: GmailOperationalWebhookContext | None,
) -> list[WebhookDeliveryAttempt]:
    if webhook_context is None:
        return []
    return _enqueue_platform_event(
        session,
        approval_pending_event(approval_id=approval_id),
        webhook_context,
    )


def enqueue_gmail_send_outcome_event(
    session: Session,
    *,
    outcome: GmailSendOutcomeRecord,
    webhook_context: GmailOperationalWebhookContext | None,
) -> list[WebhookDeliveryAttempt]:
    if webhook_context is None:
        return []
    event = PlatformWebhookEvent(
        event_type=WEBHOOK_EVENT_SEND_OUTCOME,
        payload={
            "resource_id": outcome.approval_id,
            "resource_type": "approval",
            "status": outcome.outcome,
            "reconciliation_path": f"/api/v1/approvals/{outcome.approval_id}/evidence",
        },
    )
    return _enqueue_direct_event(session, event, webhook_context)


def _record_gmail_run_steps(
    session: Session,
    *,
    run: AgentRun,
    retrieval: GmailRetrievalResult,
) -> list[AgentRunStep]:
    records = retrieval.records
    classified_count = sum(
        1 for record in records if record.classification_status == "classified"
    )
    review_required_count = sum(
        1 for record in records if record.classification_status != "classified"
    )
    held_count = sum(1 for record in records if record.manual_handling_id is not None)
    steps = [
        record_run_step(
            session,
            run_id=run.run_id,
            step_name="eligibility",
            status="succeeded",
            metadata={
                "eligible_count": len(records),
                "skipped_count": retrieval.skipped_count,
            },
        ),
        record_run_step(
            session,
            run_id=run.run_id,
            step_name="classification",
            status="succeeded",
            metadata={
                "classified_count": classified_count,
                "review_required_count": review_required_count,
            },
        ),
        record_run_step(
            session,
            run_id=run.run_id,
            step_name="suppression",
            status="succeeded",
            metadata={
                "suppressed_count": retrieval.suppressed_count,
                "held_count": held_count,
            },
        ),
    ]
    for step_name in (
        "actions",
        "questions",
        "drafts",
        "approvals",
        "continuation",
        "outcomes",
    ):
        steps.append(
            record_run_step(
                session,
                run_id=run.run_id,
                step_name=step_name,
                status="skipped",
                metadata={"count": 0, "reason_code": "not_requested_for_run"},
            )
        )
    _audit_run(
        session,
        run=run,
        action="summarize",
        result="succeeded",
        correlation_id=run.correlation_id,
        metadata={
            "eligible_count": len(records),
            "suppressed_count": retrieval.suppressed_count,
            "held_count": held_count,
        },
    )
    return steps


def _enqueue_run_state(
    session: Session,
    run: AgentRun,
    webhook_context: GmailOperationalWebhookContext | None,
) -> list[WebhookDeliveryAttempt]:
    if webhook_context is None:
        return []
    return _enqueue_platform_event(
        session,
        run_state_changed_event(
            run_id=run.run_id,
            status=run.status,
            trigger_source=run.trigger_source,
        ),
        webhook_context,
    )


def _enqueue_platform_event(
    session: Session,
    event: PlatformWebhookEvent,
    webhook_context: GmailOperationalWebhookContext,
) -> list[WebhookDeliveryAttempt]:
    return enqueue_platform_webhook_event(
        session,
        event,
        correlation_id=webhook_context.correlation_id,
        now=webhook_context.now or utc_now(),
        settings=webhook_context.settings,
        audit_hook=lambda item: _record_webhook(session, item, webhook_context),
    )


def _enqueue_direct_event(
    session: Session,
    event: PlatformWebhookEvent,
    webhook_context: GmailOperationalWebhookContext,
) -> list[WebhookDeliveryAttempt]:
    attempts: list[WebhookDeliveryAttempt] = []
    subscriptions = session.scalars(
        select(WebhookSubscription).where(
            WebhookSubscription.status == "active",
            WebhookSubscription.event_type == event.event_type,
        )
    ).all()
    for subscription in subscriptions:
        attempts.append(
            enqueue_notification(
                session,
                subscription_id=subscription.webhook_subscription_id,
                event_type=event.event_type,
                payload=event.payload,
                correlation_id=webhook_context.correlation_id,
                now=webhook_context.now or utc_now(),
                settings=webhook_context.settings,
                audit_hook=lambda item: _record_webhook(
                    session,
                    item,
                    webhook_context,
                ),
            )
        )
    return attempts


def _record_webhook(
    session: Session,
    event: WebhookAuditEvent,
    webhook_context: GmailOperationalWebhookContext,
) -> None:
    record_webhook_audit_event(
        session,
        event,
        correlation_id=webhook_context.correlation_id,
    )


def _audit_run(
    session: Session,
    *,
    run: AgentRun,
    action: str,
    result: str,
    correlation_id: str,
    reason_code: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    record_audit_event(
        session,
        AuditEventInput(
            event_type=f"gmail.agent_run_{action}",
            actor_type="service",
            actor_id=GMAIL_AGENT_ID,
            channel="service",
            action=action,
            resource_type="agent_run",
            resource_id=run.run_id,
            result=result,
            reason_code=reason_code,
            correlation_id=correlation_id,
            metadata={
                "agent_id": run.agent_id,
                "status": run.status,
                "trigger_source": run.trigger_source,
                **(metadata or {}),
            },
        ),
    )
