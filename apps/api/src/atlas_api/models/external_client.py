from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas_api.db.base import Base, TimestampMixin, prefixed_id


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "identity_provider",
            "identity_subject",
            name="uq_users_identity",
        ),
    )

    user_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("usr"),
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    identity_provider: Mapped[str] = mapped_column(String(80), nullable=False)
    identity_subject: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")


class ExternalProductClient(TimestampMixin, Base):
    __tablename__ = "external_product_clients"

    external_client_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: prefixed_id("epc"),
    )
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    authentication_key_reference: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    human_owner_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
    )

    human_owner: Mapped[User | None] = relationship()
