from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Header, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from atlas_api.core.auth import ExternalClientPrincipal, verify_external_client
from atlas_api.core.authorization import (
    ActorKind,
    AuthorizationContext,
    Channel,
    authorize,
)
from atlas_api.core.contracts import (
    PaginationParameters,
    success_payload,
    validate_idempotency_key,
)
from atlas_api.core.correlation import get_correlation_id
from atlas_api.core.errors import ApiError
from atlas_api.models.approval import ApprovalRequest, ManualHandlingRecord
from atlas_api.services.approval_contracts import (
    get_approval,
    get_manual_handling_record,
    list_approvals,
    list_manual_handling_records,
    submit_decision,
)
from atlas_api.services.approval_facts import revalidate_approval_facts
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.knowledge_facts import (
    begin_idempotent_operation,
    complete_idempotent_operation,
    resolve_owner_user_id,
)

approval_router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])
manual_router = APIRouter(
    prefix="/api/v1/manual-handling",
    tags=["manual-handling"],
)

ExternalClientDependency = Annotated[
    ExternalClientPrincipal,
    Depends(verify_external_client),
]


class ApprovalSummaryPayload(BaseModel):
    approval_id: str
    status: str
    revision: int
    action_type: str
    action_reference: str
    expires_at: datetime | None
    created_at: datetime


class ApprovalEvidencePayload(ApprovalSummaryPayload):
    action_payload_hash: str
    evidence_summary: dict[str, Any]
    decision_context_manifest: dict[str, Any]
    continuation_status: str
    superseded_by_approval_id: str | None


class ApprovalDecisionPayload(BaseModel):
    decision: str = Field(pattern="^(approve|reject|edit_approve)$")
    approval_revision: int = Field(ge=1)
    reason: str | None = Field(default=None, max_length=1000)
    edited_action_payload: dict[str, Any] | None = None


class ApprovalDecisionResultPayload(BaseModel):
    approval_id: str
    status: str
    revision: int
    decision: str
    decision_channel: str
    continuation_status: str
    superseded_by_approval_id: str | None


class ApprovalFactsRevalidationPayload(BaseModel):
    approval_id: str
    status: str
    continuation_status: str
    facts_checked: int
    failure_reason_code: str | None
    failures: list[dict[str, str]]


class ManualHandlingPayload(BaseModel):
    manual_handling_id: str
    status: str
    agent_id: str | None
    run_id: str | None
    source_reference: str
    reason_category: str
    sensitivity_classification: str
    held_at: datetime
    resolved_at: datetime | None
    metadata_json: dict[str, Any]
    created_at: datetime


class PageMeta(BaseModel):
    correlation_id: str | None
    next_cursor: str | None = None


class ApprovalListResponse(BaseModel):
    data: list[ApprovalSummaryPayload]
    meta: PageMeta


class ApprovalEvidenceResponse(BaseModel):
    data: ApprovalEvidencePayload
    meta: PageMeta


class ApprovalDecisionResponse(BaseModel):
    data: ApprovalDecisionResultPayload
    meta: PageMeta


class ApprovalFactsRevalidationResponse(BaseModel):
    data: ApprovalFactsRevalidationPayload
    meta: PageMeta


class ManualHandlingListResponse(BaseModel):
    data: list[ManualHandlingPayload]
    meta: PageMeta


class ManualHandlingResponse(BaseModel):
    data: ManualHandlingPayload
    meta: PageMeta


