# Work Order 058: Hosted Smoke Tests and Monitoring Confirmation

**Status:** Completed - Hosted Smoke Passed After WO-063
**Work Order ID:** WO-058
**Type:** Hosted validation and monitoring confirmation
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-19; pending WO-054 through WO-057 evidence
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-054 through WO-057 complete
**Review Record:** [WO-058 hosted smoke tests and monitoring confirmation report](../reviews/WO-058-hosted-smoke-tests-and-monitoring-confirmation-implementation-report.md)

## 1. Purpose

Validate the hosted MVP cutover through smoke tests, connector checks, audit
signals, log signals, and owner monitoring expectations.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Evidence data | Synthetic only unless separately authorized |
| Monitoring | Lightweight single-owner MVP posture |
| Audit | Material actions must emit audit evidence |
| Logs | Secret-free and body-minimized |

## 3. Approved Scope if Accepted

- Verify hosted frontend, API, readiness, owner session, connector health,
  manual run, approval/draft state, audit, logs, and alert expectations.
- Execute a synthetic Gmail/Drive hosted workflow only if authorized by this
  Work Order.
- Record minimized IDs, statuses, timestamps, and reason codes.

## 4. Explicitly Out of Scope

Load testing, chaos testing, public launch, production mailbox scans, broad
provider data extraction, enterprise monitoring, and automated remediation are
excluded.

## 5. Verification and Completion

Require hosted smoke checklist evidence, browser evidence, health/readiness
evidence, audit/log evidence, connector evidence, monitoring notes, and an
implementation report under `docs/reviews/`.

## 6. Rollback Expectations

If smoke validation fails, stop cutover, record blocker evidence, and follow
WO-059 rollback or corrective-forward procedures.

## 6.1 Superseded Blocker

Hosted smoke validation on 2026-07-21 confirmed that the dashboard and API
health endpoints are reachable and ready. It also confirmed that the deployed
dashboard's Connectors, Runs, Approvals, Audit, and Alerts surfaces are
explicitly fictional, session-only frontend prototypes. They do not call the
hosted runtime or expose the authenticated owner workflow required to verify
real connector health, a synthetic Gmail/Drive run, approval state, audit
events, log correlation, or monitoring signals.

The cutover is stopped. Do not begin WO-059 or WO-060 until a separately
accepted, implemented, and deployed dashboard-to-runtime integration scope has
resolved this blocker and WO-058 is rerun.

Proposed remediation scope is drafted as
[WO-062 Hosted Dashboard Runtime Integration](./062-hosted-dashboard-runtime-integration.md).

WO-062 has since been implemented, merged, deployed, and rerun against the
hosted dashboard.

## 6.2 Superseded Runtime Seed Blocker

Hosted smoke rerun on 2026-07-22 confirmed that the dashboard runtime
integration is deployed and owner-authenticated:

- the dashboard renders `RUNTIME READY`;
- the owner session redirects to
  `https://atlas.grafley.com/connectors?owner_session=signed_in`;
- Connectors, Runs, Approvals, Audit, and Alerts render live runtime states
  through the owner-authenticated dashboard facade;
- metadata-only audit and monitoring evidence is visible.

The smoke gate still cannot complete. The live Connectors page reports Gmail
and Google Drive as runtime descriptors, but both are `Offline` /
`Not connected`, and runtime health checks are disabled until owner connector
OAuth is completed. The live Runs page reports `0 of 0 runtime runs` and does
not expose a synthetic manual-run control because no runtime agent/manual-run
seed is available through the facade. The Approvals page has no pending runtime
approval state to inspect.

Do not begin WO-059 or WO-060 until a separately accepted, implemented, and
deployed runtime smoke seed / synthetic connector enablement scope resolves
this blocker and WO-058 is rerun successfully.

Proposed remediation scope is drafted as
[WO-063 Hosted Runtime Smoke Seed and Synthetic Connector Enablement](./063-hosted-runtime-smoke-seed-and-synthetic-connector-enablement.md).

WO-063 has since been implemented, merged, deployed, and used for a successful
WO-058 hosted smoke rerun.

## 6.3 Successful Rerun After WO-063

Hosted smoke rerun on 2026-07-22 passed after PR #109 deployed the
owner-authenticated synthetic runtime smoke seed:

- owner session verification returned authenticated through the dashboard
  facade;
- Netlify production deployed `main@18336a3`;
- API liveness and readiness returned healthy / ready;
- `POST /api/v1/dashboard/smoke-seed` failed closed without an owner session
  and succeeded with owner session, CSRF, and idempotency;
- hosted runtime evidence showed two synthetic connector connections
  (`gmail` and `google_drive`) with `connected` / `healthy` status;
- hosted runtime evidence showed one synthetic manual run with `succeeded`
  status;
- hosted runtime evidence showed one pending synthetic draft-review approval;
- hosted audit evidence included metadata-only seed events;
- hosted monitoring evidence returned `ready` with zero readiness problems.

No Gmail or Drive OAuth consent was submitted during this rerun. No provider
tokens, owner subject values, CSRF tokens, cookies, mailbox content, Drive
content, raw logs, or secrets were recorded.

WO-059 may proceed next under its accepted rollback and release-withdrawal
rehearsal scope. WO-060 remains blocked until WO-059 completes and the
Repository Maintainer records the required go/no-go / tag authority decision.

## 7. Stop-and-Ask Triggers

Stop before using real mailbox content, ignoring failed smoke checks, exposing
sensitive logs, weakening audit, or claiming production readiness with an
unresolved safety/security blocker.
