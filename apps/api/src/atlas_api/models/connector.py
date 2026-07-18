from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas_api.db.base import Base, TimestampMixin, prefixed_id, utc_now
from atlas_api.models.external_client import User


class ConnectorType(TimestampMixin, Base):
    __tablename__ = "connector_types"

    connector_type: Mapped[str] = mapped_column(String(80), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    authentication_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    supported_operations: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    required_scopes: Mapped[dict[str, list[str]]] = mapped_column(JSON, nullable=False)
    risk_by_operation: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False)
    supports_health_check: Mapped[bool] = mapped_column(nullable=False, default=True)
    supports_revocation: Mapped[bool] = mapped_column(nullable=False, default=True)
    supports_refresh: Mapped[bool] = mapped_column(nullable=False, default=True)
    provider_docs_reference: Mapped[str] = mapped_column(String(240), nullable=False)
    configuration_schema: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )


class ConnectorCredentialReference(TimestampMixin, Base):
    __tablename__ = "connector_credential_references"

    credential_reference_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("crd"),
    )
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    connector_type: Mapped[str] = mapped_column(
        ForeignKey("connector_types.connector_type"),
        nullable=False,
    )
    reference_label: Mapped[str] = mapped_column(String(160), nullable=False)
    key_version: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    last_rotated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    owner: Mapped[User] = relationship()
    connector: Mapped[ConnectorType] = relationship()


class ConnectorConnection(TimestampMixin, Base):
    __tablename__ = "connector_connections"
    __table_args__ = (
        UniqueConstraint(
            "owner_user_id",
            "connector_type",
            "account_identifier",
            name="uq_connector_owner_type_account",
        ),
    )

    connection_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("con"),
    )
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    connector_type: Mapped[str] = mapped_column(
        ForeignKey("connector_types.connector_type"),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    account_identifier: Mapped[str] = mapped_column(String(320), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="connected")
    granted_scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    credential_reference_id: Mapped[str] = mapped_column(
        ForeignKey("connector_credential_references.credential_reference_id"),
        nullable=False,
    )
    health_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="unknown",
    )
    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_failure_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_health_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)

    owner: Mapped[User] = relationship()
    connector: Mapped[ConnectorType] = relationship()
    credential_reference: Mapped[ConnectorCredentialReference] = relationship()


class ConnectorOAuthState(TimestampMixin, Base):
    __tablename__ = "connector_oauth_states"

    oauth_state_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("oas"),
    )
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    connector_type: Mapped[str] = mapped_column(
        ForeignKey("connector_types.connector_type"),
        nullable=False,
    )
    state_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    pkce_challenge: Mapped[str] = mapped_column(String(128), nullable=False)
    redirect_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    requested_scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    owner: Mapped[User] = relationship()
    connector: Mapped[ConnectorType] = relationship()

    @classmethod
    def pending_until(cls, minutes: int) -> datetime:
        return utc_now().replace(microsecond=0) + timedelta(minutes=minutes)
