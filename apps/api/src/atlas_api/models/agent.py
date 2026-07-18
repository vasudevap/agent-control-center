from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from atlas_api.db.base import Base, TimestampMixin, prefixed_id


class AgentRegistration(TimestampMixin, Base):
    __tablename__ = "agent_registrations"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_agent_registration_slug"),
    )

    agent_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("agt"),
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    descriptor_version: Mapped[int] = mapped_column(nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    risk_level: Mapped[str] = mapped_column(String(40), nullable=False)
    capabilities: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allowed_tools: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    required_connectors: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    configuration_schema_ref: Mapped[str | None] = mapped_column(
        String(240),
        nullable=True,
    )
    configuration_schema: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    supports_manual_run: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    supports_scheduled_run: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    health_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="unknown",
    )
    health_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
