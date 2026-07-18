# Work Order 034: Phase 5 Dashboard Contract Compatibility Pass

**Status:** Accepted - Ready After Stable API Schemas
**Work Order ID:** WO-034
**Type:** Frontend/backend contract alignment
**Implementation Authorization:** Granted under ADP-002 on 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing Plan:** [Phase 5 Work Order Backlog](../implementation-plans/phase-5-work-order-backlog.md)
**Architecture Authority:** [Component Architecture](../architecture/05-component-architecture.md), [API Contract Foundation](./021-api-contract-foundation.md)
**Prerequisites:** [WO-027](./027-agent-registry-and-runtime-contracts.md), [WO-028](./028-run-lifecycle-and-job-intake-contracts.md), [WO-029](./029-governed-knowledge-fact-contracts.md), [WO-031](./031-approval-decision-and-manual-handling-contracts.md)
**Review Record:** TBD

## 1. Purpose

Align existing dashboard assumptions with the stable Phase 5 backend contracts
without claiming full Phase 4 dashboard productization complete.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Goal | Contract compatibility, not full productization |
| Fixtures | Fixture-only assumptions that conflict with backend contracts are replaced or explicitly marked |
| UI scope | Minimal contract-aware client stubs, types, or tests only |
| Design | No major visual redesign under this Work Order |
| Deployment | No production dashboard release authority |

## 3. Approved Scope if Accepted

- Map existing dashboard surfaces to Phase 5 API schemas for agents, runs,
  approvals, manual handling, audit, and knowledge.
- Add or update typed API client contracts, test fixtures, or compatibility
  tests where useful.
- Mark deferred Phase 4 productization gaps clearly.
- Preserve existing design language and frontend test approach.

## 4. Explicitly Out of Scope

Full dashboard productization, broad UI redesign, production deployment,
live backend integration, Gmail-specific UI, and new operator workflows outside
contract compatibility are excluded.

## 5. Verification and Completion

Require frontend type/test checks relevant to touched files, backend contract
compatibility evidence where applicable, documentation updates, implementation
report, CI, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before changing approved product design, claiming MVP operability,
introducing Gmail-specific UI, or requiring live backend/provider credentials.
