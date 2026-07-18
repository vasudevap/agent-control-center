# Work Order 039: Low-Risk Mailbox Actions and Attachment Saving

**Status:** Implemented - Pending PR Review
**Work Order ID:** WO-039
**Type:** Backend connector side-effect behavior
**Implementation Authorization:** Granted under ADP-003 on 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing Plan:** [Phase 6 Work Order Backlog](../implementation-plans/phase-6-work-order-backlog.md)
**Prerequisites:** WO-036, WO-037, and WO-038 completed and merged
**Review Record:** [WO-039 Implementation Report](../reviews/WO-039-low-risk-mailbox-actions-and-attachment-saving-implementation-report.md)

## 1. Purpose

Implement approved low-risk Gmail and Drive side effects through idempotent
connector operations after message eligibility, classification, policy, and
suppression checks pass.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Low-risk actions | Apply labels, archive approved categories, save approved attachments |
| Drive scope | Use `https://www.googleapis.com/auth/drive.file` only |
| Idempotency | Required for every side-effecting operation |
| Approval boundary | No high-risk action is implemented here |
| Suppressed sources | Never eligible for low-risk actions |

## 3. Approved Scope if Accepted

- Gmail label application through the connector.
- Archive behavior for explicitly configured low-risk categories.
- Attachment retrieval and Drive save for approved attachment policies.
- Idempotency records for labels, archive, attachment retrieval, and Drive save.
- Provider outcome normalization, retry handling, and audit events.
- Denied-action records when policy, connector, or suppression gates fail.

## 4. Explicitly Out of Scope

Email send, delete, forward, unsubscribe, external sharing, broad Drive
permission changes, unrestricted attachment copies, live provider calls,
knowledge behavior, drafting, approval creation, and dashboard productization
are excluded.

## 5. Verification and Completion

Require fake Gmail and Drive provider tests for label/archive/save idempotency,
duplicate retry behavior, policy denial, suppression denial, normalized
provider failures, minimized audit metadata, no token/content leakage, `ruff`,
`mypy`, and CI.

## 6. Rollback Expectations

Rollback must preserve idempotency records and provider outcome references so a
retried run does not duplicate side effects. If schema changes are introduced,
document downgrade behavior for operation outcome records.

## 7. Stop-and-Ask Triggers

Stop before implementing delete, forward, unsubscribe, external sharing,
automatic send, live provider calls, broader Drive scopes, action on suppressed
sources, or non-idempotent side effects.
