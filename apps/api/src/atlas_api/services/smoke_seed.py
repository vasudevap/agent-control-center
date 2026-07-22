from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.agent import AgentRegistration
from atlas_api.models.approval import ApprovalRequest
from atlas_api.models.connector import (
    ConnectorConnection,
    ConnectorCredentialReference,
)
from atlas_api.models.run import AgentRun, AgentRunStep
from atlas_api.services.agent_registry import create_agent_registration
from atlas_api.services.approval_contracts import create_approval_request
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.connectors import (
    DRIVE_SCOPE_FILE,
    GMAIL_SCOPE_MODIFY,
    ensure_default_connector_types,
)
from atlas_api.services.runs import record_run_step

SMOKE_SEED_SCOPE = "hosted_mvp_smoke"
SMOKE_AGENT_SLUG = "hosted-runtime-smoke-agent"
SMOKE_ACCOUNT_DOMAIN = "grafley.invalid"
SMOKE_CREDENTIAL_VERSION = "synthetic-smoke-v1"

_SMOKE_CONNECTORS = {
    "gmail": {
        "display_name": "Synthetic Gmail Smoke Connector",
        "account_identifier": f"synthetic-smoke+gmail@{SMOKE_ACCOUNT_DOMAIN}",
        "granted_scopes": [GMAIL_SCOPE_MODIFY],
    },
    "google_drive": {
        "display_name": "Synthetic Drive Smoke Connector",
        "account_identifier": f"synthetic-smoke+drive@{SMOKE_ACCOUNT_DOMAIN}",
        "granted_scopes": [DRIVE_SCOPE_FILE],
    },
}


@dataclass(frozen=True)
class RuntimeSmokeSeedResult:
    scope: str
    synthetic: bool
    agent: AgentRegistration
    connections: list[ConnectorConnection]
    run: AgentRun
    approval: ApprovalRequest


def seed_hosted_runtime_smoke(
    session: Session,
    *,
    owner_user_id: str,
    idempotency_key: str,
    correlation_id: str,
    now: datetime | None = None,
) -> RuntimeSmokeSeedResult:
    seed_time = now or utc_now()
    agent = _ensure_smoke_agent(session, now=seed_time)
    connections = [
        _ensure_synthetic_connection(
            session,
            owner_user_id=owner_user_id,
            connector_type=connector_type,
            display_name=str(spec["display_name"]),
            account_identifier=str(spec["account_identifier"]),
            granted_scopes=list(spec["granted_scopes"]),
            now=seed_time,
        )
        for connector_type, spec in _SMOKE_CONNECTORS.items()
    ]
    run = _ensure_smoke_run(
        session,
        owner_user_id=owner_user_id,
        agent=agent,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        now=seed_time,
    )
    approval = _ensure_smoke_approval(
        session,
        owner_user_id=owner_user_id,
        agent=agent,
        run=run,
        now=seed_time,
    )
    record_audit_event(
        session,
        AuditEventInput(
            event_type="smoke_seed.hosted_runtime_seeded",
            actor_type="human_owner",
            actor_id=owner_user_id,
            channel="dashboard",
            action="seed_hosted_runtime_smoke",
            resource_type="agent_run",
            resource_id=run.run_id,
            result="succeeded",
            correlation_id=correlation_id,
            metadata={
                "run_id": run.run_id,
                "connection_id": connections[0].connection_id if connections else None,
                "connector_type": "synthetic_smoke",
                "count": len(connections),
                "status": run.status,
            },
        ),
    )
    session.flush()
    return RuntimeSmokeSeedResult(
        scope=SMOKE_SEED_SCOPE,
        synthetic=True,
        agent=agent,
        connections=connections,
        run=run,
        approval=approval,
    )


def _ensure_smoke_agent(session: Session, *, now: datetime) -> AgentRegistration:
    agent = session.scalar(
        select(AgentRegistration).where(AgentRegistration.slug == SMOKE_AGENT_SLUG)
    )
    if agent is None:
        return create_agent_registration(
            session,
            slug=SMOKE_AGENT_SLUG,
            display_name="Hosted Runtime Smoke Agent",
            description=(
                "Synthetic no-op agent used only for WO-063 hosted MVP smoke "
                "evidence."
            ),
            version="0.1.0",
            risk_level="medium",
            capabilities=["synthetic.smoke"],
            allowed_tools=["synthetic.noop"],
            required_connectors=["gmail", "google_drive"],
            supports_manual_run=True,
            health_status="healthy",
        )
    agent.status = "active"
    agent.health_status = "healthy"
    agent.health_checked_at = now
    agent.supports_manual_run = True
    session.flush()
    return agent


