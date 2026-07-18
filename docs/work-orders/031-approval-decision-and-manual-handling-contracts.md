# Work Order 031: Approval Decision and Manual-Handling Contracts

**Status:** Completed - Merged
**Work Order ID:** WO-031
**Type:** Backend approval contract
**Implementation Authorization:** Granted under ADP-002 on 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing Plan:** [Phase 5 Work Order Backlog](../implementation-plans/phase-5-work-order-backlog.md)
**Architecture Authority:** [ADR-002](../decisions/ADR-002-human-approvals-decision-integrity.md), [ADR-003](../decisions/ADR-003-governed-external-approval-decision-channel.md), [ADR-004](../decisions/ADR-004-governed-external-product-client-contract.md)
**Prerequisite:** ES-005 accepted; Phase 3 backend foundation complete
**Review Record:** [WO-031 Implementation Report](../reviews/WO-031-approval-decision-and-manual-handling-contracts-implementation-report.md)

## 1. Purpose

Implement generic approval queue, evidence read, approve/reject,
edit-then-approve, and manual-handling contracts for internal and external
decision channels.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| System of record | Atlas Approval Service remains authoritative |
| Channels | Internal and External use the same lifecycle and audit rules |
| Edit-then-approve | Supersedes the original request and approves exact edited content in one governed workflow |
| Manual handling | Suppressed items are not approvals and cannot authorize action |
| Gmail | No draft or send execution |

## 3. Approved Scope if Accepted

- Approval request persistence or hardening needed for generic contracts.
- Pending approval queue and evidence read APIs.
- Approve/reject decision submission with expiry, concurrency, exact-content
  binding, idempotency, channel provenance, and audit.
- Edit-then-approve supersession workflow.
- Manual-handling records, reads, and minimized event enqueue points.
- Authorization and OpenAPI contract tests.

## 4. Explicitly Out of Scope

Gmail drafting, Gmail sending, connector action execution, LLM generation,
multi-reviewer behavior, approval delegation, frontend productization, and live
external webhook delivery are excluded.

## 5. Verification and Completion

Require API contract tests, state transition tests, idempotency/concurrency
tests, expiry tests, authorization negative tests, audit tests, webhook
fake-transport tests, `ruff`, `mypy`, repository formatting checks,
implementation report, CI, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before adding reviewers, roles, delegation, provider execution, sending
behavior, fail-open decisions, unaudited material state changes, or manual
handling that can create an approval bypass.
