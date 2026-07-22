# Work Order 062: Hosted Dashboard Runtime Integration

**Status:** Completed - Deployed and Authenticated Runtime Surfaces Verified
**Work Order ID:** WO-062
**Type:** Hosted dashboard remediation and runtime integration
**Implementation Authorization:** Accepted by Repository Maintainer; autonomous implementation, WO-058 rerun, WO-059, and WO-060 continuation authorized in one sequence
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-019, WO-020, WO-046, WO-056, WO-057, WO-058 blocker evidence, WO-061
**Review Record:** [WO-062 Implementation Report](../reviews/WO-062-hosted-dashboard-runtime-integration-implementation-report.md)

## 1. Purpose

Resolve the WO-058 hosted smoke blocker by integrating the hosted dashboard
with the existing authenticated Atlas API contracts, while preserving the
single-owner, secret-free browser boundary required for hosted production
cutover.

This Work Order creates the owner-facing operational surface needed to rerun
WO-058 and produce real connector, run, approval, audit, log, and monitoring
evidence. It does not itself complete WO-058, authorize production launch, or
begin WO-059/WO-060.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Browser secret boundary | External-client HMAC secrets remain server-side only and are never exposed to browser JavaScript, local storage, page props, logs, or screenshots. |
| Owner access boundary | Hosted operational dashboard access must be gated by the existing single-owner session or an accepted equivalent owner-authenticated boundary before live runtime actions are exposed. |
| API authority | The dashboard consumes existing backend contracts; it does not create new backend semantics unless a small facade endpoint is required and reviewed within this scope. |
| Runtime integration path | Use API-owned dashboard facade endpoints gated by the existing host-only owner session cookie, with the dashboard browser calling the API using credentials. This avoids exposing external-client HMAC secrets to the browser and avoids requiring a Next.js server proxy to read API-host cookies. |
| Initial integration slice | Start with read-only status and connector inventory/connection health before enabling controlled OAuth start, manual run creation, approval decisions, or revocation actions. |
| Evidence data | Synthetic only unless separately authorized; no production mailbox scans, broad provider extraction, or personal mailbox content. |
| Fixture posture | Fixture-only operational pages must be replaced, removed, or clearly quarantined away from release-critical hosted paths. |

## 3. Approved Scope if Accepted

- Add API-owned dashboard facade endpoints that support owner-authenticated
  `GET` and controlled state-changing requests, correlation IDs, idempotency
  keys where required, timeout handling, structured errors, and secret
  redaction.
- Gate all dashboard runtime routes behind the accepted owner session boundary
  or a separately accepted owner-authenticated equivalent.
- Replace the hosted Connectors page's release-critical path with real
  connector descriptors, connection list, connection health, and safe OAuth
  start evidence using the hosted API.
- Replace or integrate the hosted Runs page with real run list/detail data and
  controlled manual-run creation for synthetic-only smoke evidence.
- Replace or integrate the hosted Approvals page with real approval list/detail
  evidence and decision controls only where existing approval authorization,
  revision, idempotency, and reason requirements are preserved.
- Replace or integrate the hosted Audit page with metadata-only audit event
  visibility needed to correlate WO-058 smoke checks.
- Replace or integrate Alerts/monitoring with the lightweight MVP posture from
  WO-049, or document a narrower owner-facing monitoring surface that satisfies
  WO-058 without pretending fixture alerts are runtime evidence.
- Preserve existing design-system conventions, responsive behavior,
  accessibility, and explicit loading/empty/error/unauthorized/stale states.
- Update dashboard tests, source documentation, Work Order status records, and
  the WO-062 implementation report.

## 4. Explicitly Out of Scope

Public launch, release tagging, WO-059 rollback rehearsal, WO-060 closeout,
new provider infrastructure, new OAuth scopes, new Google clients, production
mailbox scans, non-synthetic provider content, broad redesign, multi-user
authentication, RBAC, enterprise monitoring, automated remediation, schema
changes unrelated to the integration, and weakening existing backend
authorization or audit controls are excluded.

