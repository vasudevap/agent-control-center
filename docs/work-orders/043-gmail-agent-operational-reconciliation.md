# Work Order 043: Gmail Agent Operational Reconciliation

**Status:** Implemented - Pending PR Review
**Work Order ID:** WO-043
**Type:** Runtime, webhook, audit, and contract compatibility
**Implementation Authorization:** Granted under ADP-003 on 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing Plan:** [Phase 6 Work Order Backlog](../implementation-plans/phase-6-work-order-backlog.md)
**Prerequisites:** WO-039, WO-040, and WO-042 completed and merged
**Review Record:** [WO-043 Implementation Report](../reviews/WO-043-gmail-agent-operational-reconciliation-implementation-report.md)

## 1. Purpose

Wire Gmail Agent behavior into Atlas operational contracts so runs, statuses,
webhooks, audit events, dashboard views, and the external product client can
reconcile Gmail work without bypassing Phase 5 contracts.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Agent registration | Gmail Agent registers through generic agent registry contracts |
| Runs | Manual and scheduled runs use existing run lifecycle and queue contracts |
| Webhooks | Notifications only; API remains authoritative |
| Dashboard | Contract compatibility only unless a separate productization Work Order is accepted |
| Audit | Material Gmail actions and denied actions produce durable audit events |

## 3. Approved Scope if Accepted

- Gmail Agent descriptor, capabilities, required connectors, risk level, and
  configuration schema reference.
- Manual and scheduled run execution packet wiring through the generic runtime.
- Run-step summaries for eligibility, classification, suppression, actions,
  questions, drafts, approvals, continuation, and outcomes.
- Webhook producers for pending approvals, send outcomes, held manual-handling
  items, relevant question/answer events, and run state changes.
- Audit action names and metadata contracts for Gmail-specific behavior.
- Dashboard and external-client contract compatibility notes and fixture updates
  where necessary.

## 4. Explicitly Out of Scope

Broad dashboard productization, live webhook receivers, production deployment,
new audit browsing APIs unless separately accepted, new generic Phase 5
contract semantics, live provider calls, and release authority are excluded.

## 5. Verification and Completion

Require fake-provider run integration tests, run status/state transition tests,
webhook minimized-payload tests, audit event coverage, dashboard contract
fixture checks if frontend files are touched, authorization negative tests,
`ruff`, `mypy`, frontend validation if touched, and CI.

## 6. Rollback Expectations

Rollback must preserve run, webhook, and audit records created by prior Work
Orders. Event schema changes must either remain backwards-readable or include a
documented compatibility note.

## 7. Stop-and-Ask Triggers

Stop before treating webhooks as authorization, adding live webhook delivery,
changing generic Phase 5 semantics, broadening dashboard scope, bypassing run
lifecycle contracts, or using live provider data.
