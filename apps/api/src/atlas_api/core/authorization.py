from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ActorKind(StrEnum):
    HUMAN_OWNER = "human_owner"
    EXTERNAL_CLIENT = "external_client"
    SERVICE = "service"


class Channel(StrEnum):
    DASHBOARD = "dashboard"
    EXTERNAL_PRODUCT_CLIENT = "external_product_client"
    SERVICE = "service"


@dataclass(frozen=True)
class AuthorizationContext:
    actor_kind: ActorKind
    actor_id: str
    channel: Channel
    resource: str
    action: str
    risk_level: str | None = None
    environment: str | None = None


@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    reason_code: str


def authorize(context: AuthorizationContext) -> AuthorizationDecision:
    if (
        context.actor_kind is ActorKind.EXTERNAL_CLIENT
        and context.channel is Channel.EXTERNAL_PRODUCT_CLIENT
        and context.resource == "external_client_authentication"
        and context.action == "probe"
    ):
        return AuthorizationDecision(allowed=True, reason_code="explicit_allow")
    return AuthorizationDecision(allowed=False, reason_code="authorization_denied")
