from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from atlas_api.core.errors import ApiError
from atlas_api.models.gmail_message import GmailActionOperation, GmailMessageRecord
from atlas_api.services.audit import AuditEventInput, record_audit_event
from atlas_api.services.connectors import (
    DRIVE_SCOPE_FILE,
    authorize_connector_operation,
    get_connection,
)
from atlas_api.services.gmail_messages import (
    GMAIL_AGENT_ID,
    ensure_gmail_message_allowed_for_downstream_use,
)
from atlas_api.services.knowledge_facts import (
    begin_idempotent_operation,
    complete_idempotent_operation,
)

LOW_RISK_ACTIONS = frozenset(
    {
        "gmail.apply_label",
        "gmail.archive_message",
        "gmail.get_attachment",
        "drive.save_attachment",
    }
)
MAX_REFERENCE_LENGTH = 160


@dataclass(frozen=True)
class GmailLowRiskActionPolicy:
    label_by_category: dict[str, str]
    archive_categories: frozenset[str]
    attachment_save_categories: frozenset[str]
    drive_folder_reference: str | None = None


@dataclass(frozen=True)
class FakeRetrievedAttachment:
    provider_attachment_reference: str
    filename: str
    mime_type: str
    size_bytes: int
    content_hash: str


@dataclass(frozen=True)
class LowRiskActionResult:
    operations: list[GmailActionOperation]
    denied_count: int
    replayed_count: int


class ProviderOperationError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class FakeGmailActionProvider:
    def __init__(
        self,
        *,
        attachments: dict[str, bytes] | None = None,
        fail_operations: set[str] | None = None,
    ) -> None:
        self.attachments = attachments or {}
        self.fail_operations = fail_operations or set()
        self.applied_labels: list[tuple[str, str]] = []
        self.archived_messages: list[str] = []
        self.retrieved_attachments: list[tuple[str, str]] = []

    def apply_label(self, provider_message_reference: str, label_name: str) -> str:
        self._maybe_fail("gmail.apply_label")
        self.applied_labels.append((provider_message_reference, label_name))
        return _provider_operation_reference(
            "label",
            provider_message_reference,
            label_name,
        )

    def archive_message(self, provider_message_reference: str) -> str:
        self._maybe_fail("gmail.archive_message")
        self.archived_messages.append(provider_message_reference)
        return _provider_operation_reference("archive", provider_message_reference)

    def get_attachment(
        self,
        provider_message_reference: str,
        provider_attachment_reference: str,
        *,
        filename: str,
        mime_type: str,
        size_bytes: int,
    ) -> FakeRetrievedAttachment:
        self._maybe_fail("gmail.get_attachment")
        content = self.attachments.get(provider_attachment_reference, b"")
        self.retrieved_attachments.append(
            (provider_message_reference, provider_attachment_reference)
        )
        return FakeRetrievedAttachment(
            provider_attachment_reference=provider_attachment_reference,
            filename=filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            content_hash=_hash_bytes(content),
        )

    def _maybe_fail(self, operation_type: str) -> None:
        if operation_type in self.fail_operations:
            raise ProviderOperationError(f"{operation_type}.provider_failed")


class FakeDriveProvider:
    def __init__(self, *, fail_operations: set[str] | None = None) -> None:
        self.fail_operations = fail_operations or set()
        self.saved_attachments: list[tuple[str, str, str]] = []

    def save_attachment(
        self,
        *,
        folder_reference: str,
        attachment: FakeRetrievedAttachment,
    ) -> str:
        if "drive.save_attachment" in self.fail_operations:
            raise ProviderOperationError("drive.save_attachment.provider_failed")
        provider_file_reference = _provider_operation_reference(
            "drive-file",
            folder_reference,
            attachment.provider_attachment_reference,
            attachment.content_hash,
        )
        self.saved_attachments.append(
            (
                folder_reference,
                attachment.provider_attachment_reference,
                provider_file_reference,
            )
        )
        return provider_file_reference


