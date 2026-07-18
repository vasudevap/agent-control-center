from __future__ import annotations

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from atlas_api.db.base import Base, TimestampMixin, prefixed_id


class ApiIdempotencyRecord(TimestampMixin, Base):
    __tablename__ = "api_idempotency_records"
    __table_args__ = (
        UniqueConstraint(
            "actor_id",
            "operation",
            "idempotency_key",
            name="uq_api_idempotency_actor_operation_key",
        ),
    )

    api_idempotency_record_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("idem"),
    )
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    operation: Mapped[str] = mapped_column(String(120), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