def _ensure_synthetic_connection(
    session: Session,
    *,
    owner_user_id: str,
    connector_type: str,
    display_name: str,
    account_identifier: str,
    granted_scopes: list[str],
    now: datetime,
) -> ConnectorConnection:
    ensure_default_connector_types(session)
    connection = session.scalar(
        select(ConnectorConnection).where(
            ConnectorConnection.owner_user_id == owner_user_id,
            ConnectorConnection.connector_type == connector_type,
            ConnectorConnection.account_identifier == account_identifier,
        )
    )
    credential = (
        session.get(
            ConnectorCredentialReference,
            connection.credential_reference_id,
        )
        if connection is not None
        else None
    )
    if credential is None or credential.key_version != SMOKE_CREDENTIAL_VERSION:
        credential = ConnectorCredentialReference(
            owner_user_id=owner_user_id,
            connector_type=connector_type,
            reference_label=f"{connector_type}:synthetic-smoke:wo-063",
            key_version=SMOKE_CREDENTIAL_VERSION,
            status="active",
            last_rotated_at=now,
        )
        session.add(credential)
        session.flush()
    else:
        credential.status = "active"
        credential.last_rotated_at = now

    if connection is None:
        connection = ConnectorConnection(
            owner_user_id=owner_user_id,
            connector_type=connector_type,
            display_name=display_name,
            account_identifier=account_identifier,
            status="connected",
            granted_scopes=granted_scopes,
            credential_reference_id=credential.credential_reference_id,
            health_status="healthy",
            last_success_at=now,
            last_health_checked_at=now,
        )
        session.add(connection)
    else:
        connection.display_name = display_name
        connection.status = "connected"
        connection.granted_scopes = granted_scopes
        connection.credential_reference_id = credential.credential_reference_id
        connection.health_status = "healthy"
        connection.last_success_at = now
        connection.last_failure_at = None
        connection.last_health_checked_at = now
        connection.last_error_code = None
    session.flush()
    return connection


def _ensure_smoke_run(
    session: Session,
    *,
    owner_user_id: str,
    agent: AgentRegistration,
    idempotency_key: str,
    correlation_id: str,
    now: datetime,
) -> AgentRun:
    run = session.scalar(
        select(AgentRun).where(
            AgentRun.owner_user_id == owner_user_id,
            AgentRun.idempotency_key == idempotency_key,
        )
    )
    if run is not None:
        if run.agent_id != agent.agent_id:
            raise ApiError(
                409,
                "smoke_seed_idempotency_conflict",
                "Idempotency-Key is already bound to a different run.",
            )
        _ensure_smoke_run_steps(session, run=run)
        return run

    run = AgentRun(
        owner_user_id=owner_user_id,
        agent_id=agent.agent_id,
        status="succeeded",
        trigger_source="manual",
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
        timeout_seconds=300,
        started_at=now,
        completed_at=now,
    )
    session.add(run)
    session.flush()
    _ensure_smoke_run_steps(session, run=run)
    return run


def _ensure_smoke_run_steps(session: Session, *, run: AgentRun) -> None:
    existing = session.scalar(
        select(AgentRunStep).where(AgentRunStep.run_id == run.run_id)
    )
    if existing is not None:
        return
    record_run_step(
        session,
        run_id=run.run_id,
        step_name="synthetic_connector_health",
        status="succeeded",
        metadata={
            "scope": SMOKE_SEED_SCOPE,
            "synthetic": True,
            "connector_count": len(_SMOKE_CONNECTORS),
        },
    )
    record_run_step(
        session,
        run_id=run.run_id,
        step_name="synthetic_draft_approval_ready",
        status="succeeded",
        metadata={"scope": SMOKE_SEED_SCOPE, "synthetic": True},
    )


def _ensure_smoke_approval(
    session: Session,
    *,
    owner_user_id: str,
    agent: AgentRegistration,
    run: AgentRun,
    now: datetime,
) -> ApprovalRequest:
    action_reference = f"{SMOKE_SEED_SCOPE}:{run.run_id}"
    approval = session.scalar(
        select(ApprovalRequest).where(
            ApprovalRequest.owner_user_id == owner_user_id,
            ApprovalRequest.run_id == run.run_id,
            ApprovalRequest.action_reference == action_reference,
        )
    )
    if approval is not None:
        return approval
    return create_approval_request(
        session,
        owner_user_id=owner_user_id,
        agent_id=agent.agent_id,
        run_id=run.run_id,
        action_type="synthetic_draft_review",
        action_reference=action_reference,
        action_payload={
            "operation": "synthetic_noop_draft",
            "target_reference": "synthetic-smoke-record",
            "mailbox_data_used": False,
            "drive_data_used": False,
        },
        evidence_summary={
            "scope": SMOKE_SEED_SCOPE,
            "synthetic": True,
            "mailbox_data_used": False,
            "drive_data_used": False,
            "run_id": run.run_id,
            "connector_count": len(_SMOKE_CONNECTORS),
        },
        decision_context_manifest={
            "scope": SMOKE_SEED_SCOPE,
            "synthetic": True,
            "redaction_state": "metadata_only",
            "created_at": now.isoformat(),
        },
    )
