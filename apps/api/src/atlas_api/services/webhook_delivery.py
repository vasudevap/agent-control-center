from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.events import (
    ALLOWED_WEBHOOK_EVENT_TYPES,
    ALLOWED_WEBHOOK_PAYLOAD_KEYS,
    DENIED_WEBHOOK_PAYLOAD_KEY_PARTS,
)
from atlas_api.db.base import prefixed_id
from atlas_api.models.webhook import WebhookDeliveryAttempt, WebhookSubscription

RETRY_DELAYS = (30, 120, 480, 1800)
MAX_ATTEMPTS = 5
ALLOWED_EVENT_TYPES = ALLOWED_WEBHOOK_EVENT_TYPES
ALLOWED_PAYLOAD_KEYS = ALLOWED_WEBHOOK_PAYLOAD_KEYS


class WebhookError(ValueError):
    pass


@dataclass(frozen=True)
class WebhookNotification:
    event_id: str
    event_type: str
    target_url: str
    body: bytes
    headers: dict[str, str]


@dataclass(frozen=True)
class WebhookDeliveryResult:
    status: str
    error_code: str | None = None


@dataclass(frozen=True)
class WebhookAuditEvent:
    event_type: str
    delivery_attempt_id: str
    metadata: dict[str, int | str | None]


WebhookAuditHook = Callable[[WebhookAuditEvent], None]


class WebhookTransport(Protocol):
    async def send(
        self, notification: WebhookNotification, *, timeout_seconds: int
    ) -> WebhookDeliveryResult: ...


class RecordingWebhookTransport:
    def __init__(self, result: WebhookDeliveryResult | None = None) -> None:
        self.sent: list[WebhookNotification] = []
        self.result = result or WebhookDeliveryResult("delivered")

    async def send(
        self, notification: WebhookNotification, *, timeout_seconds: int
    ) -> WebhookDeliveryResult:
        if timeout_seconds != 5:
            raise AssertionError("webhook_timeout_contract_invalid")
        self.sent.append(notification)
        return self.result


class WebhookDeliveryService:
    def __init__(self, transport: WebhookTransport, settings: Settings) -> None:
        self._transport = transport
        self._settings = settings

    async def deliver_due(
        self,
        session: Session,
        *,
        now: datetime,
        audit_hook: WebhookAuditHook | None = None,
    ) -> int:
        delivered = 0
        attempts = session.scalars(
            select(WebhookDeliveryAttempt).where(
                WebhookDeliveryAttempt.status.in_(
                    ("pending", "retry_wait", "indeterminate")
                ),
                WebhookDeliveryAttempt.next_retry_at.is_(None)
                | (WebhookDeliveryAttempt.next_retry_at <= now),
            )
        ).all()
        for attempt in attempts:
            subscription = session.get(
                WebhookSubscription, attempt.webhook_subscription_id
            )
            if subscription is None or subscription.status != "active":
                continue
            notification = _notification(attempt, subscription, self._settings, now)
            attempt.status = "delivering"
            attempt.attempt_count += 1
            result = await self._transport.send(notification, timeout_seconds=5)
            _apply_result(attempt, result, now)
            _audit(
                audit_hook,
                f"webhook.delivery_{attempt.status}",
                attempt,
                error_code=result.error_code,
            )
            delivered += 1
        session.flush()
        return delivered


def enqueue_notification(
    session: Session,
    *,
    subscription_id: str,
    event_type: str,
    payload: dict[str, str],
    correlation_id: str,
    now: datetime,
    settings: Settings,
    audit_hook: WebhookAuditHook | None = None,
) -> WebhookDeliveryAttempt:
    _validate_payload(event_type, payload)
    subscription = session.get(WebhookSubscription, subscription_id)
    if subscription is None or subscription.status != "active":
        raise WebhookError("webhook_subscription_unavailable")
    key_id, _ = _signing_key(settings, None)
    event_id = prefixed_id("whe")
    attempt = WebhookDeliveryAttempt(
        webhook_subscription_id=subscription_id,
        event_id=event_id,
        event_type=event_type,
        payload_summary=payload,
        correlation_id=correlation_id,
        key_id=key_id,
        status="pending",
        attempt_count=0,
        next_retry_at=now,
    )
    session.add(attempt)
    session.flush()
    _audit(audit_hook, "webhook.delivery_queued", attempt)
    return attempt


