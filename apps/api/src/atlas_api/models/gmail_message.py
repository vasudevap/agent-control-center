from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas_api.db.base import Base, TimestampMixin, prefixed_id
from atlas_api.models.approval import ManualHandlingRecord
from atlas_api.models.connector import ConnectorConnection
from atlas_api.models.external_client import User


class GmailMessageRecord(TimestampMixin, Base):
    __tablename__ = "gmail_message_records"
    __table_args__ = (
        UniqueConstraint(
            "owner_user_id",
            "connection_id",
            "provider_message_reference",
            name="uq_gmail_message_owner_connection_provider_ref",
        ),
    )

    gmail_message_record_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("gmr"),
    )
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    connection_id: Mapped[str] = mapped_column(
        ForeignKey("connector_connections.connection_id"),
        nullable=False,
    )
    provider_message_reference: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    provider_thread_reference: Mapped[str] = mapped_column(String(160), nullable=False)
    sender_address: Mapped[str] = mapped_column(String(320), nullable=False)
    sender_domain: Mapped[str] = mapped_column(String(160), nullable=False)
    subject_preview: Mapped[str] = mapped_column(String(240), nullable=False)
    content_excerpt_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    attachment_metadata: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    label_names: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    eligibility_reason: Mapped[str] = mapped_column(String(120), nullable=False)
    classification_category: Mapped[str] = mapped_column(String(80), nullable=False)
    classification_confidence: Mapped[int] = mapped_column(nullable=False)
    classification_status: Mapped[str] = mapped_column(String(40), nullable=False)
    review_reason_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    suppression_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="not_suppressed",
    )
    suppression_reason_code: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    manual_handling_id: Mapped[str | None] = mapped_column(
        ForeignKey("manual_handling_records.manual_handling_id"),
        nullable=True,
    )
    source_integrity_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    owner: Mapped[User] = relationship()
    connection: Mapped[ConnectorConnection] = relationship()
    manual_handling: Mapped[ManualHandlingRecord | None] = relationship()
