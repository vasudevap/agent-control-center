# WO-064 Active Navigation and Synthetic Fixture Quarantine - Implementation Report

**Status:** Completed - Local Validation Passed
**Date:** 2026-07-24
**Work Order:** [WO-064](../work-orders/064-active-navigation-and-synthetic-fixture-quarantine.md)
**Scope Authorized:** Repository Maintainer accepted ADP-006 and WO-064 through WO-071, and authorized autonomous execution starting with WO-064 on 2026-07-24.

## Summary

WO-064 resets the active dashboard surface to the Agent Visibility MVP boundary
before new ES-009 persistence and telemetry work begins.

Root `/` is now a public Atlas landing page. The active shell begins at
`/control-center` and exposes only Overview, Agents, Executions, Alerts, and
Activity under that route base. Dormant source files for approvals, connectors,
policies, artifacts, settings, and historical audit routes remain in the
repository, but they are no longer linked from normal product navigation.

## Source Changes

- Reduced primary desktop and mobile navigation to the five active MVP
  destinations under `/control-center`.
- Adopted the parallel landing-page change by keeping `/` as the public Atlas
  landing page and making `/control-center` the canonical dashboard root.
- Added canonical active wrapper routes under `/control-center/agents`,
  `/control-center/runs`, `/control-center/alerts`, and
  `/control-center/audit`.
- Redirected legacy active root routes `/agents`, `/runs`, `/alerts`, and
  `/audit` into their `/control-center/...` equivalents.
- Relabeled the run inventory as Executions.
- Relabeled the audit route as Activity in primary navigation.
- Removed active Overview approval and scheduling panels from the MVP landing
  path.
- Removed active Agent Detail pause, resume, and simulated-run controls.
- Removed active Alerts simulated-investigation controls.
- Removed the web runtime helper for dashboard-created manual runs.
- Removed dashboard POST `/api/v1/dashboard/runs` from the dashboard facade.
- Added `ATLAS_API_ENABLE_SYNTHETIC_SMOKE_SEED`, defaulting to `false`.
- Made dashboard `POST /api/v1/dashboard/smoke-seed` return
  `404 dashboard_smoke_seed_disabled` unless the flag is explicitly enabled.
- Updated tests to prove active navigation, read-only execution history,
  absence of simulated controls, and smoke-seed fail-closed behavior.

## Security and Boundary Evidence

- No provider writes, hosted deployment, production migration, credential
  issuance, or live third-party data use occurred.
- No historical migrations, historical route source, or completed review
  evidence was deleted.
- Synthetic smoke seeding now requires an explicit environment flag before the
  existing owner-session, CSRF, and idempotency controls are reachable.
- Active dashboard navigation no longer exposes deferred approvals,
  connectors, policies, artifacts, audit, or settings destinations as primary
  product paths.
- The dashboard facade no longer exposes a POST route for dashboard-created
  manual runs.

## Validation

Commands run from the repository root:

```text
npm test -- --run src/components/layout/sidebar.test.tsx src/features/overview/components/attention-queue.test.tsx 'src/app/(shell)/runs/runs-workspace.test.tsx' 'src/app/(shell)/alerts/alerts-workspace.test.tsx' 'src/app/(shell)/agents/[agentId]/agent-detail-workspace.test.tsx' 'src/app/(shell)/signed-out-workspaces.test.tsx' src/lib/dashboard-runtime.test.ts
apps/api/.venv/bin/python -m pytest apps/api/tests/test_dashboard_facade.py apps/api/tests/test_config.py
npm run typecheck
npm run lint
npm --workspace @atlas/web exec eslint -- <WO-064 touched web files>
apps/api/.venv/bin/python -m ruff check apps/api
npm test
apps/api/.venv/bin/python -m pytest apps/api
git diff --check
rg -n "(sk-[A-Za-z0-9]|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\s*=|refresh_token|access_token)" <WO-064 touched files>
```

Results:

- Focused web tests: 7 files passed, 22 tests passed.
- Focused API tests: 23 passed, 1 existing Starlette/httpx deprecation warning.
- Web typecheck: passed.
- Web lint: passed after adopting the parallel `/` landing page and
  `/control-center` dashboard route base.
- Scoped ESLint for WO-064 touched web files: passed.
- API Ruff: passed.
- Full web tests: 26 files passed, 108 tests passed.
- Full API tests: 170 passed, 1 existing Starlette/httpx deprecation warning.
- `git diff --check`: passed.
- Focused touched-file secret-pattern scan: no secrets found; matches were
  expected negative assertions for `access_token` and `refresh_token` absence
  and CSS class names such as `text-risk-high`.

Initial validation command corrections:

- A first focused web test attempt used repository-root paths after npm had
  entered the `apps/web` workspace, so Vitest found no files.
- A first Python test attempt used `python`, which is not installed in this
  environment; reruns used `apps/api/.venv/bin/python`.
- A parallel change moved root `/` to a public landing page and introduced
  `/control-center` as the active dashboard root. WO-064 was reconciled to
  that route base before final validation.

## Rollback

Rollback may restore the previous source state for the touched dashboard
navigation, page, runtime helper, and dashboard facade files. Rollback must not
promote synthetic fixtures as production evidence. If the active shell needs a
temporary repair, keep deferred routes hidden from normal navigation and keep
synthetic smoke seeding disabled by default.

## Residual Risks

- `/control-center/runs` and `/control-center/audit` remain transitional
  canonical URLs for the active Executions and Activity labels. WO-069 should
  decide whether to introduce `/control-center/executions` and
  `/control-center/activity` after live ES-009 contracts exist.
- Dormant approval, connector, policy, artifact, settings, and historical audit
  pages remain accessible by direct URL. This is intentional preservation under
  WO-064; future removal or archival needs separate accepted authority.
- The non-dashboard API still contains historical run-creation capability from
  prior phases. WO-064 only reset the active dashboard path.