## 5. Security and Architecture Requirements

- The browser must never receive Atlas external-client HMAC secrets, provider
  credentials, OAuth codes, access tokens, refresh tokens, database URLs,
  webhook signing secrets, owner-subject values, or raw logs.
- A public unauthenticated visitor must not be able to use the dashboard as a
  signed API tunnel. Missing, expired, revoked, or invalid owner sessions must
  fail closed.
- State-changing requests must preserve existing API requirements for
  idempotency, approval revision, CSRF/session protection where applicable, and
  audit evidence.
- Server-side route handlers must minimize logged request/response data and
  expose only stable statuses, IDs, timestamps, reason codes, and correlation
  IDs needed for owner operation and WO-058 evidence.
- Any need to change owner authentication, external-client authentication,
  approval semantics, Google OAuth scopes, deployment topology, or monitoring
  posture beyond this Work Order requires a stop-and-ask decision and possibly
  a new ADR.

## 6. Verification and Completion

Require:

- frontend unit/component tests for all touched runtime pages and states;
- API dashboard facade tests covering owner session validation, `GET`, controlled
  state-changing requests, correlation IDs, idempotency, and secret redaction;
- owner-session gate tests proving unauthorized browser access fails closed;
- backend contract compatibility tests or smoke checks for touched API
  surfaces;
- `npm run lint`, `npm run typecheck`, `npm run build`, and relevant `npm test`
  targets;
- backend focused tests if API facade code is touched;
- `git diff --check`;
- focused secret/token scans across touched web, API, and documentation files;
- deployed Netlify/Render evidence after merge, if deployment authority is
  granted;
- browser evidence for the hosted owner-authenticated dashboard surfaces needed
  to rerun WO-058.

WO-062 completes only when the hosted dashboard can produce real runtime
evidence for the WO-058 checklist without using fixture-only operational paths
or exposing sensitive values.

## 7. Rollback Expectations

Rollback must preserve backend contracts, database state, provider credentials,
and hosted migration state. If the dashboard integration is unsafe or unusable,
revert or disable the affected dashboard runtime routes, return release-critical
pages to a clearly blocked state, and keep WO-058 blocked. Do not hide a failed
runtime integration behind fictional fixture evidence.

## 8. Stop-and-Ask Triggers

Stop before:

- exposing any server-side signing secret, provider credential, OAuth code,
  token, database URL, owner subject, or raw log content;
- allowing unauthenticated public browser traffic to trigger signed runtime
  API calls;
- changing Google OAuth scopes, Google clients, Render/Netlify provider
  configuration, production secrets, database schema, deployment topology, or
  monitoring architecture outside this scope;
- using production mailbox content, personal mailbox content, or non-synthetic
  provider data to fill evidence gaps;
- weakening approval, idempotency, CSRF/session, authorization, audit, or
  suppression guarantees;
- starting WO-059 or WO-060 before WO-062 is accepted, implemented, deployed,
  and WO-058 is rerun successfully.

## 9. Rerun Gate for WO-058

After WO-062 is implemented and deployed, rerun WO-058 with synthetic-only
evidence. WO-059 and WO-060 remain blocked until WO-058 records successful
hosted owner-session, connector health, run, approval/draft state, audit/log,
and monitoring evidence through the integrated hosted dashboard.

## 9.1 Rerun Result

WO-062 was implemented, merged, deployed, and authenticated browser-verified on
2026-07-22. Connectors, Runs, Approvals, Audit, and Alerts now render live
runtime states through the owner-authenticated dashboard facade.

WO-058 remains blocked by a narrower runtime seed / connector configuration
gap: Gmail and Google Drive are visible as live runtime descriptors but are not
connected, health checks are disabled until connector OAuth exists, the live
Runs page has no synthetic manual-run seed, and the live Approvals page has no
synthetic approval state.

Next remediation scope:
[WO-063 Hosted Runtime Smoke Seed and Synthetic Connector Enablement](./063-hosted-runtime-smoke-seed-and-synthetic-connector-enablement.md).
