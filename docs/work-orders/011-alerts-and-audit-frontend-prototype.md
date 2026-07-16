# Work Order 011: Alerts and Audit Frontend Prototype

**Status:** Implementation Review — Merge Pending
**Work Order ID:** WO-011
**Type:** Frontend prototype
**Owner:** Product owner
**Review owner:** Frontend implementation
**Authorization date:** 2026-07-16
**Review authority:** [WO-011 authorization review](../reviews/WO-011-alerts-and-audit-frontend-prototype-review.md)
**Implementation review:** [WO-011 implementation report](../reviews/WO-011-alerts-and-audit-implementation-report.md)

## Purpose

Replace the Alerts and Audit placeholders with local-fixture operational and
governance surfaces. Alerts becomes the canonical destination for Overview
attention items. Audit presents an append-only-looking fictional history while
stating clearly that no audit record is written or persisted.

## Approved scope

- `/alerts`: severity-led local inventory with search, status/severity/source
  filters, true-value sorting, semantic desktop table, mobile cards, details
  disclosure, empty/filtered states, and canonical Overview links.
- `/audit`: local, immutable-looking event history with search, action/result/
  actor/resource filters, true-value sorting, semantic desktop table, mobile
  cards, correlation context, and event-detail disclosure.
- Typed fictional fixtures, focused tests, and durable visual evidence.

## Explicit exclusions and safety boundary

- No alert engine, notifications, APIs, polling, acknowledgement persistence,
  audit writer, audit export, authentication, authorization, or service calls.
- Alert controls may only simulate a local display-state change and must use
  `Simulate` language.
- Audit fixtures never claim operational immutability or system-of-record
  status. The page must distinguish prototype examples from real audit records.
- Audit rows are read-only; no edit or delete affordance is permitted.
- Operational alert evidence and governance audit history remain distinct.

## UX, acceptance, and verification

- Reuse Atlas inventory and detail/disclosure patterns with `PageHeader`, shared
  tables/cards/controls, `StatusBadge`, and `RiskChip` as applicable.
- Preserve severity-first ordering and non-color state semantics.
- Overview alert items navigate only to canonical fixture destinations.
- Support themes, all sidebar tiers, keyboard/focus behavior, 320px and
  200%-equivalent reflow, semantic desktop tables, and mobile cards.
- Automated tests and browser evidence cover representative, empty, filtered,
  detail, simulation, theme, responsive, and reflow states.
- `npm ci`, typecheck, lint, tests, production build, required CI, governed PR,
  implementation report, and final review must pass before closure.

## File scope

- `apps/web/src/app/(shell)/alerts/**`
- `apps/web/src/app/(shell)/audit/**`
- Bounded Overview fixture/link updates
- Shared status vocabulary only where a canonical state is missing
- `docs/work-orders/**`, `docs/reviews/**`, `docs/handoff.md`, and `ROADMAP.md`

No architecture change, unrelated refactor, or dependency change is authorized.
