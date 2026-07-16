# Work Order 012: Connectors, Policies, and Settings Frontend Prototype

**Status:** Implementation Review — Merge Pending
**Work Order ID:** WO-012
**Type:** Frontend prototype
**Owner:** Product owner
**Review owner:** Frontend implementation
**Authorization date:** 2026-07-16
**Review authority:** [WO-012 authorization review](../reviews/WO-012-governance-settings-frontend-prototype-review.md)
**Implementation review:** [WO-012 implementation report](../reviews/WO-012-governance-settings-implementation-report.md)

## Purpose

Replace the Connectors, Policies, and Settings placeholders with truthful
local-fixture prototype surfaces that express Atlas governance boundaries
without implying live OAuth, credentials, policy enforcement, authorization,
storage, or configuration persistence.

## Approved scope

- `/connectors`: connector inventory, declared capabilities/scopes, fictional
  health and account metadata, local filters, and explicit connection/reconnect/
  health-check/revoke simulations.
- `/policies`: policy inventory, type, version, status, scope, agent assignment,
  and explicit local enable/disable simulation. Policy definitions are readable
  summaries; no evaluation occurs.
- `/settings`: workspace, appearance, notification, scheduling, and retention
  preference forms whose save/reset actions are explicit session-only
  simulations.
- Typed fictional fixtures, focused tests, dialogs where confirmation matters,
  and durable visual evidence.

## Explicit exclusions and safety boundary

- No OAuth flow, provider SDK, token or credential handling, APIs, `fetch`,
  server actions, storage, browser persistence, authentication, authorization,
  policy engine, notification delivery, or external mutation.
- Secret fields and real credentials are prohibited. Scope displays are
  fictional descriptors only.
- Every action with a mutating appearance begins with `Simulate` or is contained
  in a persistent `Session-only simulation` context. Result messages must also
  use `Simulated` and refresh must restore fixtures.
- Policy state never claims enforcement. Settings never claim they were saved.

## UX, acceptance, and verification

- Reuse Atlas page, card, table, dialog, status, risk, and control patterns.
- Use `StatusBadge` for connector and policy state; geometric icons remain
  reserved for risk.
- Support themes, all sidebar tiers, keyboard/focus behavior, 320px and
  200%-equivalent reflow, semantic tables, and mobile fallbacks.
- Automated tests cover local simulation boundaries, form reset, confirmation,
  no-persistence wording, filters, and alternate states.
- Browser evidence covers desktop/tablet/mobile, light/dark, important dialogs
  and alternate states, keyboard access, focus, and reflow.
- `npm ci`, typecheck, lint, tests, production build, required CI, governed PR,
  implementation report, and final review must pass before closure.

## File scope

- `apps/web/src/app/(shell)/connectors/**`
- `apps/web/src/app/(shell)/policies/**`
- `apps/web/src/app/(shell)/settings/**`
- Shared status vocabulary only where canonical connector/policy states are missing
- `docs/work-orders/**`, `docs/reviews/**`, `docs/handoff.md`, and `ROADMAP.md`

No architecture change, unrelated refactor, or dependency change is authorized.
