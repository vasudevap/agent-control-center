# WO-057 Hosted Migration, Backup, and Restore Readiness Implementation Report

**Work Order:** [WO-057](../work-orders/057-hosted-migration-backup-and-restore-readiness.md)
**Status:** Completed - Hosted Migration Verified
**Date:** 2026-07-21
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Summary

WO-057 now has source-controlled migration cutover guardrails, a hosted
backup/restore readiness record, local migration validation, hosted migration
execution evidence, final current-head verification, and hosted API health
evidence. Hosted migration ran only after backup evidence was recorded and the
Repository Maintainer authorized execution on 2026-07-21.

No hosted database connection URL, password, OAuth secret, token, backup export
URL, owner subject, or signing secret was displayed, copied to Git, captured
in screenshots, or shared in chat.

## Scope Implemented

- Added the `atlas-migration-cutover` console script.
- Added guarded upgrade behavior that requires:
  - `--confirm-hosted-migration`
  - `--authority-ticket`
  - `--backup-evidence-id`
- Added evidence-label validation to reject URL-like or email-like values.
- Applied evidence-label validation before any database connection attempt,
  including optional labels supplied in read-only check mode.
- Added sanitized JSON evidence with repository head, before/after migration
  revisions, environment, and non-secret evidence labels.
- Added tests for the explicit migration authority gate, local upgrade to
  Alembic head, and evidence-label redaction guard.
- Added SQLAlchemy database URL normalization so provider-managed
  `postgres://` and `postgresql://` values use the installed `psycopg` driver
  for migration and scheduled-job commands.
- Added the hosted migration, backup, restore, and failure-handling readiness
  record under `docs/implementation-plans/`.
- Updated the API README with the guarded check and upgrade commands.

## Backup and Restore Evidence

Render documentation records two accepted provider recovery paths for paid
Render PostgreSQL instances:

- point-in-time recovery from the database Recovery page;
- manual logical exports created through Create export from the same Recovery
  page.

References:

