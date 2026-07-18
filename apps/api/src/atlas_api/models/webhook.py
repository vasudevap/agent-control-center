from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas_api.db.base import Base, TimestampMixin, prefixed_id
from atlas_api.models.external_client import ExternalProductClient


class WebhookSubscription(TimestampMixin, Base):
    __tablename__ = "webhook_subscriptions"

    webhook_subscription_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("whsub"),
    )
    external_client_id: Mapped[str] = mapped_column(
        ForeignKey("external_product_clients.external_client_id"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    target_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    secret_reference: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    external_client: Mapped[ExternalProductClient] = relationship()


class WebhookDeliveryAttempt(TimestampMixin, Base):
    __tablename__ = "webhook_delivery_attempts"
    __table_args__ = (
        UniqueConstraint(
            "webhook_subscription_id", "event_id", name="uq_webhook_delivery_event"
        ),
    )

    webhook_delivery_attempt_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("whdel"),
    )
    webhook_subscription_id: Mapped[str] = mapped_column(
        ForeignKey("webhook_subscriptions.webhook_subscription_id"),
        nullable=False,
    )
    event_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    payload_summary: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(80), nullable=False)
    key_id: Mapped[str] = mapped_column(String(160), nullable=False)

    subscription: Mapped[WebhookSubscription] = relationship()
