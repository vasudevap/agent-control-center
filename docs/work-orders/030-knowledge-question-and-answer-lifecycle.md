# Work Order 030: Knowledge Question and Answer Lifecycle

**Status:** Proposed - Governance Review Required
**Work Order ID:** WO-030
**Type:** Backend governance contract
**Implementation Authorization:** Not Granted
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing Plan:** [Phase 5 Work Order Backlog](../implementation-plans/phase-5-work-order-backlog.md)
**Architecture Authority:** [ADR-005](../decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md), [Human Approvals Architecture](../architecture/13-human-approvals.md)
**Prerequisite:** [WO-029](./029-governed-knowledge-fact-contracts.md)
**Review Record:** TBD

## 1. Purpose

Implement first-class knowledge question and answer records so Atlas can ask
instead of guess without confusing knowledge acquisition with approval.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Authority | Questions and answers are not approvals and do not authorize actions |
| Lifecycle | Explicit question states and answer validation before fact mutation |
| Provenance | Answers are untrusted human input until validated and persisted |
| Events | Webhook notifications are non-authoritative |
| Gmail | No Gmail drafting or message eligibility behavior |

## 3. Approved Scope if Accepted

- Question create/read/list/cancel contracts.
- Answer submission, validation, answer-to-fact creation/update pathway, and
  duplicate handling.
- Lifecycle states, timeout/cancellation metadata where needed, authorization,
  audit, and OpenAPI contracts.
- Webhook enqueue points for pending and answered question events using fake
  delivery tests only.

## 4. Explicitly Out of Scope

Approval clarification, approval decisions, Gmail ask behavior, LLM extraction,
live provider data, frontend productization, and production notification
delivery are excluded.

## 5. Verification and Completion

Require lifecycle tests, fact mutation integration tests, authorization
negative tests, webhook fake-transport tests, audit tests, `ruff`, `mypy`,
repository formatting checks, implementation report, CI, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before treating answers as approvals, reusing approval clarification,
persisting prohibited answer values, creating Gmail-specific fields, or sending
live notifications.
