from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.core.contracts import PaginationParameters, decode_cursor, encode_cursor
from atlas_api.core.errors import ApiError
from atlas_api.db.base import utc_now
from atlas_api.models.approval import (
    ApprovalDecision,
    ApprovalRequest,
    ManualHandlingRecord,
)

ALLOWED_APPROVAL_STATUSES = frozenset(
    {"pending", "approved", "rejected", "expired", "superseded"}
)
ALLOWED_DECISIONS = frozenset({"approve", "reject", "edit_approve"})
ALLOWED_MANUAL_REASONS = frozenset({"Clinical", "ProtectedHealthInformation"})


@dataclass(frozen=True)
class ApprovalPage:
    approvals: list[ApprovalRequest]
    next_cursor: str | None


@dataclass(frozen=True)
class ManualHandlingPage:
    records: list[ManualHandlingRecord]
    next_cursor: str | None


def create_approval_request(
    session: Session,
    *,
    owner_user_id: str,
    action_type: str,
    action_reference: str,
    action_payload: dict[str, Any],
    evidence_summary: dict[str, Any],
    decision_context_manifest: dict[str, Any],
    agent_id: str | None = None,
    run_id: str | None = None,
    expires_at: datetime | None = None,
) -> ApprovalRequest:
    approval = ApprovalRequest(
        owner_user_id=owner_user_id,
        agent_id=agent_id,
        run_id=run_id,
        status="pending",
        revision=1,
        action_type=action_type,
        action_reference=action_reference,
        action_payload_hash=_payload_hash(action_payload),
        evidence_summary=evidence_summary,
        decision_context_manifest=decision_context_manifest,
        expires_at=expires_at,
        continuation_status="not_requested",
    )
    session.add(approval)
    session.flush()
    return approval


def list_approvals(
    session: Session,
    *,
    owner_user_id: str,
    pagination: PaginationParameters,
    status: str = "pending",
) -> ApprovalPage:
    if status not in ALLOWED_APPROVAL_STATUSES:
        raise ApiError(422, "approval_status_invalid", "Approval status is invalid.")
    query = select(ApprovalRequest).where(
        ApprovalRequest.owner_user_id == owner_user_id,
        ApprovalRequest.status == status,
    )
    query = _apply_approval_cursor(query, pagination.cursor)
    query = query.order_by(ApprovalRequest.created_at, ApprovalRequest.approval_id)
    approvals = list(session.scalars(query.limit(pagination.limit + 1)))
    next_cursor = None
    if len(approvals) > pagination.limit:
        approvals = approvals[: pagination.limit]
        last = approvals[-1]
        next_cursor = encode_cursor(
            {"created_at": last.created_at.isoformat(), "approval_id": last.approval_id}
        )
    return ApprovalPage(approvals=approvals, next_cursor=next_cursor)


def get_approval(
    session: Session,
    *,
    owner_user_id: str,
    approval_id: str,
) -> ApprovalRequest:
    approval = session.get(ApprovalRequest, approval_id)
    if approval is None or approval.owner_user_id != owner_user_id:
        raise ApiError(404, "approval_not_found", "Approval was not found.")
    return approval


def submit_decision(
    session: Session,
    *,
    owner_user_id: str,
    approval_id: str,
    decision: str,
    submitted_revision: int,
    channel: str,
    external_client_id: str | None,
    reviewer_user_id: str,
    reason: str | None = None,
    edited_action_payload: dict[str, Any] | None = None,
) -> tuple[ApprovalRequest, ApprovalDecision]:
    if decision not in ALLOWED_DECISIONS:
        raise ApiError(422, "approval_decision_invalid", "Decision is invalid.")
    approval = get_approval(
        session,
        owner_user_id=owner_user_id,
        approval_id=approval_id,
    )
    _validate_decidable(approval, submitted_revision=submitted_revision)
    if decision == "edit_approve":
        if edited_action_payload is None:
            raise ApiError(
                422,
                "approval_edit_payload_required",
                "Edited action payload is required.",
            )
        replacement = create_approval_request(
            session,
            owner_user_id=owner_user_id,
            action_type=approval.action_type,
            action_reference=f"{approval.action_reference}:edited",
            action_payload=edited_action_payload,
            evidence_summary={
                **approval.evidence_summary,
                "supersedes_approval_id": approval.approval_id,
            },
            decision_context_manifest={
                **approval.decision_context_manifest,
                "supersedes_approval_id": approval.approval_id,
            },
            agent_id=approval.agent_id,
            run_id=approval.run_id,
            expires_at=approval.expires_at,
        )
        approval.status = "superseded"
        approval.superseded_by_approval_id = replacement.approval_id
        approval.decided_at = utc_now()
        approval = replacement
        submitted_revision = replacement.revision
    approval.status = (
        "approved" if decision in {"approve", "edit_approve"} else "rejected"
    )
    approval.decided_at = utc_now()
    approval.decision_channel = channel
    approval.external_client_id = external_client_id
    approval.reviewer_user_id = reviewer_user_id
    approval.continuation_status = (
        "pending" if approval.status == "approved" else "not_requested"
    )
    decision_record = ApprovalDecision(
        approval_id=approval.approval_id,
        decision=decision,
        submitted_revision=submitted_revision,
        channel=channel,
        external_client_id=external_client_id,
        reviewer_user_id=reviewer_user_id,
        reason=reason,
        edited_action_payload_hash=(
            _payload_hash(edited_action_payload)
            if edited_action_payload is not None
            else None
        ),
    )
    session.add(decision_record)
    session.flush()
    return approval, decision_record