def execute_low_risk_mailbox_actions(
    session: Session,
    *,
    owner_user_id: str,
    gmail_message_record_id: str,
    gmail_provider: FakeGmailActionProvider,
    drive_provider: FakeDriveProvider,
    policy: GmailLowRiskActionPolicy,
    idempotency_key_prefix: str,
    drive_connection_id: str | None = None,
    actor_id: str = GMAIL_AGENT_ID,
    correlation_id: str | None = None,
) -> LowRiskActionResult:
    _validate_idempotency_prefix(idempotency_key_prefix)
    record = _load_message_record(
        session,
        owner_user_id=owner_user_id,
        gmail_message_record_id=gmail_message_record_id,
    )
    denied_count = 0
    replayed_count = 0
    operations: list[GmailActionOperation] = []
    try:
        ensure_gmail_message_allowed_for_downstream_use(
            session,
            owner_user_id=owner_user_id,
            gmail_message_record_id=gmail_message_record_id,
            downstream_use="action",
        )
    except ApiError as exc:
        operations.append(
            _record_denied_operation(
                session,
                record=record,
                operation_type="gmail.low_risk_actions",
                idempotency_key=f"{idempotency_key_prefix}:gate",
                reason_code=exc.code,
                actor_id=actor_id,
                correlation_id=correlation_id,
            )
        )
        session.flush()
        raise
    planned_actions = _planned_actions(record, policy)
    if not planned_actions:
        operations.append(
            _record_denied_operation(
                session,
                record=record,
                operation_type="gmail.low_risk_actions",
                idempotency_key=f"{idempotency_key_prefix}:policy",
                reason_code="gmail_action_policy_denied",
                actor_id=actor_id,
                correlation_id=correlation_id,
            )
        )
        session.flush()
        return LowRiskActionResult(
            operations=operations,
            denied_count=1,
            replayed_count=0,
        )
    for action in planned_actions:
        if action.operation_type == "gmail.get_attachment":
            attachment_operations, attachment_denials, attachment_replays = (
                _execute_attachment_pair(
                    session,
                    record=record,
                    action=action,
                    gmail_provider=gmail_provider,
                    drive_provider=drive_provider,
                    policy=policy,
                    idempotency_key_prefix=idempotency_key_prefix,
                    drive_connection_id=drive_connection_id,
                    actor_id=actor_id,
                    correlation_id=correlation_id,
                )
            )
            operations.extend(attachment_operations)
            denied_count += attachment_denials
            replayed_count += attachment_replays
            continue
        try:
            operation, replayed = _execute_action(
                session,
                record=record,
                action=action,
                gmail_provider=gmail_provider,
                drive_provider=drive_provider,
                policy=policy,
                idempotency_key_prefix=idempotency_key_prefix,
                drive_connection_id=drive_connection_id,
                actor_id=actor_id,
                correlation_id=correlation_id,
            )
            replayed_count += int(replayed)
            operations.append(operation)
        except ApiError as exc:
            denied_count += int(exc.status_code < 500)
            operations.append(
                _record_denied_operation(
                    session,
                    record=record,
                    operation_type=action.operation_type,
                    idempotency_key=action.idempotency_key(idempotency_key_prefix),
                    reason_code=exc.code,
                    actor_id=actor_id,
                    correlation_id=correlation_id,
                    provider_attachment_reference=action.provider_attachment_reference,
                    target_reference=action.target_reference,
                )
            )
    session.flush()
    return LowRiskActionResult(
        operations=operations,
        denied_count=denied_count,
        replayed_count=replayed_count,
    )


@dataclass(frozen=True)
class _PlannedAction:
    operation_type: str
    target_reference: str | None = None
    provider_attachment_reference: str | None = None
    attachment_payload: dict[str, Any] | None = None

    def idempotency_key(self, prefix: str) -> str:
        values = [
            prefix,
            self.operation_type,
            self.target_reference or "none",
            self.provider_attachment_reference or "none",
        ]
        return ":".join(_safe_reference(value) for value in values)


