from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class WebhookNotification:
    event_type: str
    target_url: str
    payload_summary: dict[str, str]
    correlation_id: str


@dataclass(frozen=True)
class WebhookDeliveryResult:
    status: str
    attempt_count: int
    last_error_code: str | None = None


class WebhookTransport(Protocol):
    async def send(self, notification: WebhookNotification) -> WebhookDeliveryResult:
        """Send a minimized webhook notification."""


class RecordingWebhookTransport:
    def __init__(self) -> None:
        self.sent: list[WebhookNotification] = []

    async def send(self, notification: WebhookNotification) -> WebhookDeliveryResult:
        self.sent.append(notification)
        return WebhookDeliveryResult(status="delivered", attempt_count=1)


class WebhookDeliveryService:
    def __init__(self, transport: WebhookTransport) -> None:
        self._transport = transport

    async def deliver(
        self,
        notification: WebhookNotification,
    ) -> WebhookDeliveryResult:
        return await self._transport.send(notification)