@approval_router.get(
    "",
    response_model=ApprovalListResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def list_pending_approvals(
    request: Request,
    principal: ExternalClientDependency,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str, Query(min_length=1, max_length=40)] = "pending",
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(
            session,
            principal,
            resource="approval",
            action="list",
        )
        page = list_approvals(
            session,
            owner_user_id=owner_user_id,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status=status,
        )
        _audit(
            session,
            principal,
            resource_type="approval",
            action="list",
            result="succeeded",
            resource_id=None,
            metadata={"count": len(page.approvals), "status": status},
        )
        session.commit()
        return success_payload(
            [_approval_summary(approval) for approval in page.approvals],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@approval_router.get(
    "/{approval_id}/evidence",
    response_model=ApprovalEvidenceResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_approval_evidence(
    approval_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(
            session,
            principal,
            resource="approval",
            action="read_evidence",
        )
        approval = get_approval(
            session,
            owner_user_id=owner_user_id,
            approval_id=approval_id,
        )
        _audit(
            session,
            principal,
            resource_type="approval",
            action="read_evidence",
            result="succeeded",
            resource_id=approval.approval_id,
        )
        session.commit()
        return success_payload(
            _approval_evidence(approval),
            meta={"correlation_id": get_correlation_id()},
        )


@approval_router.post(
    "/{approval_id}/decisions",
    response_model=ApprovalDecisionResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def submit_approval_decision(
    approval_id: str,
    payload: ApprovalDecisionPayload,
    request: Request,
    principal: ExternalClientDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    session_factory = _require_session_factory(request)
    payload_dict = {"approval_id": approval_id, **payload.model_dump(mode="json")}
    with session_factory() as session:
        owner_user_id = _authorized_owner(
            session,
            principal,
            resource="approval",
            action="decide",
        )
        idem = begin_idempotent_operation(
            session,
            actor_id=principal.external_client_id,
            operation="approval.decide",
            idempotency_key=key,
            payload=payload_dict,
            resource_type="approval",
        )
        if idem.replayed and idem.record.resource_id is not None:
            approval = get_approval(
                session,
                owner_user_id=owner_user_id,
                approval_id=idem.record.resource_id,
            )
            decision = payload.decision
        else:
            approval, _decision_record = submit_decision(
                session,
                owner_user_id=owner_user_id,
                approval_id=approval_id,
                decision=payload.decision,
                submitted_revision=payload.approval_revision,
                channel="external",
                external_client_id=principal.external_client_id,
                reviewer_user_id=owner_user_id,
                reason=payload.reason,
                edited_action_payload=payload.edited_action_payload,
            )
            decision = payload.decision
            complete_idempotent_operation(idem.record, resource_id=approval.approval_id)
        _audit(
            session,
            principal,
            resource_type="approval",
            action="decide",
            result="succeeded",
            resource_id=approval.approval_id,
            metadata={"decision": decision, "idempotent_replay": idem.replayed},
        )
        session.commit()
        return success_payload(
            _decision_payload(approval, decision=decision),
            meta={"correlation_id": get_correlation_id()},
        )


@approval_router.post(
    "/{approval_id}/facts-used/revalidate",
    response_model=ApprovalFactsRevalidationResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def revalidate_approval_facts_used(
    approval_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(
            session,
            principal,
            resource="approval",
            action="revalidate_facts",
        )
        approval = get_approval(
            session,
            owner_user_id=owner_user_id,
            approval_id=approval_id,
        )
        result = revalidate_approval_facts(session, approval)
        _audit(
            session,
            principal,
            resource_type="approval",
            action="revalidate_facts",
            result="succeeded" if result.status == "passed" else "failed",
            resource_id=approval.approval_id,
            reason_code=result.failure_reason_code,
            metadata={
                "continuation_status": result.continuation_status,
                "facts_checked": result.facts_checked,
                "failure_count": len(result.failures),
            },
        )
        session.commit()
        return success_payload(
            {
                "approval_id": result.approval_id,
                "status": result.status,
                "continuation_status": result.continuation_status,
                "facts_checked": result.facts_checked,
                "failure_reason_code": result.failure_reason_code,
                "failures": [
                    {
                        "knowledge_fact_id": failure.knowledge_fact_id,
                        "reason_code": failure.reason_code,
                    }
                    for failure in result.failures
                ],
            },
            meta={"correlation_id": get_correlation_id()},
        )


@manual_router.get(
    "",
    response_model=ManualHandlingListResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def list_manual_handling(
    request: Request,
    principal: ExternalClientDependency,
    cursor: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str, Query(min_length=1, max_length=40)] = "pending",
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(
            session,
            principal,
            resource="manual_handling",
            action="list",
        )
        page = list_manual_handling_records(
            session,
            owner_user_id=owner_user_id,
            pagination=PaginationParameters(cursor=cursor, limit=limit),
            status=status,
        )
        _audit(
            session,
            principal,
            resource_type="manual_handling",
            action="list",
            result="succeeded",
            resource_id=None,
            metadata={"count": len(page.records), "status": status},
        )
        session.commit()
        return success_payload(
            [_manual_payload(record) for record in page.records],
            meta={
                "correlation_id": get_correlation_id(),
                "next_cursor": page.next_cursor,
            },
        )


@manual_router.get(
    "/{manual_handling_id}",
    response_model=ManualHandlingResponse,
    openapi_extra={"security": [{"ExternalClientHmac": []}]},
)
def read_manual_handling(
    manual_handling_id: str,
    request: Request,
    principal: ExternalClientDependency,
) -> dict[str, object]:
    session_factory = _require_session_factory(request)
    with session_factory() as session:
        owner_user_id = _authorized_owner(
            session,
            principal,
            resource="manual_handling",
            action="read",
        )
        record = get_manual_handling_record(
            session,
            owner_user_id=owner_user_id,
            manual_handling_id=manual_handling_id,
        )
        _audit(
            session,
            principal,
            resource_type="manual_handling",
            action="read",
            result="succeeded",
            resource_id=record.manual_handling_id,
        )
        session.commit()
        return success_payload(
            _manual_payload(record),
            meta={"correlation_id": get_correlation_id()},
        )


def _require_session_factory(request: Request) -> Callable[[], Session]:
    session_factory = cast(
        "Callable[[], Session] | None",
        request.app.state.session_factory,
    )
    if session_factory is None:
        raise ApiError(
            503,
            "approval_store_not_configured",
            "Approval storage is not configured.",
        )
    return session_factory


def _authorized_owner(
    session: Session,
    principal: ExternalClientPrincipal,
    *,
    resource: str,
    action: str,
) -> str:
    risk_level = "medium" if action in {"decide", "revalidate_facts"} else "low"
    decision = authorize(
        AuthorizationContext(
            actor_kind=ActorKind.EXTERNAL_CLIENT,
            actor_id=principal.external_client_id,
            channel=Channel.EXTERNAL_PRODUCT_CLIENT,
            resource=resource,
            action=action,
            risk_level=risk_level,
        )
    )
    if not decision.allowed:
        _audit(
            session,
            principal,
            resource_type=resource,
            action=action,
            result="denied",
            resource_id=None,
            reason_code=decision.reason_code,
        )
        session.commit()
        raise ApiError(403, "authorization_denied", "Request is not authorized.")
    return resolve_owner_user_id(session, principal.external_client_id)


def _audit(
    session: Session,
    principal: ExternalClientPrincipal,
    *,
    resource_type: str,
    action: str,
    result: str,
    resource_id: str | None,
    reason_code: str | None = None,
    metadata: dict[str, object | None] | None = None,
) -> None:
    record_audit_event(
        session,
        AuditEventInput(
            event_type=f"{resource_type}.{action}",
            actor_type="external_client",
            actor_id=principal.external_client_id,
            channel="external_product_client",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            reason_code=reason_code,
            correlation_id=get_correlation_id(),
            metadata=metadata,
        ),
    )


def _approval_summary(approval: ApprovalRequest) -> dict[str, object]:
    return {
        "approval_id": approval.approval_id,
        "status": approval.status,
        "revision": approval.revision,
        "action_type": approval.action_type,
        "action_reference": approval.action_reference,
        "expires_at": approval.expires_at,
        "created_at": approval.created_at,
    }


def _approval_evidence(approval: ApprovalRequest) -> dict[str, object]:
    return {
        **_approval_summary(approval),
        "action_payload_hash": approval.action_payload_hash,
        "evidence_summary": approval.evidence_summary,
        "decision_context_manifest": approval.decision_context_manifest,
        "continuation_status": approval.continuation_status,
        "superseded_by_approval_id": approval.superseded_by_approval_id,
    }


def _decision_payload(
    approval: ApprovalRequest,
    *,
    decision: str,
) -> dict[str, object]:
    return {
        "approval_id": approval.approval_id,
        "status": approval.status,
        "revision": approval.revision,
        "decision": decision,
        "decision_channel": approval.decision_channel or "external",
        "continuation_status": approval.continuation_status,
        "superseded_by_approval_id": approval.superseded_by_approval_id,
    }


def _manual_payload(record: ManualHandlingRecord) -> dict[str, object]:
    return {
        "manual_handling_id": record.manual_handling_id,
        "status": record.status,
        "agent_id": record.agent_id,
        "run_id": record.run_id,
        "source_reference": record.source_reference,
        "reason_category": record.reason_category,
        "sensitivity_classification": record.sensitivity_classification,
        "held_at": record.held_at,
        "resolved_at": record.resolved_at,
        "metadata_json": _safe_manual_metadata(record.metadata_json),
        "created_at": record.created_at,
    }


def _safe_manual_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    blocked_fragments = ("content", "body", "text", "token", "secret")
    return {
        key: value
        for key, value in metadata.items()
        if not any(fragment in key.lower() for fragment in blocked_fragments)
    }
