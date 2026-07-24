# WO-069 Live Dashboard Integration Implementation Report

**Work Order:** [WO-069](../work-orders/069-live-dashboard-integration.md)
**Status:** Completed - Local Validation Passed
**Implemented:** 2026-07-24
**Commit:** This commit

## Summary

WO-069 replaces the active Agent Visibility MVP surfaces with live
owner-authenticated data and mutation paths under `/control-center`.

The implementation:

- adds owner-scoped visibility routes for executions, alerts, alert
  acknowledgement, and material activity;
- updates active Overview, Agents, Agent Detail, Executions, Execution Detail,
  Alerts, and Activity surfaces to consume ES-009 live data;
- adds a live-only agent enrollment panel that displays the one-time credential
  returned by enrollment and does not expose plaintext credentials on read
  paths;
- moves the canonical active activity route to `/control-center/activity` and
  redirects `/control-center/audit` there;
- preserves `/` as the public Atlas landing page and keeps the authenticated
  product shell rooted under `/control-center`;
- removes production fixture fallback from active `/control-center/...`
  surfaces while retaining fixture behavior only for legacy prototype routes;
- changes the global fleet pulse and overview attention queue to count persisted
  alert lifecycle records rather than synthetic monitoring readiness alerts.

## Route-Base Alignment

WO-069 adopts the parallel route change as current authority:

- `/` remains the public Atlas landing page;
- `/control-center` is the canonical authenticated active product shell;
- `/control-center/activity` is the canonical material activity surface;
- `/control-center/audit` redirects to `/control-center/activity`;
- legacy top-level prototype routes continue to redirect into
  `/control-center` where applicable or remain quarantined fixture surfaces
  outside active navigation.

## Backend Visibility Routes

New owner-authenticated API routes:

- `GET /api/v1/executions`
- `GET /api/v1/executions/{execution_id}`
- `GET /api/v1/alerts`
- `GET /api/v1/alerts/{alert_id}`
- `POST /api/v1/alerts/{alert_id}/acknowledge`
- `GET /api/v1/activity`

All reads are scoped to the owner session and active-surface-visible agents.
Alert acknowledgement requires CSRF, records audit evidence, and does not claim
that the source condition was resolved.

## Validation

Local validation:

```text
/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m ruff check apps/api/src/atlas_api/api/agent_visibility.py apps/api/src/atlas_api/core/authorization.py apps/api/src/atlas_api/main.py apps/api/tests/test_agent_visibility_owner_reads.py
All checks passed!

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m mypy apps/api/src
Success: no issues found in 72 source files

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m pytest apps/api/tests/test_agent_visibility_owner_reads.py
2 passed, 1 existing Starlette/httpx deprecation warning

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m ruff check apps/api
All checks passed!

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m pytest apps/api
206 passed, 1 existing Starlette/httpx deprecation warning

npm test --workspace apps/web -- --run src/lib/dashboard-runtime.test.ts 'src/app/(shell)/runs/runs-workspace.test.tsx' 'src/app/(shell)/alerts/alerts-workspace.test.tsx' 'src/app/(shell)/audit/audit-workspace.test.tsx' 'src/app/(shell)/agents/agents-inventory.test.tsx' 'src/app/(shell)/agents/[agentId]/agent-detail-workspace.test.tsx' 'src/app/(shell)/signed-out-workspaces.test.tsx'
22 passed across 7 focused web test files

npm test --workspace apps/web
108 passed across 26 web test files

npm run lint --workspace apps/web
pass

npm run typecheck --workspace apps/web
pass

npm run build --workspace apps/web
pass after rerun outside the sandbox because Turbopack attempted to bind a
local process port and the sandbox returned `Operation not permitted`

git diff --check
pass

Secret-pattern scan
pass after reviewing matches as pre-existing test literals, documentation
examples, and CSS risk-token class names; no WO-069 plaintext credential or
runtime secret was added.
```

## Security Notes

- Owner visibility reads require owner session authorization.
- Alert acknowledgement requires a matching CSRF token.
- Agent enrollment uses the accepted one-time credential issuance API; plaintext
  is displayed only from the mutation response.
- Activity and alert evidence are metadata-only frontend projections.
- Atlas still does not deploy, schedule, execute, pause, resume, stop, or
  maintain external agent runtimes.

## Rollback

Rollback the WO-069 frontend and `agent_visibility` API route additions if live
surface behavior is misleading or broken. Do not restore fixture fallback as
production acceptance evidence for active `/control-center` routes.

## Residual Risks

- Disconnect, reconnect, archive, credential rotation, and credential closeout
  remain WO-070 scope.
- Hosted reference-agent verification and final ADP closeout remain WO-071
  scope.
