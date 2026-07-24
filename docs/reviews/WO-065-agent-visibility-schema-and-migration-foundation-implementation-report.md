# WO-065 Agent Visibility Schema and Migration Foundation Implementation Report

**Work Order:** [WO-065](../work-orders/065-agent-visibility-schema-and-migration-foundation.md)
**Status:** Completed - Local Validation Passed
**Implemented:** 2026-07-24
**Commit:** This commit

## Summary

WO-065 adds the ES-009 persistence foundation without deleting or rewriting
historical execution-platform evidence.

The implementation:

- adds forward Alembic migration `0018_agent_visibility_lifecycle_mvp`;
- extends `agent_registrations` with lifecycle, owner, monitoring, visibility,
  health projection, and metadata columns;
- backfills existing rows as hidden `legacy_descriptor` records, except hosted
  smoke evidence rows marked as `synthetic_smoke`;
- creates normalized ES-009 tables for credentials, heartbeats, executions,
  evaluator leases, alerts, activity events, and ingestion rate limits;
- expands the PostgreSQL Alembic version identifier column before recording
  the accepted `0018_agent_visibility_lifecycle_mvp` revision id;
- adds SQLAlchemy models, constraints, uniqueness rules, and indexes;
- adds a narrow active-surface selector so active dashboard projections can
  exclude hidden legacy/synthetic records while dormant descriptor routes remain
  available until later Work Orders replace them.

## Scope Alignment

In scope:

- schema, migration, model, and focused test work;
- local migration-cutover evidence using the existing sanitized SQLite evidence
  path;
- PostgreSQL-ready Alembic upgrade/downgrade definition for CI and later hosted
  evidence.

Out of scope and not implemented:

- owner enrollment routes;
- plaintext credential issuance;
- telemetry ingestion endpoints;
- evaluator execution;
- dashboard rewrite to live ES-009 data;
- hosted production migration execution.

## Route-Base Alignment

WO-065 does not add frontend routes. It preserves the ADP-006 route-base
adoption from WO-064:

- `/` remains the public Atlas landing page;
- `/control-center` remains the canonical authenticated dashboard root;
- active dashboard projections must exclude hidden legacy/synthetic records.

## Validation

Local validation run from a clean WO-065 branch based on the WO-064 merge:

```text
apps/api/.venv/bin/python -m mypy apps/api/src
Success: no issues found in 66 source files

apps/api/.venv/bin/python -m ruff check apps/api
All checks passed!

apps/api/.venv/bin/python -m pytest apps/api/tests/test_agent_visibility_schema.py apps/api/tests/test_agent_registry.py apps/api/tests/test_dashboard_facade.py apps/api/tests/test_migration_cutover.py
25 passed, 1 existing Starlette/httpx deprecation warning

apps/api/.venv/bin/python -m pytest apps/api
176 passed, 1 existing Starlette/httpx deprecation warning

git diff --check
pass
```

## Migration Evidence

- Local sanitized migration-cutover tests now identify repository head
  `0018_agent_visibility_lifecycle_mvp`.
- CI run 253 initially exposed that the accepted revision id exceeded the
  existing PostgreSQL `alembic_version.version_num` width. The migration now
  expands that internal Alembic column to 64 characters before Alembic records
  the new revision.
- PostgreSQL upgrade/downgrade evidence is expected from the governed CI
  migration step and must be recorded before merge.

## Security Notes

- No plaintext credential field exists in `agent_credentials`.
- Credential persistence stores only lookup id, verifier HMAC, key id, status,
  fixed telemetry scope, and lifecycle timestamps.
- Existing external-product-client credentials are not reused for agents.
- Synthetic smoke records are retained as evidence but excluded from active
  default projections.

## Rollback

Source rollback removes the new model and migration files before hosted
deployment. After hosted migration, rollback should default to forward repair
unless a reviewed runbook authorizes database downgrade.

## Residual Risks

- PostgreSQL migration execution is not performed locally in this report; CI
  must supply upgrade/downgrade evidence.
- Lifecycle services and telemetry behavior remain deferred to WO-066 through
  WO-068.
