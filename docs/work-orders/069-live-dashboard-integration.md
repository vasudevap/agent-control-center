# Work Order 069: Live Dashboard Integration

**Status:** Accepted - Authorized, blocked on WO-068 completion
**Work Order ID:** WO-069
**Type:** Agent Visibility MVP frontend integration
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-24
**Engineering Specification:** [ES-009](../engineering-specifications/ES-009-agent-visibility-and-lifecycle-mvp.md)
**Governing ADP:** [ADP-006](../implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md)
**Prerequisites:** WO-068 accepted and complete
**Review Record:** To be created during implementation

## 1. Purpose

Replace the active dashboard prototype surfaces with live owner-authenticated
Agent Visibility MVP surfaces.

## 2. Approved Scope if Accepted

- Implement live Overview, Agents, Agent Detail, Executions, Alerts, and
  Activity under the canonical `/control-center` route base.
- Implement enrollment UI and one-time credential copy handling.
- Display observed health separately from reported health.
- Display version, build, environment, heartbeat, execution, alert, and
  activity data from live APIs.
- Implement alert acknowledgement UI.
- Remove production fixture fallback from active surfaces.
- Add loading, empty, first-use, error, stale, partial, disconnected,
  archived, mobile, keyboard, focus, and color-independent status coverage.

## 3. Expected File Scope

- `apps/web/src/components/layout/**`
- `apps/web/src/app/page.tsx`
- `apps/web/src/app/(shell)/control-center/**`
- `apps/web/src/app/(shell)/agents/**`
- new `apps/web/src/app/(shell)/executions/**`
- `apps/web/src/app/(shell)/alerts/**`
- new `apps/web/src/app/(shell)/activity/**`
- `apps/web/src/features/overview/**`
- `apps/web/src/lib/dashboard-runtime.ts`
- related web tests and type definitions

## 4. Explicitly Out of Scope

Backend schema changes, new telemetry API behavior, lifecycle closeout actions
not already implemented, provider integrations, dormant route deletion, and
Atlas-directed runtime controls are out of scope.

## 5. Acceptance Criteria

- Active pages use live API clients and do not rely on fixture fallback in
  production-like runtime.
- Active links and redirects keep authenticated app navigation under
  `/control-center`; root `/` remains the public landing page.
- Agent Detail resolves live agent identity and shows ES-009 required states.
- Enrollment displays plaintext credentials once and then removes them from
  read paths.
- Alerts can be acknowledged without claiming source-condition resolution.
- Navigation tests prove dormant destinations are absent.
- Responsive and accessibility tests cover the active workflows.

## 6. Verification

```bash
npm run typecheck
npm run lint
npm test
npm run build
git diff --check
```

## 7. Rollback Expectations

Rollback active frontend source if live integration is misleading or broken.
Do not restore fixture fallback as production acceptance evidence.

## 8. Stop-and-Ask Triggers

Stop before displaying plaintext credentials after issuance, adding simulated
runtime controls, using fixtures as production evidence, exposing dormant
capabilities through navigation, or weakening owner-session failure states.