def _planned_actions(
    record: GmailMessageRecord,
    policy: GmailLowRiskActionPolicy,
) -> list[_PlannedAction]:
    actions: list[_PlannedAction] = []
    label = policy.label_by_category.get(record.classification_category)
    if label is not None:
        actions.append(_PlannedAction("gmail.apply_label", target_reference=label))
    if record.classification_category in policy.archive_categories:
        actions.append(_PlannedAction("gmail.archive_message"))
    if record.classification_category in policy.attachment_save_categories:
        actions.extend(
            _PlannedAction(
                "gmail.get_attachment",
                provider_attachment_reference=str(
                    attachment["provider_attachment_reference"]
                ),
                attachment_payload=attachment,
            )
            for attachment in record.attachment_metadata
        )
    return actions


def _execute_action(
    session: Session,
    *,
    record: GmailMessageRecord,
    action: _PlannedAction,
    gmail_provider: FakeGmailActionProvider,
    drive_provider: FakeDriveProvider,
    policy: GmailLowRiskActionPolicy,
    idempotency_key_prefix: str,
    drive_connection_id: str | None,
    actor_id: str,
    correlation_id: str | None,
) -> tuple[GmailActionOperation, bool]:
    idempotency_key = action.idempotency_key(idempotency_key_prefix)
    idem = begin_idempotent_operation(
        session,
        actor_id=actor_id,
        operation=action.operation_type,
        idempotency_key=idempotency_key,
        payload={
            "gmail_message_record_id": record.gmail_message_record_id,
            "operation_type": action.operation_type,
            "target_reference": action.target_reference,
            "provider_attachment_reference": action.provider_attachment_reference,
        },
        resource_type="gmail_action_operation",
    )
    if idem.replayed and idem.record.resource_id is not None:
        operation = session.get(GmailActionOperation, idem.record.resource_id)
        if operation is None:
            raise ApiError(
                409,
                "gmail_action_idempotency_record_missing",
                "Gmail action idempotency record is missing.",
            )
        return operation, True
    authorization = authorize_connector_operation(
        session,
        owner_user_id=record.owner_user_id,
        connection_id=record.connection_id,
        operation_id=action.operation_type,
        actor_id=actor_id,
        correlation_id=correlation_id,
    )
    if not authorization.allowed:
        raise ApiError(403, authorization.reason_code, "Connector operation denied.")
    try:
        provider_reference, metadata = _call_provider(
            record=record,
            action=action,
            gmail_provider=gmail_provider,
            session=session,
            actor_id=actor_id,
            correlation_id=correlation_id,
        )
    except ProviderOperationError as exc:
        operation = _create_action_operation(
            session,
            record=record,
            operation_type=action.operation_type,
            status="failed",
            idempotency_key=idempotency_key,
            provider_attachment_reference=action.provider_attachment_reference,
            target_reference=action.target_reference,
            reason_code=exc.code,
            metadata_json={"outcome": "provider_failed"},
        )
        complete_idempotent_operation(
            idem.record,
            resource_id=operation.gmail_action_operation_id,
        )
        _audit_action(
            session,
            operation,
            actor_id=actor_id,
            result="failed",
            correlation_id=correlation_id,
        )
        return operation, False
    operation = _create_action_operation(
        session,
        record=record,
        operation_type=action.operation_type,
        status="succeeded",
        idempotency_key=idempotency_key,
        provider_operation_reference=provider_reference,
        provider_attachment_reference=action.provider_attachment_reference,
        target_reference=action.target_reference,
        metadata_json=metadata,
    )
    complete_idempotent_operation(
        idem.record,
        resource_id=operation.gmail_action_operation_id,
    )
    _audit_action(
        session,
        operation,
        actor_id=actor_id,
        result="succeeded",
        correlation_id=correlation_id,
    )
    return operation, False


