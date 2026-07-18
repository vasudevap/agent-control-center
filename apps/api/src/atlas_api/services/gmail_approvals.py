from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy.orm import Session

from atlas_api.core.errors import ApiError
from atlas_api.models.approval import ApprovalRequest
from atlas_api.models.gmail_message import (
    GmailDraftRecord,
    GmailSendOutcomeRecord,
)
from atlas_api.services.approval_contracts import create_approval_request, get_approval
from atlas_api.services.approval_facts import revalidate_approval_facts
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.connectors import authorize_connector_operation
from atlas_api.services.gmail_messages import (
    GMAIL_AGENT_ID,
    ensure_gmail_message_allowed_for_downstream_use,
)
from atlas_api.services.knowledge_facts import (
    begin_idempotent_operation,
    complete_idempotent_operation,
)

SendOutcome = Literal["sent", "failed", "indeterminate"]


@dataclass(frozen=True)
class FakeSendResult:
    outcome: SendOutcome
    provider_send_reference: str | None
    reason_code: str | None = None


@dataclass(frozen=True)
class GmailSendContinuationResult:
    outcome: GmailSendOutcomeRecord
    replayed: bool


class FakeGmailSendProvider:
    def __init__(self, result: FakeSendResult) -> None:
        self.result = result
        self.send_attempts: list[str] = []

    def send_draft(self, provider_draft_reference: str) -> FakeSendResult:
        self.send_attempts.append(provider_draft_reference)
        return self.result


def create_gmail_send_approval(
    session: Session,
    *,
    owner_user_id: str,
    gmail_draft_record_id: str,
    expires_at: datetime | None = None,
    actor_id: str = GMAIL_AGENT_ID,
    correlation_id: str | None = None,
) -> ApprovalRequest:
    draft = _get_draft(
        session,
        owner_user_id=owner_user_id,
        gmail_draft_record_id=gmail_draft_record_id,
    )
    ensure_gmail_message_allowed_for_downstream_use(
        session,
        owner_user_id=owner_user_id,
        gmail_message_record_id=draft.gmail_message_record_id,
        downstream_use="approval",
    )
    action_payload = {
        "gmail_draft_record_id": draft.gmail_draft_record_id,
        "provider_draft_reference": draft.provider_draft_reference,
        "draft_body_hash": draft.body_hash,
    }
    evidence_summary = {
        **draft.evidence_summary,
        "gmail_draft_record_id": draft.gmail_draft_record_id,
        "provider_draft_reference": draft.provider_draft_reference,
    }
    manifest = {
        **draft.decision_context_manifest,
        "gmail_draft_record_id": draft.gmail_draft_record_id,
        "provider_draft_reference": draft.provider_draft_reference,
        "draft_body_hash": draft.body_hash,
    }
    approval = create_approval_request(
        session,
        owner_user_id=owner_user_id,
        action_type="gmail.send",
        action_reference=f"gmail_draft:{draft.gmail_draft_record_id}",
        action_payload=action_payload,
        evidence_summary=evidence_summary,
        decision_context_manifest=manifest,
        agent_id=actor_id,
        expires_at=expires_at,
    )
    _audit(
        session,
        event_type="gmail.send_approval_pending",
        action="create_send_approval",
        result="succeeded",
        resource_type="approval",
        resource_id=approval.approval_id,
        actor_id=actor_id,
        correlation_id=correlation_id,
        reason_code=None,
    )
    session.flush()
    return approval


