from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas_api.db.base import Base, TimestampMixin, prefixed_id, utc_now


class KnowledgeFact(TimestampMixin, Base):
    __tablename__ = "knowledge_facts"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "fact_key", name="uq_fact_owner_key"),
    )

    knowledge_fact_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("kfact"),
    )
    owner_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )
    fact_key: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    classification: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="internal",
    )
    current_revision_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    last_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revisions: Mapped[list[KnowledgeFactRevision]] = relationship(
        back_populates="fact",
        foreign_keys="KnowledgeFactRevision.knowledge_fact_id",
    )


class KnowledgeFactRevision(Base):
    __tablename__ = "knowledge_fact_revisions"
    __table_args__ = (
        UniqueConstraint(
            "knowledge_fact_id",
            "revision_number",
            name="uq_fact_revision_number",
        ),
    )

    knowledge_fact_revision_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("kfrev"),
    )
    knowledge_fact_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_facts.knowledge_fact_id"),
        nullable=False,
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    display_value: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(240), nullable=True)
    provenance_summary: Mapped[str] = mapped_column(Text, nullable=False)
    is_volatile: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    prohibited_content_reason: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    fact: Mapped[KnowledgeFact] = relationship(
        back_populates="revisions",
        foreign_keys=[knowledge_fact_id],
    )


class KnowledgeQuestion(TimestampMixin, Base):
    __tablename__ = "knowledge_questions"

    knowledge_question_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("kq"),
    )
    owner_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )
    agent_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    required_fact_key: Mapped[str] = mapped_column(String(160), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(240), nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(80), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class KnowledgeAnswer(Base):
    __tablename__ = "knowledge_answers"
    __table_args__ = (
        UniqueConstraint("knowledge_question_id", name="uq_answer_question"),
    )

    knowledge_answer_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("ka"),
    )
    knowledge_question_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_questions.knowledge_question_id"),
        nullable=False,
    )
    answered_by_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    validation_status: Mapped[str] = mapped_column(String(40), nullable=False)
    rejected_reason: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_fact_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("knowledge_fact_revisions.knowledge_fact_revision_id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    question: Mapped[KnowledgeQuestion] = relationship()
