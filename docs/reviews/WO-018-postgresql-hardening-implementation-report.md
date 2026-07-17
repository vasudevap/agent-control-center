# WO-018 PostgreSQL Hardening Implementation Report

**Work Order:** [WO-018 PostgreSQL Environment and Migration Hardening](../work-orders/018-postgresql-environment-and-migration-hardening.md)
**Implementation Branch:** `codex/wo-018-postgresql-hardening-implementation`
**Implementation Status:** Complete
**Implementation Commit:** `45601b6`
**Merge Commit:** `0321508`
**Pull Request:** `#34`
**Report Date:** 2026-07-17
**Review Owner:** Repository Maintainer

---

## 1. Summary

WO-018 replaces the former SQLite-default migration smoke check with the
accepted PostgreSQL 18 validation path.

Delivered:

- Alembic obtains its connection only from `ATLAS_API_DATABASE_URL` and fails
  with a generic message when it is absent.
- The prior SQLite URL is removed from `alembic.ini`; SQLite remains limited to
  a narrow metadata unit test.
- GitHub Actions starts an ephemeral `postgres:18` service, waits for health,
  and runs Alembic upgrade and downgrade against it.
- CI uses only synthetic, disposable database/user credentials and never needs
  a provider or production secret.
- Local documentation defines the developer-managed PostgreSQL 18 setup and
  migration commands.
- Focused tests cover missing and configured migration URLs.

## 2. Scope Guardrails Preserved

The implementation does not add a schema or data migration, a live Render
database, a provider configuration file, committed database URL, real
credential, Docker/Compose file, authentication, authorization, API contract,
queue, scheduler, webhook hardening, observability, frontend, or Phase 5/6
behavior.

No ADR is required because this applies the accepted PostgreSQL system-of-record
and local/CI validation decisions without changing the hosting or provisioning
strategy.

## 3. Validation Evidence

Completed locally:

- `apps/api/.venv/bin/python -m pytest apps/api` — 17 passed; one existing
  Starlette/httpx deprecation warning.
- `apps/api/.venv/bin/python -m ruff check apps/api` — passed.
- `apps/api/.venv/bin/python -m mypy apps/api/src` — passed.
- `cd apps/api && .venv/bin/python -m alembic current` without a database URL
  — failed as designed with `ATLAS_API_DATABASE_URL is required for database
  migrations.` and did not disclose a connection value.
- `npm run typecheck` — passed.
- `npm run lint` — passed.
- `npm test` — 17 files and 80 tests passed.
- `npm run build` — passed after allowing access to the existing public Google
  Fonts requests; the sandboxed attempt could not resolve the font host.
- `git diff --check` — passed.
- Strict secret-pattern scan over changed files — no credential-like values;
  known synthetic CI values are confined to the ephemeral workflow service.

Required before merge:

- PostgreSQL 18 migration upgrade/downgrade in GitHub Actions.

The workstation has no local PostgreSQL 18 service. This is not bypassed:
GitHub Actions is the required ephemeral PostgreSQL 18 migration gate.

## 4. Residual Risks

| Risk | Treatment |
| --- | --- |
| Local developers need PostgreSQL 18 before running database migrations. | Canonical setup commands are documented; no hidden SQLite fallback remains. |
| CI service uses visible disposable credentials. | They are synthetic, scoped to the ephemeral service, and are not provider or production secrets. |
| Hosted Render PostgreSQL is not yet provisioned. | WO-016 preserves the planned Render target; live provisioning remains separately authorized. |

## 5. Next Recommended Work Order

Proceed to WO-019 — Owner Authentication and Session Foundation. PostgreSQL
migration compatibility is now enforced before the authentication foundation
adds persistence-dependent behavior.
