# Work Order 038: Clinical and PHI Suppression Guardrail

**Status:** Implemented - Pending PR Review
**Work Order ID:** WO-038
**Type:** Backend safety and privacy guardrail
**Implementation Authorization:** Granted under ADP-003 on 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing Plan:** [Phase 6 Work Order Backlog](../implementation-plans/phase-6-work-order-backlog.md)
**Prerequisites:** WO-037 contract shape accepted; WO-036 completed and merged
**Review Record:** [WO-038 Implementation Report](../reviews/WO-038-clinical-and-phi-suppression-guardrail-implementation-report.md)

## 1. Purpose

Enforce clinical and protected-health-information suppression before any Gmail
message can produce knowledge retrieval, questions, drafts, approvals, low-risk
actions, sends, or learned facts.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Suppression order | Runs before knowledge, question, draft, approval, action, send, or learning |
| Manual handling | Suppressed messages become minimized manual-handling records |
| Override policy | Human approval cannot override suppression |
| Payload posture | Reason codes and references only; no clinical content or PHI |
| Failure mode | Fail closed to manual handling |

## 3. Approved Scope if Accepted

- Clinical and PHI detector contract with deterministic test fixtures.
- Suppression gate invoked immediately after retrieval/classification and
  before downstream behavior.
- Manual-handling record creation with minimized metadata.
- Webhook and audit event emission with safe reason codes.
- Negative-path enforcement preventing drafts, approvals, questions, actions,
  sends, and learned facts from suppressed sources.

## 4. Explicitly Out of Scope

Medical advice, clinical content processing, PHI persistence, human override of
suppression, drafting, approval continuation, low-risk actions, history
learning, live provider calls, and release authority are excluded.

## 5. Verification and Completion

Require fake-provider and service tests for suppression ordering, detector
schema validation, fail-closed behavior, manual-handling minimization,
webhook/audit redaction, and negative tests proving suppressed sources cannot
enter knowledge, draft, approval, action, send, or learning paths. Run `ruff`,
`mypy`, secret/prohibited-content scan, and CI.

## 6. Rollback Expectations

Rollback must preserve manual-handling records and audit evidence already
created for suppressed items. If detector state changes require a migration,
the Work Order must document how existing suppressed references remain safe.

## 7. Stop-and-Ask Triggers

Stop before retaining clinical content or PHI, exposing suppressed content in
logs/webhooks/audit/API responses, allowing approval override, or implementing
any downstream behavior that can consume suppressed messages.
