from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.contracts import PaginationParameters, decode_cursor, encode_cursor
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.knowledge import KnowledgeAnswer, KnowledgeFact, KnowledgeQuestion
from atlas_api.services.knowledge_facts import create_fact, update_fact

ALLOWED_QUESTION_STATUSES = frozenset({"pending", "answered", "cancelled", "expired"})


@dataclass(frozen=True)
class QuestionPage:
    questions: list[KnowledgeQuestion]
    next_cursor: str | None


def create_question(
    session: Session,
    *,
    owner_user_id: str,
    required_fact_key: str,
    question_text: str,
    correlation_id: str,
    agent_id: str | None = None,
    source_reference: str | None = None,
    expires_at: datetime | None = None,
) -> KnowledgeQuestion:
    if not required_fact_key or len(required_fact_key) > 160:
        raise ApiError(
            422,
            "knowledge_question_fact_key_invalid",
            "Fact key is invalid.",
        )
    if not question_text.strip() or len(question_text) > 1000:
        raise ApiError(
            422,
            "knowledge_question_text_invalid",
            "Question text is invalid.",
        )
    question = KnowledgeQuestion(
        owner_user_id=owner_user_id,
        agent_id=agent_id,
        status="pending",
        required_fact_key=required_fact_key,
        question_text=question_text,
        source_reference=source_reference,
        correlation_id=correlation_id,
        expires_at=expires_at,
    )
    session.add(question)
    session.flush()
    return question


def list_questions(
    session: Session,
    *,
    owner_user_id: str,
    pagination: PaginationParameters,
    status: str = "pending",
) -> QuestionPage:
    if status not in ALLOWED_QUESTION_STATUSES:
        raise ApiError(
            422,
            "knowledge_question_status_invalid",
            "Question status is invalid.",
        )
    query = select(KnowledgeQuestion).where(
        KnowledgeQuestion.owner_user_id == owner_user_id,
        KnowledgeQuestion.status == status,
    )
    query = _apply_cursor(query, pagination.cursor)
    query = query.order_by(
        KnowledgeQuestion.created_at,
        KnowledgeQuestion.knowledge_question_id,
    )
    questions = list(session.scalars(query.limit(pagination.limit + 1)))
    next_cursor = None
    if len(questions) > pagination.limit:
        questions = questions[: pagination.limit]
        last = questions[-1]
        next_cursor = encode_cursor(
            {
                "created_at": last.created_at.isoformat(),
                "knowledge_question_id": last.knowledge_question_id,
            }
        )
    return QuestionPage(questions=questions, next_cursor=next_cursor)


def get_question(
    session: Session,
    *,
    owner_user_id: str,
    question_id: str,
) -> KnowledgeQuestion:
    question = session.get(KnowledgeQuestion, question_id)
    if question is None or question.owner_user_id != owner_user_id:
        raise ApiError(
            404,
            "knowledge_question_not_found",
            "Knowledge question was not found.",
        )
    return question


def cancel_question(
    session: Session,
    *,
    owner_user_id: str,
    question_id: str,
) -> KnowledgeQuestion:
    question = get_question(
        session,
        owner_user_id=owner_user_id,
        question_id=question_id,
    )
    if question.status != "pending":
        raise ApiError(
            409,
            "knowledge_question_not_pending",
            "Question is not pending.",
        )
    question.status = "cancelled"
    question.cancelled_at = utc_now()
    session.flush()
    return question


def submit_answer(
    session: Session,
    *,
    owner_user_id: str,
    question_id: str,
    answer_text: str,
    source_reference: str | None,
) -> tuple[KnowledgeQuestion, KnowledgeAnswer]:
    question = get_question(
        session,
        owner_user_id=owner_user_id,
        question_id=question_id,
    )
    existing = session.scalar(
        select(KnowledgeAnswer).where(
            KnowledgeAnswer.knowledge_question_id == question.knowledge_question_id
        )
    )
    if existing is not None:
        return question, existing
    _validate_answerable(question)
    fact = session.scalar(
        select(KnowledgeFact).where(
            KnowledgeFact.owner_user_id == owner_user_id,
            KnowledgeFact.fact_key == question.required_fact_key,
            KnowledgeFact.status == "active",
        )
    )
    if fact is None:
        _fact, revision = create_fact(
            session,
            owner_user_id=owner_user_id,
            fact_key=question.required_fact_key,
            display_value=answer_text,
            classification="internal",
            source_type="human",
            source_reference=source_reference,
            provenance_summary="Human answer to governed knowledge question.",
            is_volatile=False,
            confirmed=True,
        )
    else:
        _fact, revision = update_fact(
            session,
            owner_user_id=owner_user_id,
            knowledge_fact_id=fact.knowledge_fact_id,
            display_value=answer_text,
            source_type="human",
            source_reference=source_reference,
            provenance_summary="Human answer updated governed knowledge fact.",
            is_volatile=False,
            confirmed=True,
        )
    answer = KnowledgeAnswer(
        knowledge_question_id=question.knowledge_question_id,
        answered_by_user_id=owner_user_id,
        answer_text=answer_text,
        validation_status="accepted",
        created_fact_revision_id=revision.knowledge_fact_revision_id,
    )
    question.status = "answered"
    question.answered_at = utc_now()
    session.add(answer)
    session.flush()
    return question, answer


def _validate_answerable(question: KnowledgeQuestion) -> None:
    if question.status != "pending":
        raise ApiError(
            409,
            "knowledge_question_not_pending",
            "Question is not pending.",
        )
    if question.expires_at is not None:
        expires_at = question.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= utc_now():
            question.status = "expired"
            raise ApiError(
                409,
                "knowledge_question_expired",
                "Question has expired.",
            )


def _apply_cursor(query: Any, cursor: str | None) -> Any:
    if cursor is None:
        return query
    values = decode_cursor(cursor)
    created_at = datetime.fromisoformat(values["created_at"])
    question_id = values["knowledge_question_id"]
    return query.where(
        (KnowledgeQuestion.created_at > created_at)
        | (
            (KnowledgeQuestion.created_at == created_at)
            & (KnowledgeQuestion.knowledge_question_id > question_id)
        )
    )
