# Hosted Migration, Backup, and Restore Readiness

**Status:** Completed - Hosted Migration Verified
**Owner:** Repository Maintainer
**Date:** 2026-07-21
**Work Order:** [WO-057](../work-orders/057-hosted-migration-backup-and-restore-readiness.md)
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)

---

## 1. Purpose

Record the governed hosted PostgreSQL migration procedure, Render backup and
restore path, migration evidence command, and rollback expectations for the
single-owner hosted MVP cutover.

This record does not contain database URLs, credentials, backup files, export
links, OAuth tokens, owner-subject values, or provider secrets.

## 2. Current Hosted Target

| Concern | Current value |
| --- | --- |
| Provider | Render PostgreSQL |
| Database target | `atlas-agent-control-center-db` |
| Database ID | `dpg-d9e2rkbrjlhs73bkc6dg-a` |
| PostgreSQL version | 18 |
| Plan evidence | `basic_256mb` recorded by WO-055 |
| API service | `atlas-agent-control-center-api` |
| API URL | `https://api.atlas.grafley.com` |
| Migration tool | Alembic |
| Repository head | `0017_gmail_send_outcomes` |

Render documentation states that paid Render PostgreSQL instances have
point-in-time recovery and on-demand logical exports. The current WO-055
provider evidence records a non-free Render PostgreSQL plan, so the accepted
backup path is provider recovery plus a manual logical export from the
database Recovery page before hosted migration execution.

References:

- [Render Postgres Recovery and Backups](https://render.com/docs/postgresql-backups)
- [Render Postgres](https://render.com/docs/postgresql)

## 3. Confirmed Evidence Labels

| Evidence label | Meaning | Source |
| --- | --- | --- |
| `render-pitr-paid-plan-2026-07-21` | Render PostgreSQL target is `available` on paid plan `basic_256mb`; Render documentation confirms paid Render Postgres has Point-in-Time Recovery and on-demand logical exports. | Read-only `render postgres list/get` metadata plus Render documentation |
| `render-export-created-YYYYMMDD-HHMMZ` | Reserved format for a future manual logical export after it is actually created from the Render Recovery page. | Not captured for WO-057 |

Use `render-pitr-paid-plan-2026-07-21` as the current WO-057
`--backup-evidence-id` if the maintainer accepts provider PITR as sufficient
backup evidence for the hosted migration. Use an actual
`render-export-created-...` label only after a logical export exists.

The Repository Maintainer authorized hosted migration execution on 2026-07-21
using the recorded PITR evidence label.

## 4. Pre-Migration Gate

Hosted migration must not begin until all of the following are true:

| Gate | Required evidence |
| --- | --- |
| Target confirmation | The Render database target is confirmed as `atlas-agent-control-center-db` in the project-scoped production environment. |
| Backup path | `render-pitr-paid-plan-2026-07-21` is recorded, or newer Render Recovery page evidence supersedes it. |
| Logical export | A new manual export is created from the Render Recovery page through Create export, or the maintainer explicitly accepts PITR-only recovery for this migration. |
| Restore path | Restore into a separate recovery database remains available; destructive in-place restore is not authorized. |
| Application commit | The deployed API commit is recorded before migration. |
| Migration head | Repository head is recorded as `0017_gmail_send_outcomes`. |
| Authority | The Repository Maintainer explicitly authorizes hosted migration execution after backup evidence is available. |

## 5. Evidence Commands

Read-only current-head verification:

```bash
ATLAS_API_DATABASE_URL='<provider-managed-url>' atlas-migration-cutover --mode check --require-current-head
```

Authorized hosted upgrade:

```bash
ATLAS_API_DATABASE_URL='<provider-managed-url>' atlas-migration-cutover --mode upgrade --confirm-hosted-migration --authority-ticket WO-057-maintainer-approval --backup-evidence-id render-pitr-paid-plan-2026-07-21 --require-current-head
```

The helper prints sanitized JSON evidence:

- `environment`
- `database_url_configured`
- `repository_head`
- `revision_before`
- `revision_after`
- `migration_required_before`
- `upgrade_performed`
- `authority_ticket`
- `backup_evidence_id`

The helper must not print the database URL, export URL, credential, token, or
secret value.

Hosted migration was executed from the Render API service context because the
database IP allow list blocked direct local `psql` access. Render one-off job
`job-d9ft82btqb8s73b9430g` ran Alembic `upgrade head` successfully on
2026-07-21. Render one-off job `job-d9ft8dnavr4c73e0751g` then verified that
the hosted database revision equals repository head `0017_gmail_send_outcomes`.
The job commands normalized the provider-managed PostgreSQL URL to the
installed SQLAlchemy `psycopg` driver form in memory and did not print the
database URL.

## 6. Restore Procedure

Preferred restore is isolated recovery, not in-place replacement:

1. Open the Render database Recovery page.
2. Use Point-in-Time Recovery to create a new recovery database at the selected
   timestamp, or download the logical export created before migration.
3. Validate the recovered database before redirecting services.
4. Update service environment configuration to the recovery database only after
   maintainer approval.
5. Verify `/health/ready`, owner session behavior, connector health, and
   synthetic workflow checks under the relevant Work Orders.
6. Retain or retire the original database only after the replacement path is
   verified and recorded.

Do not restore in place or run destructive restore commands against the
primary hosted database without a separate explicit approval record.

## 7. Migration Failure Handling

If hosted migration fails:

- stop cutover promotion immediately;
- preserve the original error output with secrets redacted;
- record whether the database revision changed;
- do not retry blindly;
- prefer a reviewed corrective-forward migration when data remains valid;
- use Render point-in-time recovery or logical export restore only after the
  data impact is understood and maintainer approval is recorded;
- keep application rollback separate from database rollback.

## 8. Completion Evidence

WO-057 can close only after the review report records:

- local migration validation;
- Render backup or export path evidence;
- hosted migration check or upgrade evidence;
- final Alembic current-head evidence;
- restore procedure confirmation;
- migration failure and corrective-forward notes;
- a secret/log redaction scan.