def create_manual_handling_record(
    session: Session,
    *,
    owner_user_id: str,
    source_reference: str,
    reason_category: str,
    sensitivity_classification: str,
    agent_id: str | None = None,
    run_id: str | None = None,
    metadata_json: dict[str, Any] | None = None,
) -> ManualHandlingRecord:
    if reason_category not in ALLOWED_MANUAL_REASONS:
        raise ApiError(
            422,
            "manual_handling_reason_invalid",
            "Manual-handling reason is invalid.",
        )
    record = ManualHandlingRecord(
        owner_user_id=owner_user_id,
        agent_id=agent_id,
        run_id=run_id,
        source_reference=source_reference,
        reason_category=reason_category,
        sensitivity_classification=sensitivity_classification,
        status="pending",
        metadata_json=metadata_json or {},
    )
    session.add(record)
    session.flush()
    return record


def list_manual_handling_records(
    session: Session,
    *,
    owner_user_id: str,
    pagination: PaginationParameters,
    status: str = "pending",
) -> ManualHandlingPage:
    query = select(ManualHandlingRecord).where(
        ManualHandlingRecord.owner_user_id == owner_user_id,
        ManualHandlingRecord.status == status,
    )
    query = _apply_manual_cursor(query, pagination.cursor)
    query = query.order_by(
        ManualHandlingRecord.created_at,
        ManualHandlingRecord.manual_handling_id,
    )
    records = list(session.scalars(query.limit(pagination.limit + 1)))
    next_cursor = None
    if len(records) > pagination.limit:
        records = records[: pagination.limit]
        last = records[-1]
        next_cursor = encode_cursor(
            {
                "created_at": last.created_at.isoformat(),
                "manual_handling_id": last.manual_handling_id,
            }
        )
    return ManualHandlingPage(records=records, next_cursor=next_cursor)


def get_manual_handling_record(
    session: Session,
    *,
    owner_user_id: str,
    manual_handling_id: str,
) -> ManualHandlingRecord:
    record = session.get(ManualHandlingRecord, manual_handling_id)
    if record is None or record.owner_user_id != owner_user_id:
        raise ApiError(
            404,
            "manual_handling_not_found",
            "Manual-handling record was not found.",
        )
    return record


def _validate_decidable(approval: ApprovalRequest, *, submitted_revision: int) -> None:
    if approval.status != "pending":
        raise ApiError(409, "approval_not_pending", "Approval is not pending.")
    if approval.revision != submitted_revision:
        raise ApiError(
            409,
            "approval_revision_conflict",
            "Approval revision does not match the reviewed evidence.",
        )
    if approval.expires_at is not None:
        expires_at = approval.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= utc_now():
            approval.status = "expired"
            raise ApiError(409, "approval_expired", "Approval has expired.")


def _apply_approval_cursor(query: Any, cursor: str | None) -> Any:
    if cursor is None:
        return query
    values = decode_cursor(cursor)
    created_at = datetime.fromisoformat(values["created_at"])
    approval_id = values["approval_id"]
    return query.where(
        (ApprovalRequest.created_at > created_at)
        | (
            (ApprovalRequest.created_at == created_at)
            & (ApprovalRequest.approval_id > approval_id)
        )
    )


def _apply_manual_cursor(query: Any, cursor: str | None) -> Any:
    if cursor is None:
        return query
    values = decode_cursor(cursor)
    created_at = datetime.fromisoformat(values["created_at"])
    manual_handling_id = values["manual_handling_id"]
    return query.where(
        (ManualHandlingRecord.created_at > created_at)
        | (
            (ManualHandlingRecord.created_at == created_at)
            & (ManualHandlingRecord.manual_handling_id > manual_handling_id)
        )
    )


def _payload_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(serialized.encode()).hexdigest()
