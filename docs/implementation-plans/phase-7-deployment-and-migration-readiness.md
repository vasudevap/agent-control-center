# Phase 7 Deployment and Migration Readiness

**Status:** Implemented - Pending Review
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Work Order:** [WO-048](../work-orders/048-deployment-path-and-migration-readiness.md)
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)

---

## 1. Purpose

Record the accepted Netlify and Render deployment path, migration procedure,
backup/restore expectations, rollback controls, and source-level dry-run
evidence before any production cutover.

This record does not authorize live provisioning, production deployment,
production database creation, production migration execution, or provider
credential use.

## 2. Source-Level Readiness

| Area | Evidence | Status |
| --- | --- | --- |
| Monorepo workspace | Root `package.json` declares `apps/*` workspaces | Ready |
| Frontend build | Root `npm run build` delegates to `@atlas/web`; web build runs `next build` | Ready for local/CI validation |
| Backend runtime | API package requires Python 3.12+ and exposes `atlas_api.main:app` | Ready for Render command configuration |
| Scheduler | API package exposes `atlas-schedule-sweep` console script | Ready for Render Cron command configuration |
| Migrations | `apps/api/alembic.ini` and CI Alembic upgrade/downgrade checks exist | Ready for non-production migration validation |
| CI database | GitHub Actions uses ephemeral PostgreSQL 18 | Ready |
| Provider config files | No `render.yaml` or `netlify.toml` is committed | Expected; live provisioning not authorized |

The source-level dry-run test is
`apps/api/tests/test_release_readiness.py`.

## 3. Frontend Deployment Path

| Concern | MVP readiness value |
| --- | --- |
| Platform | Netlify |
| Repository base | Repository root unless later provider setup proves a narrower base is required |
| Package manager | npm workspaces |
| Install command | `npm ci` |
| Build command | `npm run build` |
| App build command | `npm --workspace @atlas/web run build` |
| Runtime artifact | Next.js output from `apps/web` managed by Netlify's Next.js support |
| Required browser-visible env | `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_APP_ENV` |
| Recommended browser-visible env | `NEXT_PUBLIC_RELEASE_VERSION` |
| Secret handling | Never place secrets in `NEXT_PUBLIC_` variables |

Provider setup may add a Netlify configuration file only after the applicable
deployment/provisioning authority accepts it.

## 4. Backend Deployment Path

| Concern | MVP readiness value |
| --- | --- |
| Platform | Render Web Service |
| Runtime | Python 3.12+ |
| Install command | `python -m pip install -c apps/api/constraints.txt -e "apps/api"` |
| Start command | `python -m uvicorn atlas_api.main:app --app-dir apps/api/src --host 0.0.0.0 --port $PORT` |
| Liveness endpoint | `/health/live` |
| Readiness endpoint | `/health/ready` |
| Database | Render PostgreSQL using internal URL for runtime services |
| Required backend env | See [Phase 7 Environment Configuration and Secrets Readiness](./phase-7-environment-configuration-and-secrets-readiness.md) |
| Secret handling | Render environment variables or environment groups; no committed secret values |

## 5. Scheduler Path

| Concern | MVP readiness value |
| --- | --- |
| Platform | Render Cron Job |
| Command | `atlas-schedule-sweep` |
| Database access | Same PostgreSQL system of record as API |
| Cadence | Five minutes unless a later Work Order accepts a different cadence |
| Production use | Requires deployment authority and recovery/runbook evidence |

The scheduler command is one-shot by design. It must not become a long-running
daemon without a new Work Order or ADR if architecture changes.

## 6. Migration Procedure

Non-production migration validation:

```bash
cd apps/api
ATLAS_API_DATABASE_URL='postgresql+psycopg://<user>:<password>@<host>:5432/<db>' python -m alembic upgrade head
ATLAS_API_DATABASE_URL='postgresql+psycopg://<user>:<password>@<host>:5432/<db>' python -m alembic current
```

Production migration requirements before execution:

- confirm the target database is the intended production database;
- confirm a current backup or provider recovery point exists;
- confirm the migration head and application commit being deployed;
- run migration from an approved maintainer-controlled execution context;
- record command, timestamp, commit, migration head, and result without
  printing the database URL;
- keep application rollback and database rollback decisions separate.

## 7. Backup and Restore Expectations

| Environment | Expectation |
| --- | --- |
| Local | Disposable unless developer chooses otherwise |
| CI | Disposable PostgreSQL 18 service |
| Development | Backup optional until non-reproducible data exists |
| Production | Paid Render PostgreSQL plan with provider recovery support before real operational data |

Production restore should prefer restore into a separate recovery database,
validation of recovered state, and controlled service redirection. Destructive
in-place restore requires explicit maintainer approval.

## 8. Rollback Controls

Application rollback:

- use Netlify deployment rollback for dashboard rollback;
- use Render previous deploy rollback or corrective deploy for API rollback;
- keep release tags immutable;
- prefer reviewed revert or corrective forward release.

Database rollback:

- do not assume application rollback undoes schema or data changes;
- prefer backward-compatible migrations;
- document migration-specific rollback notes in each schema-changing Work
  Order;
- use backup/restore only after validating data implications.

Provider side effects:

- Gmail/Drive side effects require manual reconciliation and cleanup runbooks;
- indeterminate sends must never be blindly retried;
- credential exposure requires revocation or rotation.

## 9. Manual Provider Evidence Still Required

The following evidence cannot be produced without provider access and remains
future gated work:

- Netlify site settings, deploy context, and environment variable evidence;
- Render service, database, cron, and environment group evidence;
- Render PostgreSQL backup/recovery plan evidence;
- hosted `/health/live` and `/health/ready` checks;
- production migration execution evidence;
- deployment rollback screenshots or provider logs.

WO-048 records the source and procedure readiness needed before that provider
evidence is collected.
