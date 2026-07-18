from __future__ import annotations

from collections.abc import Mapping

WEBHOOK_EVENT_APPROVAL_PENDING = "approval.pending"
WEBHOOK_EVENT_APPROVAL_DECIDED = "approval.decided"
WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING = (
    "message.held_for_manual_handling"
)
WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING = "knowledge.question.pending"
WEBHOOK_EVENT_KNOWLEDGE_QUESTION_ANSWERED = "knowledge.question.answered"
WEBHOOK_EVENT_KNOWLEDGE_FACT_RECONFIRMATION_REQUIRED = (
    "knowledge.fact.reconfirmation_required"
)
WEBHOOK_EVENT_RUN_STATE_CHANGED = "run.state_changed"

PHASE5_WEBHOOK_EVENT_TYPES = frozenset(
    {
        WEBHOOK_EVENT_APPROVAL_PENDING,
        WEBHOOK_EVENT_APPROVAL_DECIDED,
        WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING,
        WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING,
        WEBHOOK_EVENT_KNOWLEDGE_QUESTION_ANSWERED,
        WEBHOOK_EVENT_KNOWLEDGE_FACT_RECONFIRMATION_REQUIRED,
        WEBHOOK_EVENT_RUN_STATE_CHANGED,
    }
)

LEGACY_WEBHOOK_EVENT_TYPES = frozenset({"send.outcome", "message.held"})

ALLOWED_WEBHOOK_EVENT_TYPES = PHASE5_WEBHOOK_EVENT_TYPES | LEGACY_WEBHOOK_EVENT_TYPES

ALLOWED_WEBHOOK_PAYLOAD_KEYS = frozenset(
    {
        "decision_channel",
        "deduplication_key",
        "fact_key",
        "reason_category",
        "reconciliation_url",
        "reconciliation_path",
        "resource_id",
        "resource_type",
        "revision_id",
        "sensitivity_classification",
        "status",
        "trigger_source",
    }
)

PHASE5_WEBHOOK_PAYLOAD_SCHEMAS: Mapping[str, frozenset[str]] = {
    WEBHOOK_EVENT_APPROVAL_PENDING: frozenset(
        {"resource_id", "resource_type", "status", "reconciliation_path"}
    ),
    WEBHOOK_EVENT_APPROVAL_DECIDED: frozenset(
        {
            "decision_channel",
            "resource_id",
            "resource_type",
            "status",
            "reconciliation_path",
        }
    ),
    WEBHOOK_EVENT_MESSAGE_HELD_FOR_MANUAL_HANDLING: frozenset(
        {
            "reason_category",
            "resource_id",
            "resource_type",
            "sensitivity_classification",
            "status",
            "reconciliation_path",
        }
    ),
    WEBHOOK_EVENT_KNOWLEDGE_QUESTION_PENDING: frozenset(
        {"fact_key", "resource_id", "resource_type", "status", "reconciliation_path"}
    ),
    WEBHOOK_EVENT_KNOWLEDGE_QUESTION_ANSWERED: frozenset(
        {
            "fact_key",
            "resource_id",
            "resource_type",
            "revision_id",
            "status",
            "reconciliation_path",
        }
    ),
    WEBHOOK_EVENT_KNOWLEDGE_FACT_RECONFIRMATION_REQUIRED: frozenset(
        {
            "fact_key",
            "reason_category",
            "resource_id",
            "resource_type",
            "status",
            "reconciliation_path",
        }
    ),
    WEBHOOK_EVENT_RUN_STATE_CHANGED: frozenset(
        {
            "resource_id",
            "resource_type",
            "status",
            "trigger_source",
            "reconciliation_path",
        }
    ),
}

DENIED_WEBHOOK_PAYLOAD_KEY_PARTS = (
    "authorization",
    "body",
    "content",
    "cookie",
    "credential",
    "message",
    "password",
    "secret",
    "signature",
    "text",
    "token",
)