def continue_approved_gmail_send(
    session: Session,
    *,
    owner_user_id: str,
    approval_id: str,
    provider: FakeGmailSendProvider,
    idempotency_key: str,
    actor_id: str = GMAIL_AGENT_ID,
    correlation_id: str | None = None,
) -> GmailSendContinuationResult:
    _validate_idempotency_key(idempotency_key)
    approval = get_approval(
        session,
        owner_user_id=owner_user_id,
        approval_id=approval_id,
    )
    if approval.status != "approved":
        raise ApiError(
            409,
            "gmail_send_approval_not_approved",
            "Gmail send approval is not approved.",
        )
    draft_id = _required_manifest_string(approval, "gmail_draft_record_id")
    draft = _get_draft(
        session,
        owner_user_id=owner_user_id,
        gmail_draft_record_id=draft_id,
    )
    _revalidate_draft_binding(approval, draft)
    idem = begin_idempotent_operation(
        session,
        actor_id=actor_id,
        operation="gmail.send",
        idempotency_key=idempotency_key,
        payload={
            "approval_id": approval.approval_id,
            "gmail_draft_record_id": draft.gmail_draft_record_id,
            "provider_draft_reference": draft.provider_draft_reference,
            "draft_body_hash": draft.body_hash,
        },
        resource_type="gmail_send_outcome",
    )
    if idem.replayed and idem.record.resource_id is not None:
        outcome = session.get(GmailSendOutcomeRecord, idem.record.resource_id)
        if outcome is None:
            raise ApiError(
                409,
                "gmail_send_idempotency_record_missing",
                "Gmail send idempotency record is missing.",
            )
        return GmailSendContinuationResult(outcome=outcome, replayed=True)
    if approval.continuation_status != "pending":
        raise ApiError(
            409,
            "gmail_send_continuation_not_pending",
            "Gmail send continuation is not pending.",
        )
    ensure_gmail_message_allowed_for_downstream_use(
        session,
        owner_user_id=owner_user_id,
        gmail_message_record_id=draft.gmail_message_record_id,
        downstream_use="send",
    )
    facts_result = revalidate_approval_facts(session, approval)
    if facts_result.status != "passed":
        raise ApiError(
            409,
            facts_result.failure_reason_code or "gmail_send_fact_revalidation_failed",
            "Gmail send fact revalidation failed.",
        )
    authorization = authorize_connector_operation(
        session,
        owner_user_id=owner_user_id,
        connection_id=draft.connection_id,
        operation_id="gmail.send_message_later",
        actor_id=actor_id,
        correlation_id=correlation_id,
    )
    if not authorization.allowed:
        approval.continuation_status = "blocked"
        raise ApiError(403, authorization.reason_code, "Connector operation denied.")
    send_result = provider.send_draft(draft.provider_draft_reference)
    outcome = GmailSendOutcomeRecord(
        owner_user_id=owner_user_id,
        approval_id=approval.approval_id,
        gmail_draft_record_id=draft.gmail_draft_record_id,
        provider_draft_reference=draft.provider_draft_reference,
        provider_send_reference=send_result.provider_send_reference,
        outcome=send_result.outcome,
        idempotency_key=idempotency_key,
        reason_code=send_result.reason_code,
        metadata_json={"outcome": send_result.outcome},
    )
    session.add(outcome)
    session.flush()
    complete_idempotent_operation(
        idem.record,
        resource_id=outcome.gmail_send_outcome_id,
    )
    approval.continuation_status = {
        "sent": "sent",
        "failed": "failed",
        "indeterminate": "indeterminate",
    }[send_result.outcome]
    _audit(
        session,
        event_type="gmail.send_outcome",
        action="continue_send",
        result=send_result.outcome,
        resource_type="gmail_send_outcome",
        resource_id=outcome.gmail_send_outcome_id,
        actor_id=actor_id,
        correlation_id=correlation_id,
        reason_code=send_result.reason_code,
    )
    session.flush()
    return GmailSendContinuationResult(outcome=outcome, replayed=False)


def _get_draft(
    session: Session,
    *,
    owner_user_id: str,
    gmail_draft_record_id: str,
) -> GmailDraftRecord:
    draft = session.get(GmailDraftRecord, gmail_draft_record_id)
    if draft is None or draft.owner_user_id != owner_user_id:
        raise ApiError(404, "gmail_draft_not_found", "Gmail draft was not found.")
    return draft


def _revalidate_draft_binding(
    approval: ApprovalRequest,
    draft: GmailDraftRecord,
) -> None:
    if _required_manifest_string(approval, "provider_draft_reference") != (
        draft.provider_draft_reference
    ):
        raise ApiError(
            409,
            "gmail_draft_reference_changed",
            "Gmail draft reference changed.",
        )
    if _required_manifest_string(approval, "draft_body_hash") != draft.body_hash:
        raise ApiError(409, "gmail_draft_hash_changed", "Gmail draft hash changed.")


def _required_manifest_string(approval: ApprovalRequest, key: str) -> str:
    value = approval.decision_context_manifest.get(key)
    if not isinstance(value, str) or not value:
        raise ApiError(
            422,
            "gmail_send_manifest_invalid",
            "Gmail send manifest is invalid.",
        )
    return value


def _validate_idempotency_key(value: str) -> None:
    if len(value) < 16 or len(value) > 128 or any(char.isspace() for char in value):
        raise ApiError(
            422,
            "gmail_send_idempotency_key_invalid",
            "Gmail send idempotency key is invalid.",
        )


def _audit(
    session: Session,
    *,
    event_type: str,
    action: str,
    result: str,
    resource_type: str,
    resource_id: str,
    actor_id: str,
    correlation_id: str | None,
    reason_code: str | None,
) -> None:
    record_audit_event(
        session,
        AuditEventInput(
            event_type=event_type,
            actor_type="service",
            actor_id=actor_id,
            channel="service",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            reason_code=reason_code,
            correlation_id=correlation_id,
            metadata={
                "resource_id": resource_id,
                "resource_type": resource_type,
                "outcome": result,
            },
        ),
    )


def provider_send_reference(provider_draft_reference: str) -> str:
    return "sent:" + hashlib.sha256(
        provider_draft_reference.encode("utf-8")
    ).hexdigest()[:32]
