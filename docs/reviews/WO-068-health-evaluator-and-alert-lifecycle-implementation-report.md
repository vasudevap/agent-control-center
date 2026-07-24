# WO-068 Health Evaluator and Alert Lifecycle Implementation Report

**Work Order:** [WO-068](../work-orders/068-health-evaluator-and-alert-lifecycle.md)
**Status:** Completed - Local Validation Passed
**Implemented:** 2026-07-24
**Commit:** This commit

## Summary

WO-068 implements the ES-009 derived health evaluator and alert lifecycle for
owner-enrolled, externally operated agents.

The implementation:

- adds a disabled-by-default in-process evaluator gated by
  `ATLAS_API_AGENT_HEALTH_EVALUATOR_ENABLED`;
- uses the `agent-health-evaluator` database lease before mutating derived
  health, alerts, or evaluator freshness;
- derives observed health as `never_seen`, `online`, `late`, `offline`,
  `not_monitored`, `disconnected`, or `archived` from accepted telemetry and
  lifecycle state;
- opens, deduplicates, acknowledges, updates, and resolves missed-heartbeat,
  failed-check, repeated-failed-execution, version-mismatch,
  environment-mismatch, and security-ingestion alerts;
- records material first-connection, reported-health transition,
  observed-health transition, terminal execution, telemetry rejection, alert
  open, alert acknowledgement, and alert resolution activity;
- exposes evaluator freshness through `/health/ready` and the owner dashboard
  monitoring facade;
- fixes activity-only enrollment persistence so a `NULL` heartbeat interval
  remains valid instead of being replaced by the ORM default.

## Route-Base Alignment

WO-068 is primarily API-side and preserves the ADP-006 route-base adoption:

- `/` remains the public Atlas landing page;
- `/control-center` remains the canonical authenticated dashboard route base;
- evaluator readiness is exposed as backend health/monitoring data for later
  `/control-center/...` surfaces;
- no root dashboard page, simulated runtime control, or legacy fixture surface
  was reintroduced.

## Scope Alignment

In scope:

- database-leased evaluator execution inside the existing API process;
- safe repeat execution without duplicate active alerts;
- source-condition-based alert lifecycle and acknowledgement semantics;
- evaluator freshness readiness when the evaluator is enabled;
- bounded JSON-safe alert evidence and material activity metadata.

Out of scope and not implemented:

- new Render services, queues, external schedulers, orchestration frameworks,
  outbound notifications, or webhook fan-out;
- frontend alert UI rewrite or live dashboard productization, which remains
  WO-069 scope;
- hosted production configuration, which remains later ADP evidence scope;
- Atlas deployment, scheduling, execution, pause, resume, stop, or maintenance
  of external agent runtimes.

## Validation

Local validation:

```text
/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m ruff check apps/api
All checks passed!

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m mypy apps/api/src
Success: no issues found in 71 source files

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m pytest apps/api
204 passed, 1 existing Starlette/httpx deprecation warning

npm run lint
pass

npm test
108 passed across 26 web test files

npm run build
pass after rerun outside the sandbox because Turbopack attempted to bind a
local process port and the sandbox returned `Operation not permitted`

npm run typecheck
pass

git diff --check
pass

Touched-file secret scan
pass

ATLAS_API_DATABASE_URL=sqlite:////private/tmp/wo068-alembic-smoke.sqlite \
/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m alembic upgrade head
pass

ATLAS_API_DATABASE_URL=sqlite:////private/tmp/wo068-alembic-smoke.sqlite \
/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m alembic downgrade base
pass
```

The CI-equivalent PostgreSQL Alembic command was attempted with
`postgresql+psycopg://atlas_ci:...@localhost:5432/atlas_api_ci`. The sandboxed
attempt was blocked by localhost network permissions, and the escalated
attempt reached localhost but failed with `Connection refused`, indicating no
local PostgreSQL CI database was listening. WO-068 adds no new migration; the
PostgreSQL migration gate remains covered by CI.

Additional focused coverage:

- evaluator repeat-run and alert deduplication;
- lease contention;
- observed-health transitions;
- missed-heartbeat open/resolve;
- failed-check open/resolve;
- repeated-failed-execution open/resolve;
- version and environment mismatch open/resolve;
- acknowledgement not resolving source conditions;
- acknowledged security-ingestion alert quiet-period resolution;
- evaluator freshness readiness;
- activity-only enrollment `NULL` heartbeat interval persistence;
- telemetry rejection security alert/activity persistence.

## Security Notes

- Agent telemetry remains authenticated with per-agent bearer credentials, not
  the external-product-client HMAC secret.
- Rejected secret-pattern and unsupported-contract telemetry records a
  security-ingestion alert and metadata-only activity without storing the
  rejected payload body.
- Alert evidence and activity metadata are normalized to JSON-safe bounded
  projections before persistence.
- The evaluator does not call external providers or agent runtimes.

## Rollback

Set `ATLAS_API_AGENT_HEALTH_EVALUATOR_ENABLED=false` to stop in-process
evaluation. Existing alerts, activity, heartbeats, and execution summaries
remain historical evidence and must not be deleted to simulate rollback.

## Residual Risks

- Live dashboard rendering of alerts, activity, and derived health remains
  WO-069 scope.
- Disconnect, reconnect, archive, credential rotation, and credential closeout
  remain WO-070 scope.
- Hosted reference-agent verification and final ADP closeout remain WO-071
  scope.