def _call_provider(
    *,
    record: GmailMessageRecord,
    action: _PlannedAction,
    gmail_provider: FakeGmailActionProvider,
    session: Session,
    actor_id: str,
    correlation_id: str | None,
) -> tuple[str, dict[str, Any]]:
    if action.operation_type == "gmail.apply_label":
        assert action.target_reference is not None
        return (
            gmail_provider.apply_label(
                record.provider_message_reference,
                action.target_reference,
            ),
            {"label": action.target_reference},
        )
    if action.operation_type == "gmail.archive_message":
        return (
            gmail_provider.archive_message(record.provider_message_reference),
            {},
        )
    if action.operation_type == "gmail.get_attachment":
        attachment = _retrieve_attachment(record, action, gmail_provider)
        return (
            _provider_operation_reference(
                "attachment",
                attachment.provider_attachment_reference,
                attachment.content_hash,
            ),
            {
                "filename": attachment.filename,
                "mime_type": attachment.mime_type,
                "attachment_size_bytes": attachment.size_bytes,
                "attachment_content_hash": attachment.content_hash,
            },
        )
    raise ApiError(422, "gmail_action_unsupported", "Gmail action is unsupported.")


def _execute_attachment_pair(
    session: Session,
    *,
    record: GmailMessageRecord,
    action: _PlannedAction,
    gmail_provider: FakeGmailActionProvider,
    drive_provider: FakeDriveProvider,
    policy: GmailLowRiskActionPolicy,
    idempotency_key_prefix: str,
    drive_connection_id: str | None,
    actor_id: str,
    correlation_id: str | None,
) -> tuple[list[GmailActionOperation], int, int]:
    operations: list[GmailActionOperation] = []
    denied_count = 0
    replayed_count = 0
    try:
        retrieval_operation, retrieval_replayed = _execute_action(
            session,
            record=record,
            action=action,
            gmail_provider=gmail_provider,
            drive_provider=drive_provider,
            policy=policy,
            idempotency_key_prefix=idempotency_key_prefix,
            drive_connection_id=drive_connection_id,
            actor_id=actor_id,
            correlation_id=correlation_id,
        )
        operations.append(retrieval_operation)
        replayed_count += int(retrieval_replayed)
        if retrieval_operation.status != "succeeded":
            return operations, denied_count, replayed_count
        attachment = _attachment_from_operation(retrieval_operation)
        save_operation, save_replayed = _execute_drive_save_action(
            session,
            record=record,
            attachment=attachment,
            drive_provider=drive_provider,
            policy=policy,
            idempotency_key_prefix=idempotency_key_prefix,
            drive_connection_id=drive_connection_id,
            actor_id=actor_id,
            correlation_id=correlation_id,
        )
        operations.append(save_operation)
        replayed_count += int(save_replayed)
    except ApiError as exc:
        denied_count += int(exc.status_code < 500)
        operations.append(
            _record_denied_operation(
                session,
                record=record,
                operation_type="drive.save_attachment",
                idempotency_key=f"{idempotency_key_prefix}:drive-save-denied",
                reason_code=exc.code,
                actor_id=actor_id,
                correlation_id=correlation_id,
                provider_attachment_reference=action.provider_attachment_reference,
                target_reference=policy.drive_folder_reference,
            )
        )
    return operations, denied_count, replayed_count


