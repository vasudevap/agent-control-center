from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.knowledge import KnowledgeAnswer, KnowledgeFact, KnowledgeQuestion
from atlas_api.services.audit import (
    AuditEventInput,
    record_audit_event,
    record_webhook_audit_event,
)
from atlas_api.services.gmail_messages import (
    GMAIL_AGENT_ID,
    ensure_gmail_message_allowed_for_downstream_use,
)
from atlas_api.services.knowledge_facts import STALE_VOLATILE_AFTER, get_fact
from atlas_api.services.knowledge_questions import create_question, submit_answer
from atlas_api.services.platform_events import (
    PlatformWebhookEvent,
    enqueue_platform_webhook_event,
    knowledge_question_answered_event,
    knowledge_question_pending_event,
)
from atlas_api.services.webhook_delivery import WebhookAuditEvent


@dataclass(frozen=True)
class GmailRequiredFact:
    fact_key: str
    question_text: str
    volatile: bool = False


@dataclass(frozen=True)
class GmailKnowledgeRequirementSet:
    scenario: str
    required_facts: tuple[GmailRequiredFact, ...]


@dataclass(frozen=True)
class GmailKnowledgeContext:
    status: str
    fact_revision_ids: list[str]
    question_ids: list[str]


@dataclass(frozen=True)
class GmailKnowledgeWebhookContext:
    settings: Settings
    correlation_id: str
    now: datetime | None = None


GMAIL_DRAFT_REQUIREMENTS = {
    "recruiter_reply": GmailKnowledgeRequirementSet(
        scenario="recruiter_reply",
        required_facts=(
            GmailRequiredFact(
                "gmail.reply.availability",
                "What availability should I use for recruiter replies?",
                volatile=True,
            ),
            GmailRequiredFact(
                "gmail.reply.role_preferences",
                "What role preferences should I mention in recruiter replies?",
            ),
        ),
    ),
    "travel_admin": GmailKnowledgeRequirementSet(
        scenario="travel_admin",
        required_facts=(
            GmailRequiredFact(
                "gmail.travel.loyalty_numbers",
                "Which loyalty numbers should I use for travel email replies?",
            ),
        ),
    ),
}


def prepare_gmail_knowledge_context(
    session: Session,
    *,
    owner_user_id: str,
    gmail_message_record_id: str,
    scenario: str,
    correlation_id: str,
    actor_id: str = GMAIL_AGENT_ID,
    now: datetime | None = None,
    webhook_context: GmailKnowledgeWebhookContext | None = None,
) -> GmailKnowledgeContext:
    record = ensure_gmail_message_allowed_for_downstream_use(
        session,
        owner_user_id=owner_user_id,
        gmail_message_record_id=gmail_message_record_id,
        downstream_use="question",
    )
    requirement_set = _requirement_set(scenario)
    fact_revision_ids: list[str] = []
    question_ids: list[str] = []
    for requirement in requirement_set.required_facts:
        fact = _active_fact(
            session,
            owner_user_id=owner_user_id,
            fact_key=requirement.fact_key,
        )
        if fact is None:
            question = _create_or_get_question(
                session,
                owner_user_id=owner_user_id,
                requirement=requirement,
                source_reference=_source_reference(record.provider_message_reference),
                correlation_id=correlation_id,
                actor_id=actor_id,
                webhook_context=webhook_context,
            )
            question_ids.append(question.knowledge_question_id)
            continue
        _fact, revision = get_fact(
            session,
            owner_user_id=owner_user_id,
            knowledge_fact_id=fact.knowledge_fact_id,
        )
        if _revision_requires_question(revision, now=now or utc_now()):
            question = _create_or_get_question(
                session,
                owner_user_id=owner_user_id,
                requirement=requirement,
                source_reference=_source_reference(record.provider_message_reference),
                correlation_id=correlation_id,
                actor_id=actor_id,
                webhook_context=webhook_context,
            )
            question_ids.append(question.knowledge_question_id)
        else:
            fact_revision_ids.append(revision.knowledge_fact_revision_id)
    status = "ready" if not question_ids else "questions_pending"
    _audit_knowledge_context(
        session,
        actor_id=actor_id,
        result="succeeded",
        correlation_id=correlation_id,
        metadata={
            "resource_id": gmail_message_record_id,
            "resource_type": "gmail_message",
            "facts_checked": len(requirement_set.required_facts),
            "count": len(fact_revision_ids),
            "failure_count": len(question_ids),
            "status": status,
        },
    )
    session.flush()
    return GmailKnowledgeContext(
        status=status,
        fact_revision_ids=fact_revision_ids,
        question_ids=question_ids,
    )


def submit_gmail_knowledge_answer(
    session: Session,
    *,
    owner_user_id: str,
    gmail_message_record_id: str,
    question_id: str,
    answer_text: str,
    correlation_id: str,
    actor_id: str = GMAIL_AGENT_ID,
    webhook_context: GmailKnowledgeWebhookContext | None = None,
) -> tuple[KnowledgeQuestion, KnowledgeAnswer]:
    record = ensure_gmail_message_allowed_for_downstream_use(
        session,
        owner_user_id=owner_user_id,
        gmail_message_record_id=gmail_message_record_id,
        downstream_use="learning",
    )
    question, answer = submit_answer(
        session,
        owner_user_id=owner_user_id,
        question_id=question_id,
        answer_text=answer_text,
        source_reference=_source_reference(record.provider_message_reference),
    )
    _audit_knowledge_answer(
        session,
        question=question,
        answer=answer,
        actor_id=actor_id,
        correlation_id=correlation_id,
        webhook_context=webhook_context,
    )
    session.flush()
    return question, answer


