from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from atlas_api.db.base import Base, prefixed_id, utc_now


class ExternalRequestNonce(Base):
    __tablename__ = "external_request_nonces"
    __table_args__ = (
        UniqueConstraint(
            "external_client_id",
            "key_id",
            "nonce",
            name="uq_external_request_nonce",
        ),
        Index("ix_external_request_nonces_expires_at", "expires_at"),
    )

    external_request_nonce_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: prefixed_id("ern")
    )
    external_client_id: Mapped[str] = mapped_column(String(64), nullable=False)
    key_id: Mapped[str] = mapped_column(String(160), nullable=False)
    nonce: Mapped[str] = mapped_column(String(160), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
