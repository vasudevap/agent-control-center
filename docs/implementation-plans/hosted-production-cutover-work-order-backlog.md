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
| WO-053 | Production Environment and Secrets Provisioning | ES-008 accepted | Limited | Completed - Provider Configuration Bound |
| WO-054 | Netlify Frontend Deployment | WO-053 env map | Limited | Completed - Hosted Runtime Evidence Captured |
| WO-055 | Render API and PostgreSQL Deployment | WO-053 env map | Limited | Completed - Hosted API and Database Ready |
| WO-056A | Grafley Custom Domain Cutover | WO-054, WO-055 hosted provider targets | No | Completed - Custom Domains and Runtime Cutover Verified |
| WO-056 | Google OAuth Production Client and Redirects | WO-056A final domain decision, WO-054, WO-055 URL decisions | No | In Progress - Google OAuth Provider Configured; Owner OIDC Gate Cleared |
| WO-061 | Google OIDC Owner Identity Enrollment | ADR-007, WO-055 hosted API | No | Completed - Owner Identity Bound and Readiness Verified |
| WO-057 | Hosted Migration, Backup, and Restore Readiness | WO-055 database ready | No | Completed - Hosted Migration Verified |
| WO-058 | Hosted Smoke Tests and Monitoring Confirmation | WO-054 through WO-057, including WO-056A | No | Blocked - Hosted Dashboard Is Not Connected to Runtime Services |
| WO-062 | Hosted Dashboard Runtime Integration | WO-058 blocker evidence, WO-019, WO-020, WO-046, WO-061 | No | Proposed - Pending Acceptance |
| WO-059 | Production Rollback and Release Withdrawal Rehearsal | Successful WO-058 rerun after WO-062 | No | Accepted - Pending Implementation |
| WO-060 | Release Tag and Production Closeout | Successful WO-058 rerun, WO-059 | No | Accepted - Pending Implementation |

## 3. Dependency Waves

| Wave | Work Orders | Purpose | Parallel posture |
| --- | --- | --- | --- |
| Wave 0 | ES-008, ADR assessment, backlog, ADP-005 acceptance | Governance readiness | Documentation review only |
| Wave 1 | WO-053 | Provider env/secrets inventory and provisioning authority | Serial gate before provider writes |
| Wave 2 | WO-054, WO-055 | Netlify frontend and Render API/PostgreSQL setup | Parallel only if provider boundaries are clear |
| Wave 3 | WO-056A, WO-056, WO-061, WO-057 | Grafley custom domains, connector OAuth, owner OIDC enrollment, migration, backup/restore | Serial because each Google client should use final URLs and migration depends on hosted database readiness |
| Wave 4 | WO-058, WO-062, WO-058 rerun, WO-059 | Hosted smoke, dashboard runtime remediation, rerun evidence, and rollback evidence | Serial release-safety lane |
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

### WO-056A - Grafley Custom Domain Cutover

Work Order:

- `docs/work-orders/056a-grafley-custom-domain-cutover.md`

Objective:

- Configure and verify the accepted Grafley product domains
  `https://atlas.grafley.com` and `https://api.atlas.grafley.com`, capture
  provider CNAME targets for Repository Maintainer DNS provisioning, and make
  the final domain decision before Google OAuth is finalized.

Current state:

- Netlify and Render custom-domain bindings exist. Both Grafley CNAME records
  are provisioned, provider TLS is active, Netlify `NEXT_PUBLIC_API_BASE_URL`
  points to `https://api.atlas.grafley.com`, Render
  `ATLAS_API_FRONTEND_ORIGIN` allows `https://atlas.grafley.com`, and
  final-origin API CORS evidence passed.

### WO-056 - Google OAuth Production Client and Redirects

Work Order:

- `docs/work-orders/056-google-oauth-production-client-and-redirects.md`

Objective:

- Configure Google OAuth client redirect URIs for the hosted API while
  preserving `gmail.modify` and `drive.file` scope posture.

Current state:

- Source preflight found no direct browser-facing Google OAuth callback route
  at the earlier placeholder `/api/auth/google/callback` path. The implemented
  connector completion route is `POST /api/v1/connectors/{connector_type}/oauth/callback`
  behind the external-client HMAC boundary, so WO-056 must choose and implement
  or confirm the production browser callback surface before Google provider
  values are entered.
- ADR-006 is accepted to use
  `https://atlas.grafley.com/oauth/google/callback` as the Google OAuth
  redirect URI, with server-side dashboard callback handling and API-owned
  provider token exchange.
- The source callback route and signed API completion endpoint are implemented.
  Google provider configuration is complete for Google Cloud project
  `atlas-agent-control-center`, Google account `grafleyinc@gmail.com`, and
  redirect URI `https://atlas.grafley.com/oauth/google/callback`. Render has
  the Google OAuth client ID, client secret, and redirect URI configured without
  value exposure. The remaining release blockers are the separately governed
  owner-OIDC configuration and immutable owner identity subject under WO-061.

