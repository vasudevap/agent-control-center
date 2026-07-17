# Work Order 018: PostgreSQL Environment and Migration Hardening

**Status:** Completed
**Work Order ID:** WO-018
**Type:** Backend persistence foundation
**Implementation Authorization:** Granted
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Governing Strategy:** [Infrastructure Provisioning Strategy](../implementation-plans/infrastructure-provisioning-strategy.md)
**Architecture Authority:** [Deployment Architecture](../architecture/06-deployment-architecture.md), [Data Architecture](../architecture/08-data-architecture.md), [Security Architecture](../architecture/07-security-architecture.md)
**Prerequisite Work Order:** [WO-017 Backend Runtime and Dependency Hardening](./017-backend-runtime-and-dependency-hardening.md)
**Review Owner:** Repository Maintainer
**Review Record:** [WO-018 PostgreSQL Hardening Implementation Report](../reviews/WO-018-postgresql-hardening-implementation-report.md)

---

## 1. Purpose

Replace SQLite-only migration smoke validation with an explicit PostgreSQL path
for local development and GitHub Actions. This establishes the actual runtime
database compatibility gate before Phase 3 adds authentication, authorization,
queues, schedulers, or broader API contracts.

## 2. Decisions Fixed Before Implementation

The implementation must apply these already-selected decisions and must not
re-open them:

| Concern | Decision |
| --- | --- |
| Runtime system of record | PostgreSQL remains authoritative; SQLite is limited to narrow unit-test use. |
| PostgreSQL major version | PostgreSQL 18 for local and CI validation, matching Render's current default and supported major version. |
| Local path | Developer-managed PostgreSQL 18, installed through the maintainer's local package manager; no committed container, Compose, or provider configuration. |
| CI path | Ephemeral `postgres:18` GitHub Actions service on the existing Ubuntu runner, using disposable non-secret test credentials. |
| Test data | Synthetic only; created by migrations and destroyed with the CI service. |
| Connection configuration | `ATLAS_API_DATABASE_URL` only; no database URL committed to repository files. |
| Hosted environments | No Render database is created or changed by this Work Order. Render PostgreSQL remains the future hosted target. |

Render currently supports PostgreSQL 13–18 for new instances and defaults new
instances to 18 when a version is not specified. GitHub Actions supports a
PostgreSQL service container on Ubuntu runners with health checks and a mapped
localhost port. These facts were reviewed from the official Render and GitHub
documentation on 2026-07-17.

## 3. Approved Scope

### 3.1 Local PostgreSQL workflow

- Document exact PostgreSQL 18 prerequisites, database creation, environment
  variable setup, migration upgrade, migration downgrade, and cleanup commands.
- Add a narrowly scoped, non-secret local configuration example only if it does
  not contain a credential, URL, or generated database file.
- Make local database-dependent validation fail clearly when the configured
  PostgreSQL service is unavailable.

### 3.2 CI PostgreSQL migration validation

- Add an ephemeral PostgreSQL 18 service to the existing validation workflow.
- Configure only disposable CI test values in workflow environment variables.
- Run Alembic upgrade and downgrade against that PostgreSQL service.
- Preserve all existing frontend and backend checks and the constraints-based
  Python dependency install from WO-017.

### 3.3 Backend database boundary

- Refine engine/session configuration or migration configuration only as needed
  to use an injected PostgreSQL URL safely and deterministically.
- Add focused tests for database URL selection, migration execution, and
  unavailable-database behavior where practical.
- Keep readiness output structured and non-secret.

### 3.4 Documentation and evidence

- Update the root and backend READMEs with the canonical PostgreSQL 18 path.
- Add a WO-018 implementation report with local/CI validation, database
  isolation behavior, residual risks, and the next recommendation.
- Update the backlog and work-order index after completion.

## 4. Explicitly Out of Scope

WO-018 does not authorize:

- creating, provisioning, modifying, or connecting to a live Render PostgreSQL
  database, Netlify, Render service, worker, cron job, or production system;
- adding `render.yaml`, `netlify.toml`, Terraform, Pulumi, Dockerfiles, Compose
  files, or an `infrastructure/` directory;
- committing real credentials, database URLs, `.env` files, database dumps, or
  generated local database files;
- schema additions, business migrations, data seeding, or data migration;
- changes to the selected FastAPI, SQLAlchemy, Alembic, psycopg, PostgreSQL,
  GitHub Actions, or Render topology without a separate ADR;
- authentication, authorization, API contract expansion, queue, scheduler,
  webhook hardening, observability, frontend integration, or Phase 5/6 work.

## 5. Required File Scope

The implementing agent may create or modify:

- `.github/workflows/ci.yml`;
- `apps/api/alembic.ini`, `apps/api/alembic/`, and backend database/configuration
  modules only when required for PostgreSQL-compatible migration validation;
- backend tests under `apps/api/tests/`;
- `README.md`, `apps/api/README.md`, and relevant implementation-plan,
  work-order, and review records.

The agent must not add a business migration, alter frontend source, configure a
provider, create live resources, or modify unrelated documents.

## 6. Functional and Security Requirements

- CI migration smoke validation runs against PostgreSQL 18, not SQLite.
- CI service credentials are disposable, non-secret, and never reused outside
  the workflow; production credentials are not required.
- Local PostgreSQL commands use an uncommitted `ATLAS_API_DATABASE_URL`.
- Alembic upgrade and downgrade leave the disposable validation database in a
  known base state.
- Database connection strings, usernames, passwords, and host details must not
  appear in logs, errors, test fixtures, screenshots, or documentation.
- Database-dependent readiness fails safely without leaking connection details.
- Existing SQLite narrow-unit-test behavior may remain only where it does not
  substitute for the PostgreSQL migration gate.

## 7. Verification Plan

The implementation PR must include evidence for:

- `git diff --check` and strict secret-pattern scan over changed files;
- documented local PostgreSQL 18 migration upgrade/downgrade validation, or a
  precise environment blocker and compensating evidence;
- CI PostgreSQL 18 service migration upgrade/downgrade validation;
- backend dependency install, pytest, Ruff, and mypy;
- `npm run typecheck`, `npm run lint`, `npm test`, and `npm run build`;
- GitHub Actions passing on the full workflow.

## 8. Acceptance Criteria

WO-018 is complete only when:

- the repository maintainer accepts this Work Order before implementation;
- local and CI PostgreSQL 18 paths are documented and CI migration validation
  demonstrably uses PostgreSQL;
- no live provider resource, secret, schema expansion, or excluded Phase 3
  behavior is introduced;
- required local checks and GitHub CI pass;
- the implementation report records scope, validation, residual risks, and the
  next recommended Work Order;
- the branch merges through the required pull-request process.

## 9. Stop-and-Ask Triggers

The implementing agent must stop and ask before proceeding if:

- PostgreSQL 18 is unavailable in GitHub Actions or conflicts with the selected
  Python/psycopg toolchain;
- implementation needs a new package, a schema migration, live provider
  resource, provider credential, or production database URL;
- a local PostgreSQL prerequisite cannot be documented without requiring a
  committed Docker/Compose or provider configuration file;
- the work requires changing the accepted hosting, database, migration, or
  provisioning strategy;
- unrelated user changes overlap with required files or a destructive action is
  needed.

## 10. Completion Notes

The implementation adds only the selected PostgreSQL 18 migration validation
path, settings boundary, focused tests, CI configuration, and documentation.
No live resources, schema migration, provider configuration, or secrets were
added. See the linked implementation report for validation evidence.
