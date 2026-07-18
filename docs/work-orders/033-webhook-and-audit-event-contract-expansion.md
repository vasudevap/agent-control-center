# Work Order 033: Webhook and Audit Event Contract Expansion

**Status:** Implemented Locally - Pending PR, CI, and Merge
**Work Order ID:** WO-033
**Type:** Backend event contract
**Implementation Authorization:** Granted under ADP-002 on 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing Plan:** [Phase 5 Work Order Backlog](../implementation-plans/phase-5-work-order-backlog.md)
**Architecture Authority:** [ADR-003](../decisions/ADR-003-governed-external-approval-decision-channel.md), [ADR-004](../decisions/ADR-004-governed-external-product-client-contract.md), [Observability Architecture](../architecture/11-observability.md)
**Prerequisites:** [WO-029](./029-governed-knowledge-fact-contracts.md), [WO-030](./030-knowledge-question-and-answer-lifecycle.md), [WO-031](./031-approval-decision-and-manual-handling-contracts.md)
**Review Record:** [WO-033 Implementation Report](../reviews/WO-033-webhook-and-audit-event-contract-expansion-implementation-report.md)

## 1. Purpose

Expand webhook and audit contracts for Phase 5 approval, manual-handling,
knowledge, and run events using the existing Phase 3 delivery and audit
foundations.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Webhook authority | Notifications only; consumers reconcile authoritative state through API |
| Payloads | Minimum necessary, signed, no secrets, no full message content |
| Delivery | Existing fake transport and delivery persistence for tests |
| Audit | Durable audit remains separate from logs |
| Live delivery | Not authorized |

## 3. Approved Scope if Accepted

- Event type registry and payload schemas for Phase 5 events.
- Webhook enqueue points for approval pending/decided, manual handling,
  question pending/answered, fact reconfirmation required, and run state events
  where needed.
- Durable audit action names and metadata contracts.
- Fake-transport tests for signing, minimization, correlation, and
  deduplication identity.

## 4. Explicitly Out of Scope

Live external HTTP delivery, receiver implementation, external reconciliation
client, production alerting, hosted telemetry, and provider-specific events are
excluded.

## 5. Verification and Completion

Require event schema tests, minimized-payload tests, fake-delivery integration
tests, audit tests, redaction tests, `ruff`, `mypy`, repository formatting
checks, implementation report, CI, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before adding live delivery, exposing sensitive payload values, treating a
webhook as authorization, changing audit failure policy, or adding external
client behavior outside ADR-004.
