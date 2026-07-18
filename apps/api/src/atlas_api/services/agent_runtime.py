from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class AgentRuntimeDescriptor:
    agent_id: str
    version: str
    capabilities: tuple[str, ...]
    required_connectors: tuple[str, ...]
    allowed_tools: tuple[str, ...]
    risk_level: str
    supports_manual_run: bool
    supports_scheduled_run: bool


@dataclass(frozen=True)
class AgentHealth:
    status: str
    checked_at_iso: str | None = None
    last_error_code: str | None = None


class AgentRuntime(Protocol):
    """Non-executing contract future concrete agents must satisfy."""

    def descriptor(self) -> AgentRuntimeDescriptor:
        raise NotImplementedError

    def health(self) -> AgentHealth:
        raise NotImplementedError

    async def validate_configuration(self, configuration: dict[str, Any]) -> None:
        raise NotImplementedError