def _notification(
    attempt: WebhookDeliveryAttempt,
    subscription: WebhookSubscription,
    settings: Settings,
    now: datetime,
) -> WebhookNotification:
    key_id, secret = _signing_key(settings, attempt.key_id)
    body = json.dumps(
        {
            "event_id": attempt.event_id,
            "event_type": attempt.event_type,
            "payload": attempt.payload_summary,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    timestamp = str(int(now.timestamp()))
    message = b"\n".join((attempt.event_id.encode(), timestamp.encode(), body))
    signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return WebhookNotification(
        attempt.event_id,
        attempt.event_type,
        subscription.target_url,
        body,
        {
            "X-Atlas-Event-Id": attempt.event_id,
            "X-Atlas-Event-Type": attempt.event_type,
            "X-Atlas-Timestamp": timestamp,
            "X-Atlas-Key-Id": key_id,
            "X-Atlas-Signature": signature,
        },
    )


def _apply_result(
    attempt: WebhookDeliveryAttempt, result: WebhookDeliveryResult, now: datetime
) -> None:
    if result.status == "delivered":
        attempt.status, attempt.next_retry_at, attempt.last_error_code = (
            "delivered",
            None,
            None,
        )
    elif attempt.attempt_count >= MAX_ATTEMPTS:
        attempt.status, attempt.next_retry_at, attempt.last_error_code = (
            "failed",
            None,
            result.error_code,
        )
    else:
        attempt.status = (
            "indeterminate" if result.status == "indeterminate" else "retry_wait"
        )
        attempt.last_error_code = result.error_code
        attempt.next_retry_at = now + timedelta(
            seconds=RETRY_DELAYS[attempt.attempt_count - 1]
        )


def _validate_payload(event_type: str, payload: dict[str, str]) -> None:
    if (
        event_type not in ALLOWED_EVENT_TYPES
        or not payload
        or set(payload) - ALLOWED_PAYLOAD_KEYS
        or any(
            any(
                fragment in key.lower()
                for fragment in DENIED_WEBHOOK_PAYLOAD_KEY_PARTS
            )
            for key in payload
        )
    ):
        raise WebhookError("webhook_payload_invalid")
    if not all(
        isinstance(value, str) and len(value) <= 240 for value in payload.values()
    ):
        raise WebhookError("webhook_payload_invalid")


def _signing_key(settings: Settings, requested_key_id: str | None) -> tuple[str, str]:
    if (
        settings.webhook_signing_key_id
        and settings.webhook_signing_secret
        and requested_key_id in {None, settings.webhook_signing_key_id}
    ):
        return (
            settings.webhook_signing_key_id,
            settings.webhook_signing_secret.get_secret_value(),
        )
    if (
        requested_key_id == settings.webhook_signing_next_key_id
        and settings.webhook_signing_next_secret
    ):
        assert requested_key_id is not None
        return requested_key_id, settings.webhook_signing_next_secret.get_secret_value()
    raise WebhookError("webhook_signing_not_configured")


def _audit(
    audit_hook: WebhookAuditHook | None,
    event_type: str,
    attempt: WebhookDeliveryAttempt,
    **metadata: int | str | None,
) -> None:
    if audit_hook is not None:
        audit_hook(
            WebhookAuditEvent(
                event_type=event_type,
                delivery_attempt_id=attempt.webhook_delivery_attempt_id,
                metadata={
                    "event_id": attempt.event_id,
                    "event_type": attempt.event_type,
                    "status": attempt.status,
                    "attempt_count": attempt.attempt_count,
                    "webhook_delivery_attempt_id": (
                        attempt.webhook_delivery_attempt_id
                    ),
                    "webhook_subscription_id": attempt.webhook_subscription_id,
                    **metadata,
                },
            )
        )
