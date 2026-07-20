# Hosted Production Cutover Work Order Backlog

**Status:** Accepted - In Progress
**Owner:** Repository Maintainer
**Date:** 2026-07-19
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**ADR Assessment:** [Hosted Production Cutover ADR Assessment](./hosted-production-cutover-adr-assessment.md)
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-19

---

## 1. Purpose

Define the proposed Work Order sequence for taking the accepted MVP release
candidate to a hosted single-owner deployment on Netlify and Render.

Each Work Order remains the bounded implementation authority for its scope,
exclusions, validation, rollback expectations, and stop-and-ask triggers after
acceptance.

## 2. Work Order Map

| Work Order | Name | Depends On | Parallelizable | Status |
| --- | --- | --- | --- | --- |
| WO-053 | Production Environment and Secrets Provisioning | ES-008 accepted | Limited | Accepted - In Progress |
| WO-054 | Netlify Frontend Deployment | WO-053 env map | Limited | Blocked - API CORS Source Fix Pending Deploy |
| WO-055 | Render API and PostgreSQL Deployment | WO-053 env map | Limited | Blocked - Secret/Database Binding Pending |
| WO-056 | Google OAuth Production Client and Redirects | WO-054, WO-055 URL decisions | No | Accepted - Pending Implementation |
| WO-057 | Hosted Migration, Backup, and Restore Readiness | WO-055 database ready | No | Accepted - Pending Implementation |
| WO-058 | Hosted Smoke Tests and Monitoring Confirmation | WO-054 through WO-057 | No | Accepted - Pending Implementation |
| WO-059 | Production Rollback and Release Withdrawal Rehearsal | WO-054 through WO-058 | No | Accepted - Pending Implementation |
| WO-060 | Release Tag and Production Closeout | WO-058, WO-059 | No | Accepted - Pending Implementation |

## 3. Dependency Waves

| Wave | Work Orders | Purpose | Parallel posture |
| --- | --- | --- | --- |
| Wave 0 | ES-008, ADR assessment, backlog, ADP-005 acceptance | Governance readiness | Documentation review only |
| Wave 1 | WO-053 | Provider env/secrets inventory and provisioning authority | Serial gate before provider writes |
| Wave 2 | WO-054, WO-055 | Netlify frontend and Render API/PostgreSQL setup | Parallel only if provider boundaries are clear |
| Wave 3 | WO-056, WO-057 | OAuth redirects, migration, backup/restore | Serial because they depend on hosted URLs and database |
| Wave 4 | WO-058, WO-059 | Hosted smoke and rollback evidence | Serial release-safety lane |
| Wave 5 | WO-060 | Go/no-go, optional tag, closeout | Maintainer decision lane |

## 4. Accepted Work Orders

### WO-053 - Production Environment and Secrets Provisioning

Work Order:

- `docs/work-orders/053-production-environment-and-secrets-provisioning.md`

Objective:

- Configure provider-native environment variables and secrets for Netlify,
  Render, PostgreSQL, and Google OAuth without exposing secret values.

### WO-054 - Netlify Frontend Deployment

Work Order:

- `docs/work-orders/054-netlify-frontend-deployment.md`

Objective:

- Deploy the Atlas web dashboard to Netlify with the accepted build command,
  publish path, environment variables, runtime health URL, and rollback path.

### WO-055 - Render API and PostgreSQL Deployment

Work Order:

- `docs/work-orders/055-render-api-and-postgresql-deployment.md`

Objective:

- Deploy the Atlas FastAPI service and PostgreSQL database on Render with
  health/readiness, logs, runtime settings, and provider rollback evidence.

### WO-056 - Google OAuth Production Client and Redirects

Work Order:

- `docs/work-orders/056-google-oauth-production-client-and-redirects.md`

Objective:

- Configure Google OAuth client redirect URIs for the hosted API while
  preserving `gmail.modify` and `drive.file` scope posture.

### WO-057 - Hosted Migration, Backup, and Restore Readiness

Work Order:

- `docs/work-orders/057-hosted-migration-backup-and-restore-readiness.md`

Objective:

- Execute or rehearse hosted database migration with backup, restore, and
  rollback evidence.

### WO-058 - Hosted Smoke Tests and Monitoring Confirmation

Work Order:

- `docs/work-orders/058-hosted-smoke-tests-and-monitoring-confirmation.md`

Objective:

- Validate hosted frontend/API behavior, health/readiness, connector state,
  synthetic Gmail/Drive workflow evidence if authorized, audit/log signals, and
  owner monitoring expectations.

### WO-059 - Production Rollback and Release Withdrawal Rehearsal

Work Order:

- `docs/work-orders/059-production-rollback-and-release-withdrawal-rehearsal.md`

Objective:

- Confirm Netlify, Render, migration, OAuth, Gmail/Drive cleanup, and release
  withdrawal procedures before go/no-go.

### WO-060 - Release Tag and Production Closeout

Work Order:

- `docs/work-orders/060-release-tag-and-production-closeout.md`

Objective:

- Record the final go/no-go decision, optional release-tag authority, hosted
  URLs, validation evidence, residual risks, and ADP-005 closeout.

## 5. Stop-and-Ask Triggers

Stop before implementation if:

- ES-008, ADP-005, or the relevant Work Order is not accepted;
- a provider write, deployment, migration, rollback, tag, revoke, delete, or
  credential action lacks explicit Work Order authority;
- secret values would be exposed in source, logs, screenshots, PRs, or chat;
- Google requires broader OAuth scopes or external verification;
- production mailbox data, personal mailbox data, or non-synthetic test data
  would be used to fill evidence gaps;
- production migration or rollback instructions are ambiguous;
- required CI fails and the needed fix is outside the current Work Order;
- a new ADR is required.

## 6. Acceptance Boundary

This backlog was accepted by the Repository Maintainer on 2026-07-19 with
ES-008 and ADP-005. It authorizes only the bounded Work Order sequence above.
Deployment, provider configuration, migrations, release tags, and production
use must remain inside the active Work Order scope and stop-and-ask triggers.