def _execute_drive_save_action(
    session: Session,
    *,
    record: GmailMessageRecord,
    attachment: FakeRetrievedAttachment,
    drive_provider: FakeDriveProvider,
    policy: GmailLowRiskActionPolicy,
    idempotency_key_prefix: str,
    drive_connection_id: str | None,
    actor_id: str,
    correlation_id: str | None,
) -> tuple[GmailActionOperation, bool]:
    if policy.drive_folder_reference is None:
        raise ApiError(
            422,
            "drive_folder_required",
            "Drive folder reference is required.",
        )
    action = _PlannedAction(
        "drive.save_attachment",
        target_reference=policy.drive_folder_reference,
        provider_attachment_reference=attachment.provider_attachment_reference,
    )
    idempotency_key = action.idempotency_key(idempotency_key_prefix)
    idem = begin_idempotent_operation(
        session,
        actor_id=actor_id,
        operation=action.operation_type,
        idempotency_key=idempotency_key,
        payload={
            "gmail_message_record_id": record.gmail_message_record_id,
            "operation_type": action.operation_type,
            "target_reference": action.target_reference,
            "provider_attachment_reference": action.provider_attachment_reference,
        },
        resource_type="gmail_action_operation",
    )
    if idem.replayed and idem.record.resource_id is not None:
        operation = session.get(GmailActionOperation, idem.record.resource_id)
        if operation is None:
            raise ApiError(
                409,
                "gmail_action_idempotency_record_missing",
                "Gmail action idempotency record is missing.",
            )
        return operation, True
    _authorize_drive_save(
        session,
        owner_user_id=record.owner_user_id,
        drive_connection_id=drive_connection_id,
        actor_id=actor_id,
        correlation_id=correlation_id,
    )
    try:
        provider_reference = drive_provider.save_attachment(
            folder_reference=policy.drive_folder_reference,
            attachment=attachment,
        )
    except ProviderOperationError as exc:
        operation = _create_action_operation(
            session,
            record=record,
            operation_type=action.operation_type,
            status="failed",
            idempotency_key=idempotency_key,
            drive_connection_id=drive_connection_id,
            provider_attachment_reference=attachment.provider_attachment_reference,
            target_reference=policy.drive_folder_reference,
            reason_code=exc.code,
            metadata_json={"outcome": "provider_failed"},
        )
        complete_idempotent_operation(
            idem.record,
            resource_id=operation.gmail_action_operation_id,
        )
        _audit_action(
            session,
            operation,
            actor_id=actor_id,
            result="failed",
            correlation_id=correlation_id,
        )
        return operation, False
    operation = _create_action_operation(
        session,
        record=record,
        operation_type=action.operation_type,
        status="succeeded",
        idempotency_key=idempotency_key,
        drive_connection_id=drive_connection_id,
        provider_operation_reference=provider_reference,
        provider_attachment_reference=attachment.provider_attachment_reference,
        target_reference=policy.drive_folder_reference,
        metadata_json={
            "drive_file_reference": provider_reference,
            "attachment_size_bytes": attachment.size_bytes,
            "attachment_content_hash": attachment.content_hash,
        },
    )
    complete_idempotent_operation(
        idem.record,
        resource_id=operation.gmail_action_operation_id,
    )
    _audit_action(
        session,
        operation,
        actor_id=actor_id,
        result="succeeded",
        correlation_id=correlation_id,
    )
    return operation, False


def _attachment_from_operation(
    operation: GmailActionOperation,
) -> FakeRetrievedAttachment:
    if operation.provider_attachment_reference is None:
        raise ApiError(
            409,
            "gmail_attachment_operation_invalid",
            "Gmail attachment operation is invalid.",
        )
    return FakeRetrievedAttachment(
        provider_attachment_reference=operation.provider_attachment_reference,
        filename=str(operation.metadata_json.get("filename", "")),
        mime_type=str(operation.metadata_json.get("mime_type", "")),
        size_bytes=int(operation.metadata_json.get("attachment_size_bytes", 0)),
        content_hash=str(operation.metadata_json.get("attachment_content_hash", "")),
    )


def _retrieve_attachment(
    record: GmailMessageRecord,
    action: _PlannedAction,
    gmail_provider: FakeGmailActionProvider,
) -> FakeRetrievedAttachment:
    if (
        action.attachment_payload is None
        or action.provider_attachment_reference is None
    ):
        raise ApiError(
            422,
            "gmail_attachment_reference_invalid",
            "Attachment reference is invalid.",
        )
    return gmail_provider.get_attachment(
        record.provider_message_reference,
        action.provider_attachment_reference,
        filename=str(action.attachment_payload.get("filename", "")),
        mime_type=str(action.attachment_payload.get("mime_type", "")),
        size_bytes=int(action.attachment_payload.get("size_bytes", 0)),
    )


