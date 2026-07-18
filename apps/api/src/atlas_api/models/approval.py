from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas_api.db.base import Base, TimestampMixin, prefixed_id, utc_now


class ApprovalRequest(TimestampMixin, Base):
    __tablename__ = "approval_requests"

    approval_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("appr"),
    )
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    action_type: Mapped[str] = mapped_column(String(120), nullable=False)
    action_reference: Mapped[str] = mapped_column(String(160), nullable=False)
    action_payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_summary: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    decision_context_manifest: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    decision_channel: Mapped[str | None] = mapped_column(String(40), nullable=True)
    external_client_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reviewer_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    superseded_by_approval_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    continuation_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="not_requested",
    )

    decisions: Mapped[list[ApprovalDecision]] = relationship(back_populates="approval")


class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"

    approval_decision_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("apprd"),
    )
    approval_id: Mapped[str] = mapped_column(
        ForeignKey("approval_requests.approval_id"),
        nullable=False,
    )
    decision: Mapped[str] = mapped_column(String(40), nullable=False)
    submitted_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    channel: Mapped[str] = mapped_column(String(40), nullable=False)
    external_client_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reviewer_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    edited_action_payload_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    approval: Mapped[ApprovalRequest] = relationship(back_populates="decisions")


class ManualHandlingRecord(TimestampMixin, Base):
    __tablename__ = "manual_handling_records"

    manual_handling_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("mh"),
    )
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_reference: Mapped[str] = mapped_column(String(240), nullable=False)
    reason_category: Mapped[str] = mapped_column(String(80), nullable=False)
    sensitivity_classification: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    held_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
