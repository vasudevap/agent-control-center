# Work Order 065: Agent Visibility Schema and Migration Foundation

**Status:** Completed - Merged
**Work Order ID:** WO-065
**Type:** Agent Visibility MVP persistence foundation
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-24
**Engineering Specification:** [ES-009](../engineering-specifications/ES-009-agent-visibility-and-lifecycle-mvp.md)
**Governing ADP:** [ADP-006](../implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md)
**Prerequisites:** WO-064 completed and merged
**Review Record:** [WO-065 Implementation Report](../reviews/WO-065-agent-visibility-schema-and-migration-foundation-implementation-report.md)

## 1. Purpose

Create the normalized database foundation required by ES-009 without dropping
or rewriting historical execution-platform evidence.

## 2. Approved Scope if Accepted

- Add forward migration `0018_agent_visibility_lifecycle_mvp`.
- Extend `agent_registrations` with ES-009 lifecycle, owner, monitoring, and
  projection columns.
- Backfill existing rows as `legacy_descriptor` or `synthetic_smoke` and hide
  them from active default projections.
- Create `agent_credentials`, `agent_heartbeats`, `agent_executions`,
  `agent_health_evaluator_leases`, `agent_alerts`,
  `agent_activity_events`, and `agent_ingestion_rate_limits`.
- Add SQLAlchemy models, constraints, indexes, and bounded enum validation.
- Add migration upgrade/downgrade tests against PostgreSQL.

## 3. Expected File Scope

- `apps/api/alembic/versions/0018_agent_visibility_lifecycle_mvp.py`
- `apps/api/src/atlas_api/models/agent.py`
- new or updated API model modules under `apps/api/src/atlas_api/models/`
- `apps/api/src/atlas_api/models/__init__.py`
- `apps/api/tests/**`
- documentation updates only where needed for migration evidence

## 4. Explicitly Out of Scope

Owner enrollment routes, plaintext credential issuance, telemetry endpoints,
evaluator execution, dashboard rewrites, provider writes, production
migration execution, and destructive legacy table removal are out of scope.

## 5. Acceptance Criteria

- Alembic upgrade from head creates all ES-009 schema objects.
- Alembic downgrade returns to the prior head locally.
- Historical rows are preserved and excluded from active default projections.
- Required indexes and uniqueness constraints match ES-009 section 6.
- New models have focused tests for defaults, constraints, and synthetic
  exclusion.

## 6. Verification

```bash
python -m mypy apps/api/src
python -m ruff check apps/api
python -m pytest apps/api
cd apps/api
ATLAS_API_DATABASE_URL="$ATLAS_API_DATABASE_URL" python -m alembic upgrade head
ATLAS_API_DATABASE_URL="$ATLAS_API_DATABASE_URL" python -m alembic downgrade base
git diff --check
```

## 7. Rollback Expectations

Rollback defaults to source rollback before hosted deployment. After hosted
migration, rollback defaults to forward repair unless a reviewed runbook
authorizes downgrade. No rollback may require dropping historical tables.

## 8. Stop-and-Ask Triggers

Stop before destructive legacy data removal, hosted production migration,
changing database provider/topology, weakening audit retention, or adding a
new persistence framework.