- [Render Postgres Recovery and Backups](https://render.com/docs/postgresql-backups)
- [Render Postgres](https://render.com/docs/postgresql)

WO-055 provider evidence records the Atlas PostgreSQL target as
`atlas-agent-control-center-db`, ID `dpg-d9e2rkbrjlhs73bkc6dg-a`, PostgreSQL
18, plan `basic_256mb`.

Read-only Render CLI confirmation on 2026-07-21 returned the same target as
`available`, `not_suspended`, PostgreSQL 18, plan `basic_256mb`, disk size 15
GB, region `ohio`, and project ID `prj-d8dqn1mk1jcs7399ubvg`. The command did
not use `--include-sensitive-connection-info`, and no connection string or
credential was printed.

Confirmed non-secret backup evidence label:

```text
render-pitr-paid-plan-2026-07-21
```

This label confirms the provider PITR path for WO-057. The Repository
Maintainer authorized hosted migration execution on 2026-07-21 using this
recorded PITR evidence label. A manual logical export was not created or
confirmed for WO-057. If the maintainer requires a logical export for a later
operation, use a new label in the format `render-export-created-YYYYMMDD-HHMMZ`
only after the export exists in the Render Recovery page.

Restore must use a separate recovery database first. Destructive in-place
restore remains out of scope without a separate explicit approval.

## Local Migration Evidence

Command:

```text
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas_wo057_migration_20260721_1.db apps/api/.venv/bin/python -m atlas_api.cli.migration_cutover --mode upgrade --confirm-hosted-migration --authority-ticket WO-057-local-validation --backup-evidence-id local-disposable-db --require-current-head
```

Result:

```json
{"authority_ticket": "WO-057-local-validation", "backup_evidence_id": "local-disposable-db", "checked_at": "2026-07-21T19:06:28+00:00", "database_url_configured": true, "environment": "local", "migration_required_before": true, "mode": "upgrade", "repository_head": "0017_gmail_send_outcomes", "revision_after": "0017_gmail_send_outcomes", "revision_before": null, "upgrade_performed": true}
```

The command output did not include the configured database URL.

## Hosted Migration Status

Hosted migration ran successfully.

Execution context:

- Target API service: `atlas-agent-control-center-api`
  (`srv-d9e2rprbc2fs73f4l23g`).
- Target database: `atlas-agent-control-center-db`
  (`dpg-d9e2rkbrjlhs73bkc6dg-a`).
- Backup evidence label: `render-pitr-paid-plan-2026-07-21`.
- Authority ticket: maintainer `authorized` message on 2026-07-21.

Direct external `render psql` access from the local task environment was
blocked by the Render database IP allow list, so migration was executed through
Render one-off jobs from the API service context. The deployed provider-managed
database URL was present but not already in SQLAlchemy's
`postgresql+psycopg://` driver form. The migration and verification commands
normalized the URL scheme in memory, did not print the URL, and did not change
the Render environment value.

Evidence:

| Evidence | Result |
| --- | --- |
| Initial direct `render psql` check | Blocked by database IP allow list before any migration |
| Render job `job-d9ft7pvavr4c73e05rt0` | Normalized SQLAlchemy DB connectivity probe succeeded |
| Render job `job-d9ft82btqb8s73b9430g` | Alembic `upgrade head` succeeded |
| Render job `job-d9ft8dnavr4c73e0751g` | Current-head verification succeeded for `0017_gmail_send_outcomes` |

Hosted API compatibility after migration:

| Check | Result |
| --- | --- |
| `https://api.atlas.grafley.com/health/live` | `status=ok`, `environment=production` |
| `https://api.atlas.grafley.com/health/ready` | `status=ready`, no configuration problems |
| `https://api.atlas.grafley.com/api/v1/health` | `status=ok`, correlation ID returned |

## Rollback and Corrective-Forward Notes

Application rollback does not roll back the database. If migration fails,
cutover promotion stops and the maintainer should choose one reviewed path:

- corrective-forward migration if schema/data state is valid and the fix is
  safer than restore;
- Render point-in-time recovery into a separate recovery database;
- logical export restore into an empty replacement database.

The service should only be redirected to a recovery database after recovered
state is verified and provider environment changes are authorized.

## Validation Commands

Focused migration cutover tests:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_migration_cutover.py
```

Result:

```text
4 passed
```

Release-readiness artifact test:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_release_readiness.py
```

Result:

```text
3 passed
```

Combined focused validation:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_migration_cutover.py apps/api/tests/test_release_readiness.py
```

Result:

```text
7 passed
```

Focused lint:

```text
apps/api/.venv/bin/python -m ruff check apps/api/src/atlas_api/db/config.py apps/api/src/atlas_api/cli/migration_cutover.py apps/api/tests/test_config.py apps/api/tests/test_migration_cutover.py apps/api/tests/test_release_readiness.py
```

Result:

```text
All checks passed!
```

Focused configuration, migration, and release-readiness tests:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_config.py apps/api/tests/test_migration_cutover.py apps/api/tests/test_release_readiness.py
```

Result:

```text
21 passed
```

Full backend validation:

```text
apps/api/.venv/bin/python -m pytest apps/api
apps/api/.venv/bin/python -m ruff check apps/api
apps/api/.venv/bin/python -m mypy apps/api/src
```

Result:

```text
159 passed, 1 warning
All checks passed!
Success: no issues found in 64 source files
```

Static diff validation:

```text
git diff --check
```

Result:

```text
Passed
```

Secret-pattern scan:

```text
rg -n "(sk-[A-Za-z0-9]|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\s*=|refresh_token|access_token|postgresql://[^<]|postgresql\+psycopg://[^<])" apps/api docs
```

Result:

```text
Only pre-existing false positives, placeholder test values, and documented
scan command patterns were found; no WO-057 credential, provider URL, token,
or secret value was added.
```

## Residual Risks

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Render Recovery page screenshot/export artifact is not captured in Git | Accepted PITR evidence label only | Capture a new non-secret export label before any future restore or higher-risk migration if required |
| Restore has not been rehearsed against a Render recovery instance | Deferred | Requires provider restore authority and review of any service redirection |
| Render database URL remains provider-managed rather than driver-qualified | Mitigated in source by SQLAlchemy URL normalization | Deploy source guardrail before relying on future CLI database commands |

## Completion State

WO-057 source guardrails, procedure documentation, hosted migration execution,
and final current-head evidence are complete. The next dependency-ready Work
Order is WO-058 Hosted Smoke Tests and Monitoring Confirmation.
