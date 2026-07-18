# Work Order 048: Deployment Path and Migration Readiness

**Status:** Implemented - Pending PR Review
**Work Order ID:** WO-048
**Type:** Deployment and data readiness
**Implementation Authorization:** Granted under ADP-004 on 2026-07-18
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)
**Governing Plan:** [Phase 7 Work Order Backlog](../implementation-plans/phase-7-work-order-backlog.md)
**Prerequisites:** WO-047 accepted readiness path
**Review Record:** [WO-048 Implementation Report](../reviews/WO-048-deployment-path-and-migration-readiness-implementation-report.md)

## 1. Purpose

Verify the accepted Netlify and Render deployment path, build/runtime settings,
migration procedure, backup/restore expectations, and rollback evidence before
production cutover.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Hosting path | Netlify frontend and Render backend/database unless an ADR changes this |
| Database | PostgreSQL remains runtime system of record |
| Migration posture | Backup/restore and rollback notes are required before production migration |
| Production cutover | Requires explicit release authority |

## 3. Approved Scope if Accepted

- Verify monorepo build commands, publish paths, runtime versions, service
  boundaries, health endpoints, and environment variable mapping.
- Document Render API service, scheduler/cron expectations, database migration
  command, and provider dashboard steps that cannot safely be represented in
  source.
- Add or update dry-run checks that do not require production credentials.
- Document backup, restore, migration rollback, deployment rollback, and
  destructive-operation controls.
- Record deployment readiness evidence without performing unauthorized
  production cutover.

## 4. Explicitly Out of Scope

Changing hosting providers, adding infrastructure-as-code, provisioning live
production resources, running production migrations, creating production
databases, and public release are excluded unless separately accepted.

## 5. Verification and Completion

Require local build/test evidence, migration-head verification, deployment
configuration review, provider-path dry-run or documented manual evidence,
rollback checklist evidence, and a readiness report under `docs/reviews/`.

## 6. Rollback Expectations

Rollback must preserve data integrity. Application rollback must not be treated
as database rollback. Migration rollback must include backup/restore awareness,
data compatibility notes, and a reviewed corrective path.

## 7. Stop-and-Ask Triggers

Stop before provisioning production resources, running production migrations,
changing provider topology, skipping backup/restore expectations, using live
provider credentials without authority, or weakening deployment controls for
convenience.