def _requirement_set(scenario: str) -> GmailKnowledgeRequirementSet:
    try:
        return GMAIL_DRAFT_REQUIREMENTS[scenario]
    except KeyError as exc:
        raise ApiError(
            422,
            "gmail_draft_scenario_unknown",
            "Gmail draft scenario is unknown.",
        ) from exc


def _active_fact(
    session: Session,
    *,
    owner_user_id: str,
    fact_key: str,
) -> KnowledgeFact | None:
    return session.scalar(
        select(KnowledgeFact).where(
            KnowledgeFact.owner_user_id == owner_user_id,
            KnowledgeFact.fact_key == fact_key,
            KnowledgeFact.status == "active",
        )
    )


def _revision_requires_question(revision: object, *, now: datetime) -> bool:
    is_volatile = bool(getattr(revision, "is_volatile", False))
    confirmed_at = getattr(revision, "confirmed_at", None)
    if not is_volatile:
        return False
    if not isinstance(confirmed_at, datetime):
        return True
    normalized = (
        confirmed_at.replace(tzinfo=now.tzinfo)
        if confirmed_at.tzinfo is None
        else confirmed_at.astimezone(now.tzinfo)
    )
    return normalized <= now - STALE_VOLATILE_AFTER


def _create_or_get_question(
    session: Session,
    *,
    owner_user_id: str,
    requirement: GmailRequiredFact,
    source_reference: str,
    correlation_id: str,
    actor_id: str,
    webhook_context: GmailKnowledgeWebhookContext | None,
) -> KnowledgeQuestion:
    existing = session.scalar(
        select(KnowledgeQuestion).where(
            KnowledgeQuestion.owner_user_id == owner_user_id,
            KnowledgeQuestion.required_fact_key == requirement.fact_key,
            KnowledgeQuestion.source_reference == source_reference,
            KnowledgeQuestion.status == "pending",
        )
    )
    if existing is not None:
        return existing
    question = create_question(
        session,
        owner_user_id=owner_user_id,
        required_fact_key=requirement.fact_key,
        question_text=requirement.question_text,
        source_reference=source_reference,
        correlation_id=correlation_id,
        agent_id=actor_id,
    )
    _audit_question_pending(
        session,
        question=question,
        actor_id=actor_id,
        correlation_id=correlation_id,
        webhook_context=webhook_context,
    )
    return question


def _audit_question_pending(
    session: Session,
    *,
    question: KnowledgeQuestion,
    actor_id: str,
    correlation_id: str,
    webhook_context: GmailKnowledgeWebhookContext | None,
) -> None:
    event = knowledge_question_pending_event(
        question_id=question.knowledge_question_id,
        fact_key=question.required_fact_key,
        status=question.status,
    )
    record_audit_event(
        session,
        AuditEventInput(
            event_type="gmail.knowledge_question_pending",
            actor_type="service",
            actor_id=actor_id,
            channel="service",
            action="create_question",
            resource_type="knowledge_question",
            resource_id=question.knowledge_question_id,
            result="succeeded",
            correlation_id=correlation_id,
            metadata=event.payload,
        ),
    )
    _enqueue_webhook(session, event, webhook_context=webhook_context)


def _audit_knowledge_answer(
    session: Session,
    *,
    question: KnowledgeQuestion,
    answer: KnowledgeAnswer,
    actor_id: str,
    correlation_id: str,
    webhook_context: GmailKnowledgeWebhookContext | None,
) -> None:
    revision_id = answer.created_fact_revision_id or "revision_unavailable"
    event = knowledge_question_answered_event(
        question_id=question.knowledge_question_id,
        fact_key=question.required_fact_key,
        revision_id=revision_id,
        status=question.status,
    )
    record_audit_event(
        session,
        AuditEventInput(
            event_type="gmail.knowledge_question_answered",
            actor_type="service",
            actor_id=actor_id,
            channel="service",
            action="answer_question",
            resource_type="knowledge_question",
            resource_id=question.knowledge_question_id,
            result="succeeded",
            correlation_id=correlation_id,
            metadata=event.payload,
        ),
    )
    _enqueue_webhook(session, event, webhook_context=webhook_context)


def _audit_knowledge_context(
    session: Session,
    *,
    actor_id: str,
    result: str,
    correlation_id: str,
    metadata: dict[str, int | str],
) -> None:
    record_audit_event(
        session,
        AuditEventInput(
            event_type="gmail.knowledge_context_prepared",
            actor_type="service",
            actor_id=actor_id,
            channel="service",
            action="prepare_knowledge_context",
            resource_type="gmail_message",
            resource_id=str(metadata["resource_id"]),
            result=result,
            correlation_id=correlation_id,
            metadata=metadata,
        ),
    )


def _enqueue_webhook(
    session: Session,
    event: PlatformWebhookEvent,
    *,
    webhook_context: GmailKnowledgeWebhookContext | None,
) -> None:
    if webhook_context is None:
        return

    def audit_webhook_delivery(webhook_event: WebhookAuditEvent) -> None:
        record_webhook_audit_event(
            session,
            webhook_event,
            correlation_id=webhook_context.correlation_id,
        )

    enqueue_platform_webhook_event(
        session,
        event,
        correlation_id=webhook_context.correlation_id,
        now=webhook_context.now or utc_now(),
        settings=webhook_context.settings,
        audit_hook=audit_webhook_delivery,
    )


def _source_reference(provider_message_reference: str) -> str:
    return f"gmail:{provider_message_reference[:220]}"
