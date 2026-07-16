# Work Order 013: Atlas Indicator Consistency Maintenance

**Status:** Implementation Review — Merge Pending
**Work Order ID:** WO-013
**Type:** Frontend maintenance
**Owner:** Product owner
**Review owner:** Frontend implementation
**Authorization date:** 2026-07-16
**Authorization review:** [WO-013 authorization review](../reviews/WO-013-indicator-consistency-authorization-review.md)
**Implementation review:** [WO-013 implementation report](../reviews/WO-013-indicator-consistency-implementation-report.md)

## Purpose

Apply the established Alerts indicator treatment consistently after the final
prototype-route delivery review. Operational status and risk indicators must
be readable inline rather than requiring a separate legend or decoding an
icon-only table column.

## Approved scope

- Add a shared plain risk treatment: geometric icon plus visible label without
  pill chrome.
- Use quiet inline icon-and-text indicators in operational inventories and
  desktop header metadata where Alerts establishes that pattern.
- Keep the compact Overview attention queue as the sole icon-only exception.
- Keep contained pills only where the mobile-card or decision context needs
  stronger state containment.
- Remove superseded Agents and Approvals legends and the redundant Runs and
  Alerts page-title counters.
- Correct true-value sort affordances in Connectors and Policies, and correct
  completed Work Order merge status for the already merged delivery rounds.

## Explicit exclusions

- No route, data model, architecture, API, persistence, authentication,
  connector, policy-evaluation, or runtime behavior change.
- No new visual system, new status vocabulary, or redesign of Overview.
- No changes to the deliberately paused public-site worktree or branch.

## Verification and acceptance

- Shared components own status/risk icon, label, and color semantics.
- Inventory cells retain visible text at desktop and mobile breakpoints.
- The desktop Alerts, Agents, and Approvals patterns are visually consistent;
  mobile cards retain intentional contained status where applicable.
- Added/updated focused tests cover the plain indicator output and sorting.
- `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`, browser
  responsive review, `git diff --check`, required CI, governed PR, and final
  review evidence pass before closure.

## Governing references

- [Atlas design principles](../design-principles.md)
- [Atlas handoff guide](../handoff.md)
- [Branching strategy](../governance/branching-strategy.md)
- [Pull-request and review process](../governance/pull-request-and-review-process.md)

No ADR is required: this is a bounded presentation-system consistency change.