def _authorize_drive_save(
    session: Session,
    *,
    owner_user_id: str,
    drive_connection_id: str | None,
    actor_id: str,
    correlation_id: str | None,
) -> None:
    if drive_connection_id is None:
        raise ApiError(
            422,
            "drive_connection_required",
            "Drive connection is required.",
        )
    drive_connection = get_connection(
        session,
        owner_user_id=owner_user_id,
        connection_id=drive_connection_id,
    )
    if DRIVE_SCOPE_FILE not in drive_connection.granted_scopes:
        raise ApiError(403, "connector_scope_missing", "Connector scope is missing.")
    authorization = authorize_connector_operation(
        session,
        owner_user_id=owner_user_id,
        connection_id=drive_connection_id,
        operation_id="drive.save_attachment",
        actor_id=actor_id,
        correlation_id=correlation_id,
    )
    if not authorization.allowed:
        raise ApiError(403, authorization.reason_code, "Connector operation denied.")


def _record_denied_operation(
    session: Session,
    *,
    record: GmailMessageRecord,
    operation_type: str,
    idempotency_key: str,
    reason_code: str,
    actor_id: str,
    correlation_id: str | None,
    provider_attachment_reference: str | None = None,
    target_reference: str | None = None,
) -> GmailActionOperation:
    operation = _create_action_operation(
        session,
        record=record,
        operation_type=operation_type,
        status="denied",
        idempotency_key=idempotency_key,
        provider_attachment_reference=provider_attachment_reference,
        target_reference=target_reference,
        reason_code=reason_code,
        metadata_json={"outcome": "denied"},
    )
    _audit_action(
        session,
        operation,
        actor_id=actor_id,
        result="denied",
        correlation_id=correlation_id,
    )
    return operation


def _create_action_operation(
    session: Session,
    *,
    record: GmailMessageRecord,
    operation_type: str,
    status: str,
    idempotency_key: str,
    drive_connection_id: str | None = None,
    provider_operation_reference: str | None = None,
    provider_attachment_reference: str | None = None,
    target_reference: str | None = None,
    reason_code: str | None = None,
    metadata_json: dict[str, Any] | None = None,
) -> GmailActionOperation:
    operation = GmailActionOperation(
        owner_user_id=record.owner_user_id,
        gmail_message_record_id=record.gmail_message_record_id,
        connection_id=record.connection_id,
        drive_connection_id=drive_connection_id,
        operation_type=operation_type,
        status=status,
        idempotency_key=_safe_reference(idempotency_key, limit=128),
        provider_operation_reference=provider_operation_reference,
        provider_message_reference=record.provider_message_reference,
        provider_attachment_reference=provider_attachment_reference,
        target_reference=target_reference,
        reason_code=reason_code,
        metadata_json=metadata_json or {},
    )
    session.add(operation)
    session.flush()
    return operation


def _audit_action(
    session: Session,
    operation: GmailActionOperation,
    *,
    actor_id: str,
    result: str,
    correlation_id: str | None,
) -> None:
    record_audit_event(
        session,
        AuditEventInput(
            event_type="gmail.low_risk_action",
            actor_type="service",
            actor_id=actor_id,
            channel="service",
            action="execute_low_risk_action",
            resource_type="gmail_action_operation",
            resource_id=operation.gmail_action_operation_id,
            result=result,
            reason_code=operation.reason_code,
            correlation_id=correlation_id,
            metadata={
                "operation_id": operation.operation_type,
                "resource_id": operation.gmail_action_operation_id,
                "resource_type": "gmail_action_operation",
                "outcome": operation.status,
            },
        ),
    )


def _load_message_record(
    session: Session,
    *,
    owner_user_id: str,
    gmail_message_record_id: str,
) -> GmailMessageRecord:
    record = session.get(GmailMessageRecord, gmail_message_record_id)
    if record is None or record.owner_user_id != owner_user_id:
        raise ApiError(404, "gmail_message_record_not_found", "Message was not found.")
    return record


def _validate_idempotency_prefix(value: str) -> None:
    if len(value) < 8 or len(value) > 80 or any(char.isspace() for char in value):
        raise ApiError(
            422,
            "gmail_action_idempotency_key_invalid",
            "Gmail action idempotency prefix is invalid.",
        )


def _provider_operation_reference(*values: str) -> str:
    return "fake:" + _hash_text(":".join(values))[:32]


def _safe_reference(value: str, *, limit: int = MAX_REFERENCE_LENGTH) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
