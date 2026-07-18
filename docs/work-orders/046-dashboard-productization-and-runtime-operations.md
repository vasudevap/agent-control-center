# Work Order 046: Dashboard Productization and Runtime Operations

**Status:** Proposed - Pending Acceptance
**Work Order ID:** WO-046
**Type:** Frontend and operator workflow readiness
**Implementation Authorization:** Not granted
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)
**Governing Plan:** [Phase 7 Work Order Backlog](../implementation-plans/phase-7-work-order-backlog.md)
**Prerequisites:** WO-043 completed and ES-007 accepted
**Review Record:** TBD

## 1. Purpose

Productize MVP-critical single-owner dashboard workflows against real backend
contracts so the owner can operate the Gmail Agent without fixture-only
behavior on release-critical paths.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Dashboard boundary | MVP-critical operation only |
| Backend contracts | Consume accepted Phase 5 and Phase 6 contracts |
| Product scope | Single-owner personal operation |
| Design posture | Preserve existing design system and accessibility standards |

## 3. Approved Scope if Accepted

- Wire or verify real-contract dashboard behavior for agent status, connector
  state, manual runs, scheduled runs, held messages, questions, drafts,
  approvals, send outcomes, audit, logs, and health.
- Replace, remove, or clearly quarantine fixture-only behavior on MVP-critical
  paths.
- Add loading, empty, error, stale, retry, and unauthorized states where needed.
- Preserve responsive behavior and keyboard/screen-reader accessibility.
- Document any dashboard surface intentionally deferred beyond MVP.

## 4. Explicitly Out of Scope

Broad redesign, multi-user UI, new product modules, new backend contract
semantics, live provider calls, production deployment, and enterprise console
features are excluded.

## 5. Verification and Completion

Require frontend lint/typecheck/build, component or integration tests for
touched workflows, browser evidence for critical desktop and mobile states,
accessibility evidence, backend contract compatibility checks if API calls are
touched, and an implementation report under `docs/reviews/`.

## 6. Rollback Expectations

Rollback must preserve backend contracts and database state. UI rollback may
restore the previous route behavior if release-critical workflows become
unusable, but must not hide broken production contracts behind misleading
fixtures.

## 7. Stop-and-Ask Triggers

Stop before changing accepted backend semantics, expanding to multi-user
operation, weakening approval or suppression visibility, adding broad redesign
scope, or treating fixture-only behavior as MVP-ready.
