# Work Order 037: Gmail Message Eligibility, Retrieval, and Classification

**Status:** Completed - Merged
**Work Order ID:** WO-037
**Type:** Backend Gmail agent behavior
**Implementation Authorization:** Granted under ADP-003 on 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing Plan:** [Phase 6 Work Order Backlog](../implementation-plans/phase-6-work-order-backlog.md)
**Prerequisites:** WO-036 completed and merged
**Review Record:** [WO-037 Implementation Report](../reviews/WO-037-gmail-message-eligibility-retrieval-and-classification-implementation-report.md)

## 1. Purpose

Retrieve only eligible Gmail messages through the connector boundary, normalize
minimum necessary message data, classify messages, and preserve provider
references and integrity identities for later governed actions.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Mailbox access | Eligible-message retrieval only; no unrestricted mailbox scan |
| Message persistence | Store references, selected metadata, classification, and hashes; avoid full body persistence |
| Classification output | Strict schema validation before use |
| Uncertainty | Fail closed to `Review Required` or manual handling |
| Downstream actions | No draft, send, approval, question, or learning in this Work Order |

## 3. Approved Scope if Accepted

- Eligibility configuration and query construction for controlled inbox
  subsets.
- Message metadata, selected content, thread metadata, attachment metadata, and
  provider reference normalization.
- Classification into ES-006 MVP categories.
- Confidence thresholds and uncertain-output handling.
- Provider error, rate-limit, pagination, and retry normalization.
- Audit events for retrieval, classification, denied retrieval, and fail-closed
  classification.

## 4. Explicitly Out of Scope

Clinical/PHI suppression enforcement beyond classification output, low-risk
mailbox actions, Drive attachment saving, knowledge retrieval, question
creation, draft generation, approval creation, send continuation, history
learning, live Gmail calls, and dashboard productization are excluded.

## 5. Verification and Completion

Require fake-provider tests for eligibility filters, pagination, minimized
message normalization, provider references, classification schema validation,
uncertainty fallback, provider error normalization, redaction, audit events,
`ruff`, `mypy`, and CI.

## 6. Rollback Expectations

If retrieval/classification schema changes are introduced, rollback must leave
existing run, audit, and provider-reference records readable or provide an
accepted migration rollback note.

## 7. Stop-and-Ask Triggers

Stop before implementing unrestricted mailbox scans, storing full message
bodies, using live Gmail, using unvalidated model output, bypassing connector
runtime, or allowing classification uncertainty to continue into draft/action
flows.
