from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.orm import Session

from atlas_api.core.config import Settings
from atlas_api.core.contracts import (
    PaginationParameters,
    decode_cursor,
    encode_cursor,
)
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.agent import AgentRegistration
from atlas_api.services.agent_credentials import (
    IssuedAgentCredential,
    issue_agent_credential,
)

ALLOWED_AGENT_STATUSES = frozenset({"active", "disabled", "retired"})
ALLOWED_HEALTH_STATUSES = frozenset({"unknown", "healthy", "degraded", "unhealthy"})
ALLOWED_RISK_LEVELS = frozenset({"low", "medium", "high"})
ALLOWED_LIFECYCLE_STATUSES = frozenset(
    {"pending", "connected", "disconnected", "archived"}
)
ALLOWED_MONITORING_MODES = frozenset({"heartbeat", "activity_only"})
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


@dataclass(frozen=True)
class AgentEnrollmentResult:
    agent: AgentRegistration
    issued_credential: IssuedAgentCredential


def list_agent_registrations(
    session: Session,
    *,
    pagination: PaginationParameters,
    status: str | None = None,
    active_surface_only: bool = False,
    owner_user_id: str | None = None,
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
    if active_surface_only:
        query = query.where(AgentRegistration.active_surface_visible.is_(True))
    if owner_user_id is not None:
        query = query.where(AgentRegistration.owner_user_id == owner_user_id)
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


def get_owner_agent_registration(
    session: Session,
    *,
    owner_user_id: str,
    agent_id: str,
) -> AgentRegistration:
    agent = session.get(AgentRegistration, agent_id)
    if (
        agent is None
        or agent.owner_user_id != owner_user_id
        or not agent.active_surface_visible
    ):
        raise ApiError(
            status_code=404,
            code="agent_not_found",
            message="Agent was not found.",
        )
    return agent


def enroll_owner_agent(
    session: Session,
    *,
    owner_user_id: str,
    settings: Settings,
    slug: str,
    display_name: str,
    description: str,
    environment: str,
    monitoring_mode: str = "heartbeat",
    heartbeat_interval_seconds: int | None = 60,
    tags: list[str] | None = None,
    repository_url: str | None = None,
    deployment_url: str | None = None,
    expected_version: str | None = None,
) -> AgentEnrollmentResult:
    _validate_slug(slug)
    _validate_identifier("environment", environment, max_length=80)
    _validate_monitoring(monitoring_mode, heartbeat_interval_seconds)
    bounded_tags = tags or []
    _validate_tags(bounded_tags)
    _validate_optional_url("repository_url", repository_url)
    _validate_optional_url("deployment_url", deployment_url)
    if expected_version is not None:
        _validate_identifier("expected_version", expected_version, max_length=80)

    agent = AgentRegistration(
        owner_user_id=owner_user_id,
        slug=slug,
        display_name=display_name,
        description=description,
        version=expected_version or "unreported",
        risk_level="low",
        capabilities=["telemetry.report"],
        allowed_tools=["atlas.telemetry.write"],
        required_connectors=[],
        configuration_schema={},
        supports_manual_run=False,
        supports_scheduled_run=False,
        status="active",
        health_status="unknown",
        registration_source="owner_enrolled",
        active_surface_visible=True,
        lifecycle_status="pending",
        environment=environment,
        monitoring_mode=monitoring_mode,
        heartbeat_interval_seconds=heartbeat_interval_seconds,
        tags=bounded_tags,
        repository_url=repository_url,
        deployment_url=deployment_url,
        expected_version=expected_version,
        observed_health=(
            "not_monitored" if monitoring_mode == "activity_only" else "never_seen"
        ),
        reported_health="unknown",
        last_activity_at=utc_now(),
    )
    session.add(agent)
    session.flush()
    issued = issue_agent_credential(session, agent=agent, settings=settings)
    return AgentEnrollmentResult(agent=agent, issued_credential=issued)


def update_owner_agent_metadata(
    session: Session,
    *,
    owner_user_id: str,
    agent_id: str,
    display_name: str | None = None,
    description: str | None = None,
    environment: str | None = None,
    tags: list[str] | None = None,
    repository_url: str | None = None,
    deployment_url: str | None = None,
    expected_version: str | None = None,
) -> AgentRegistration:
    agent = get_owner_agent_registration(
        session,
        owner_user_id=owner_user_id,
        agent_id=agent_id,
    )
    if display_name is not None:
        agent.display_name = display_name
    if description is not None:
        agent.description = description
    if environment is not None:
        _validate_identifier("environment", environment, max_length=80)
        agent.environment = environment
    if tags is not None:
        _validate_tags(tags)
        agent.tags = tags
    if repository_url is not None:
        _validate_optional_url("repository_url", repository_url)
        agent.repository_url = repository_url
    if deployment_url is not None:
        _validate_optional_url("deployment_url", deployment_url)
        agent.deployment_url = deployment_url
    if expected_version is not None:
        _validate_identifier("expected_version", expected_version, max_length=80)
        agent.expected_version = expected_version
    session.flush()
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
    owner_user_id: str | None = None,
    registration_source: str = "owner_enrolled",
    active_surface_visible: bool = True,
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
        owner_user_id=owner_user_id,
        registration_source=registration_source,
        active_surface_visible=active_surface_visible,
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


def _validate_monitoring(mode: str, heartbeat_interval_seconds: int | None) -> None:
    if mode not in ALLOWED_MONITORING_MODES:
        raise ApiError(422, "agent_monitoring_mode_invalid", "Monitoring mode invalid.")
    if mode == "activity_only":
        if heartbeat_interval_seconds is not None:
            raise ApiError(
                422,
                "agent_heartbeat_interval_invalid",
                "Activity-only agents must not set a heartbeat interval.",
            )
        return
    if (
        heartbeat_interval_seconds is None
        or not 30 <= heartbeat_interval_seconds <= 3600
    ):
        raise ApiError(
            422,
            "agent_heartbeat_interval_invalid",
            "Heartbeat interval must be between 30 and 3600 seconds.",
        )


def _validate_tags(tags: list[str]) -> None:
    if len(tags) > 12:
        raise ApiError(422, "agent_tags_invalid", "Agent tags are invalid.")
    for tag in tags:
        _validate_identifier("tags", tag, max_length=40)


def _validate_identifier(field_name: str, value: str, *, max_length: int) -> None:
    if len(value) > max_length or _DESCRIPTOR_VALUE_PATTERN.fullmatch(value) is None:
        raise ApiError(
            422,
            "agent_metadata_invalid",
            "Agent metadata is invalid.",
            details={"field": field_name},
        )


def _validate_optional_url(field_name: str, value: str | None) -> None:
    if value is None:
        return
    if len(value) > 500 or not value.startswith(("https://", "http://")):
        raise ApiError(
            422,
            "agent_metadata_invalid",
            "Agent metadata is invalid.",
            details={"field": field_name},
        )
