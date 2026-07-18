from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.orm import Session

from atlas_api.core.contracts import (
    PaginationParameters,
    decode_cursor,
    encode_cursor,
)
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.agent import AgentRegistration

ALLOWED_AGENT_STATUSES = frozenset({"active", "disabled", "retired"})
ALLOWED_HEALTH_STATUSES = frozenset({"unknown", "healthy", "degraded", "unhealthy"})
ALLOWED_RISK_LEVELS = frozenset({"low", "medium", "high"})
_SLUG_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{1,118}[a-z0-9]")
_DESCRIPTOR_VALUE_PATTERN = re.compile(r"[A-Za-z0-9_.:-]{1,160}")
_SECRET_KEY_PATTERN = re.compile(
    r"(secret|token|password|credential|api[_-]?key|oauth|private[_-]?key)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AgentRegistryPage:
    agents: list[AgentRegistration]
    next_cursor: str | None


def list_agent_registrations(
    session: Session,
    *,
    pagination: PaginationParameters,
    status: str | None = None,
) -> AgentRegistryPage:
    if status is not None and status not in ALLOWED_AGENT_STATUSES:
        raise ApiError(
            status_code=422,
            code="agent_status_filter_invalid",
            message="Agent status filter is invalid.",
        )
    query = select(AgentRegistration)
    if status is not None:
        query = query.where(AgentRegistration.status == status)
    query = _apply_cursor(query, pagination.cursor)
    query = query.order_by(AgentRegistration.created_at, AgentRegistration.agent_id)
    rows = list(session.scalars(query.limit(pagination.limit + 1)))
    next_cursor = None
    if len(rows) > pagination.limit:
        rows = rows[: pagination.limit]
        last = rows[-1]
        next_cursor = encode_cursor(
            {
                "created_at": last.created_at.isoformat(),
                "agent_id": last.agent_id,
            }
        )
    return AgentRegistryPage(agents=rows, next_cursor=next_cursor)


def get_agent_registration(session: Session, agent_id: str) -> AgentRegistration:
    agent = session.get(AgentRegistration, agent_id)
    if agent is None:
        raise ApiError(
            status_code=404,
            code="agent_not_found",
            message="Agent was not found.",
        )
    return agent


def create_agent_registration(
    session: Session,
    *,
    slug: str,
    display_name: str,
    description: str,
    version: str,
    risk_level: str,
    capabilities: list[str],
    allowed_tools: list[str],
    required_connectors: list[str],
    configuration_schema_ref: str | None = None,
    configuration_schema: dict[str, Any] | None = None,
    supports_manual_run: bool = False,
    supports_scheduled_run: bool = False,
    status: str = "active",
    health_status: str = "unknown",
) -> AgentRegistration:
    _validate_slug(slug)
    _validate_descriptor_values("capabilities", capabilities)
    _validate_descriptor_values("allowed_tools", allowed_tools)
    _validate_descriptor_values("required_connectors", required_connectors)
    schema = configuration_schema or {}
    _validate_configuration_schema(schema)
    if status not in ALLOWED_AGENT_STATUSES:
        raise ApiError(422, "agent_status_invalid", "Agent status is invalid.")
    if health_status not in ALLOWED_HEALTH_STATUSES:
        raise ApiError(422, "agent_health_status_invalid", "Agent health is invalid.")
    if risk_level not in ALLOWED_RISK_LEVELS:
        raise ApiError(422, "agent_risk_level_invalid", "Agent risk level is invalid.")
    agent = AgentRegistration(
        slug=slug,
        display_name=display_name,
        description=description,
        version=version,
        risk_level=risk_level,
        capabilities=capabilities,
        allowed_tools=allowed_tools,
        required_connectors=required_connectors,
        configuration_schema_ref=configuration_schema_ref,
        configuration_schema=schema,
        supports_manual_run=supports_manual_run,
        supports_scheduled_run=supports_scheduled_run,
        status=status,
        health_status=health_status,
        health_checked_at=utc_now(),
    )
    session.add(agent)
    session.flush()
    return agent


def _apply_cursor(
    query: Select[tuple[AgentRegistration]],
    cursor: str | None,
) -> Select[tuple[AgentRegistration]]:
    if cursor is None:
        return query
    values = decode_cursor(cursor)
    try:
        created_at = datetime.fromisoformat(values["created_at"])
        agent_id = values["agent_id"]
    except (KeyError, ValueError) as exc:
        raise ApiError(
            status_code=422,
            code="pagination_cursor_invalid",
            message="Pagination cursor is invalid.",
        ) from exc
    return query.where(
        or_(
            AgentRegistration.created_at > created_at,
            and_(
                AgentRegistration.created_at == created_at,
                AgentRegistration.agent_id > agent_id,
            ),
        )
    )


def _validate_slug(slug: str) -> None:
    if _SLUG_PATTERN.fullmatch(slug) is None:
        raise ApiError(422, "agent_slug_invalid", "Agent slug is invalid.")


def _validate_descriptor_values(field_name: str, values: list[str]) -> None:
    if not values:
        raise ApiError(
            422,
            "agent_descriptor_invalid",
            "Agent descriptor values are invalid.",
            details={"field": field_name},
        )
    if any(_DESCRIPTOR_VALUE_PATTERN.fullmatch(value) is None for value in values):
        raise ApiError(
            422,
            "agent_descriptor_invalid",
            "Agent descriptor values are invalid.",
            details={"field": field_name},
        )


def _validate_configuration_schema(schema: dict[str, Any]) -> None:
    blocked = sorted(_secret_keys(schema))
    if blocked:
        raise ApiError(
            422,
            "agent_configuration_schema_prohibited",
            "Agent configuration schema contains prohibited secret-bearing keys.",
            details={"fields": blocked},
        )


def _secret_keys(value: Any, *, prefix: str = "") -> set[str]:
    if isinstance(value, dict):
        found: set[str] = set()
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            if _SECRET_KEY_PATTERN.search(key_text):
                found.add(path)
            found.update(_secret_keys(nested, prefix=path))
        return found
    if isinstance(value, list):
        found = set()
        for index, nested in enumerate(value):
            found.update(_secret_keys(nested, prefix=f"{prefix}[{index}]"))
        return found
    return set()