### WO-061 - Google OIDC Owner Identity Enrollment

Work Order:

- `docs/work-orders/061-google-oidc-owner-identity-enrollment.md`

Objective:

- Establish a separate Google OIDC identity-verification path to derive and
  bind the immutable `sub` for `grafleyinc@gmail.com` without changing the
  Gmail/Drive connector OAuth scopes or client.

Current state:

- ADR-007 and WO-061 were accepted by the Repository Maintainer on 2026-07-20.
  The API owner-OIDC start and callback routes, dedicated configuration,
  transaction-cookie handling, server-side exchange boundary, injectable
  ID-token verification, minimized owner-facing output, and offline tests are
  implemented. PR #96 merged the source slice to `main`, Render deployed it,
  controlled authorization completed with `grafleyinc@gmail.com`, and the
  derived opaque owner subject was manually entered in Render without value
  exposure.
- The Atlas Render target is project-scoped: **My project -> Production ->
  atlas-agent-control-center-api -> Environment**. The workspace homepage's
  ungrouped service list is not a complete Atlas inventory. Canonical resource
  IDs are recorded in the WO-061 review report and environment-provisioning
  record.
- Final readiness now returns `ready` with no configuration problems. Remaining
  cutover work moves to WO-057 migration/backup/restore evidence and later
  smoke, rollback, release tag, and public-launch gates.

### WO-057 - Hosted Migration, Backup, and Restore Readiness

Work Order:

- `docs/work-orders/057-hosted-migration-backup-and-restore-readiness.md`

Objective:

- Execute or rehearse hosted database migration with backup, restore, and
  rollback evidence.

Current state:

- Render PostgreSQL backup path evidence is recorded as
  `render-pitr-paid-plan-2026-07-21`. The Repository Maintainer authorized
  hosted migration on 2026-07-21. Hosted Alembic upgrade ran through Render
  one-off job `job-d9ft82btqb8s73b9430g`, and final current-head verification
  passed through `job-d9ft8dnavr4c73e0751g` with repository head
  `0017_gmail_send_outcomes`.

### WO-058 - Hosted Smoke Tests and Monitoring Confirmation

Work Order:

- `docs/work-orders/058-hosted-smoke-tests-and-monitoring-confirmation.md`

Objective:

- Validate hosted frontend/API behavior, health/readiness, connector state,
  synthetic Gmail/Drive workflow evidence if authorized, audit/log signals, and
  owner monitoring expectations.

Current state:

- Hosted smoke validation on 2026-07-21 passed dashboard rendering, dashboard
  runtime readiness, API liveness/readiness, API health, final-origin CORS,
  and the OAuth-denial redirect. It is blocked because the deployed dashboard
  identifies its operational surfaces as fictional session-only prototypes;
  it cannot perform or display the real owner-session, connector, run,
  approval, audit, log, or monitoring checks required by this Work Order.
  Evidence is recorded in
  `docs/reviews/WO-058-hosted-smoke-tests-and-monitoring-confirmation-implementation-report.md`.

### WO-062 - Hosted Dashboard Runtime Integration

Work Order:

- `docs/work-orders/062-hosted-dashboard-runtime-integration.md`

Objective:

- Resolve the WO-058 blocker by replacing release-critical fixture-only
  dashboard paths with owner-authenticated, server-signed hosted API
  integrations for connector, run, approval, audit, and monitoring evidence.

Current state:

- Proposed after WO-058 recorded that the deployed dashboard cannot exercise
  the real owner-session, connector, run, approval, audit, log, or monitoring
  workflow required for hosted smoke completion. WO-062 must be accepted,
  implemented, deployed, and followed by a successful WO-058 rerun before
  WO-059 or WO-060 can begin.

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
- custom-domain setup requires a different provider, registrar, paid plan, or
  DNS authority decision;
- production migration or rollback instructions are ambiguous;
- required CI fails and the needed fix is outside the current Work Order;
- a new ADR is required.

## 6. Acceptance Boundary

This backlog was accepted by the Repository Maintainer on 2026-07-19 with
ES-008 and ADP-005. WO-056A was added on 2026-07-20 after the Repository
Maintainer accepted Grafley custom domains. Later on 2026-07-20, the Repository
Maintainer confirmed that `atlas-owner@grafley.com` is not a Google account and
authorized `grafleyinc@gmail.com` as the single-owner Google account for the
OAuth cutover. ADR-007 and WO-061 were accepted later that day for local
source implementation only. This backlog authorizes only the bounded Work
Order sequence above. Deployment, provider configuration, migrations, release
tags, and production use must remain inside the active Work Order scope and
stop-and-ask triggers.
