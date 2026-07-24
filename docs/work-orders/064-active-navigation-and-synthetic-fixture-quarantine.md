# Work Order 064: Active Navigation and Synthetic Fixture Quarantine

**Status:** Completed - Local Validation Passed
**Work Order ID:** WO-064
**Type:** Agent Visibility MVP active-surface reset
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-24
**Engineering Specification:** [ES-009](../engineering-specifications/ES-009-agent-visibility-and-lifecycle-mvp.md)
**Governing ADP:** [ADP-006](../implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md)
**Prerequisites:** ES-009 accepted
**Review Record:** [WO-064 Implementation Report](../reviews/WO-064-active-navigation-and-synthetic-fixture-quarantine-implementation-report.md)

## 1. Purpose

Reduce Atlas to the active Agent Visibility MVP surface before new runtime
work begins. This Work Order removes dormant execution-platform implications
from normal navigation and quarantines synthetic fixture behavior so future
implementation can prove live product value honestly.

## 2. Approved Scope if Accepted

- Change primary navigation to Overview, Agents, Executions, Alerts, and
  Activity under `/control-center`.
- Preserve `/` as the public Atlas landing page and make `/control-center` the
  canonical active dashboard root.
- Remove Runs, Approvals, Connectors, Policies, Artifacts, Audit, and Settings
  from normal product navigation.
- Remove simulated pause, resume, run, schedule, connector, approval, policy,
  artifact, and tool controls from active routes.
- Quarantine `POST /api/v1/dashboard/smoke-seed` behind
  `ATLAS_API_ENABLE_SYNTHETIC_SMOKE_SEED=false` by default.
- Stop active pages from falling back to local fixture data in production-like
  runtime.
- Preserve dormant route source files and historical evidence unless ES-009
  explicitly authorizes a change.

## 3. Expected File Scope

- `apps/web/src/components/layout/nav-items.ts`
- `apps/web/src/components/layout/sidebar.tsx`
- `apps/web/src/components/layout/mobile-nav-drawer.tsx`
- `apps/web/src/components/layout/status-bar.tsx`
- `apps/web/src/components/layout/top-bar.tsx`
- `apps/web/src/app/page.tsx`
- `apps/web/src/app/(shell)/control-center/**`
- `apps/web/src/features/overview/**`
- `apps/web/src/app/(shell)/**`
- `apps/web/src/lib/dashboard-runtime.ts`
- `apps/api/src/atlas_api/api/dashboard.py`
- `apps/api/src/atlas_api/core/config.py`
- related tests for the touched files

## 4. Explicitly Out of Scope

New agent schema, credential issuance, telemetry ingestion, evaluator logic,
alert persistence, hosted migration, provider configuration, production data
use, deletion of historical migrations, and reactivation of deferred product
capabilities are out of scope.

## 5. Acceptance Criteria

- Primary navigation exposes only Overview, Agents, Executions, Alerts, and
  Activity, all rooted under `/control-center`.
- Root `/` is a public landing page, not the authenticated dashboard shell.
- Active pages do not show controls that imply Atlas can deploy, schedule,
  run, pause, resume, stop, or maintain external agents.
- Synthetic smoke seed is disabled by default and cannot run in normal
  production behavior.
- Active page tests prove fixture fallback is not used as production evidence.
- Dormant routes remain inaccessible from normal navigation.

## 6. Verification

Run focused web and API tests for touched surfaces, then include the relevant
subset of the ES-009 full command set in the implementation report. At minimum:

```bash
npm run typecheck
npm run lint
npm test
python -m ruff check apps/api
python -m pytest apps/api
git diff --check
```

## 7. Rollback Expectations

Rollback may restore the previous source state but must not reactivate
synthetic production fallback as accepted product evidence. If active routing
breaks, disable the affected active page and show a fail-closed error state
until repaired.

## 8. Stop-and-Ask Triggers

Stop before deleting historical route source, weakening owner session or CSRF
checks, using production fixture data as acceptance evidence, reactivating
deferred capabilities, changing provider configuration, or making any
Atlas-to-agent runtime-control call.
