# WO-058 Hosted Smoke Tests and Monitoring Confirmation Report

**Work Order:** [WO-058](../work-orders/058-hosted-smoke-tests-and-monitoring-confirmation.md)
**Status:** Blocked - Cutover Stopped
**Date:** 2026-07-21
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Summary

WO-058 performed the authorized, non-destructive hosted smoke checks. The
Grafley dashboard renders, its runtime indicator reports ready, and the hosted
API reports healthy and configuration-ready. Final-domain CORS and the safe
OAuth-denial path also work.

The Work Order cannot complete: the deployed dashboard's operational pages are
explicitly session-only fictional prototypes. They do not use the hosted API
for owner authentication, connector OAuth/health, manual runs, approvals,
audit history, logs, or alerts. The required real workflow evidence therefore
cannot be generated or inspected through the approved dashboard boundary.

No Gmail or Drive data was read, searched, created, changed, or deleted. No
OAuth consent was submitted. No provider configuration, deployment, migration,
rollback, credential, or production data change was made.

## Evidence Collected

| Area | Check | Result |
| --- | --- | --- |
| Dashboard | `https://atlas.grafley.com/` browser smoke | Rendered the Atlas dashboard shell and its `RUNTIME READY` indicator. |
| API liveness | `GET https://api.atlas.grafley.com/health/live` | `status=ok`, `service=atlas-api`, `environment=production`. |
| API readiness | `GET https://api.atlas.grafley.com/health/ready` | `status=ready`; configuration check `ok`; no problem codes. |
| API health | `GET https://api.atlas.grafley.com/api/v1/health` | `status=ok`; a response correlation ID was returned. |
| Browser CORS | `OPTIONS /health/ready` with origin `https://atlas.grafley.com` | `200`; allows `GET` from the final dashboard origin. |
| OAuth denial | `GET https://atlas.grafley.com/oauth/google/callback?error=access_denied` | `307` to the minimized `connectors?oauth=google&status=denied` result. |
| Callback boundary | Unauthenticated `POST /api/v1/connectors/oauth/google/callback` | `401`, confirming the external-client boundary remains enforced. |

All endpoint evidence was limited to status, service, readiness state, stable
problem codes, headers, and correlation identifiers. No secret, token, subject,
authorization code, message body, or provider content was recorded.

## Blocking Evidence

Browser inspection of the deployed `https://atlas.grafley.com/connectors` page
displayed this product boundary: its connector registry is a frontend prototype
using fictional descriptors and session-only actions, and it states that no
OAuth, provider, token, credential, secret, or connection service exists.

Repository source matches the hosted behavior:

- `apps/web/src/app/(shell)/connectors/connectors-workspace.tsx` declares the
  frontend-prototype and session-only connector boundary.
- `apps/web/src/app/(shell)/runs/runs-workspace.tsx` declares fictional local
  run fixtures and no runtime/service contact.
- `apps/web/src/app/(shell)/audit/audit-workspace.tsx` declares fictional audit
  examples.
- `apps/web/src/app/(shell)/alerts/alerts-workspace.tsx` declares local,
  fictional alert evidence.

Consequently, the following required WO-058 checks are unavailable:

| Required check | Disposition |
| --- | --- |
| Owner session | Blocked: no hosted owner-session UI boundary is exposed. |
| Gmail/Drive connector health | Blocked: no real connector connection can be started or inspected from the deployed dashboard. |
| Synthetic Gmail/Drive workflow | Not run: the dashboard cannot invoke a real run and using an alternate direct API path would require unavailable external-client credentials. |
| Manual run and approval/draft state | Blocked: deployed Run and Approval pages are session-only fixtures. |
| Audit and log signals | Blocked: deployed Audit and Alerts pages are fictional fixture views; no authenticated runtime event exists to correlate safely. |
| Owner monitoring confirmation | Blocked: monitoring views do not represent runtime data. |

## Required Next Authority

This is not a provider, DNS, migration, or secret configuration defect. It
requires an accepted engineering scope to integrate the hosted dashboard with
the existing authenticated API contracts (or to define another approved
owner-facing operational surface), including real read-only status, controlled
connector actions, manual-run/approval evidence, audit visibility, and safe
monitoring/log correlation. That scope must include security review of the
owner and external-client boundary before it can be implemented.

After that work is deployed, rerun WO-058 with a synthetic-only Gmail/Drive
workflow and minimized evidence. WO-059 and WO-060 remain blocked by this
failed smoke gate.

## Rerun After WO-062 - 2026-07-22

WO-062 was implemented, merged, deployed, and followed by two production
follow-up fixes before rerunning this smoke gate:

- PR #105 implemented the owner-authenticated dashboard facade and web runtime
  integration.
- PR #106 fixed production API session-factory wiring so dashboard facade
  routes can use the configured hosted database.
- PR #107 fixed the authenticated Connectors page adapter for the hosted
  connector descriptor shape.

Post-merge evidence:

| Area | Check | Result |
| --- | --- | --- |
| Main CI | GitHub Actions run `29889387816` for `main@3ce58c8` | Passed; Validate completed in 3m6s. |
| Netlify production deploy | Deploy `6a603d84c07e05000871e659` | Ready; `context=production`; `commit_ref=3ce58c8e1507540408d3b2c57069273cce1e39d3`; published 2026-07-22T03:49:12.943Z. |
| Netlify secret scan | Deploy validation report `6a603db092d2f45f649f55bc` | No classic or enhanced secret-scan matches. |
| API readiness | `GET https://api.atlas.grafley.com/health/ready` | `status=ready`; configuration check `ok`; no problems. |
| Unauthenticated session boundary | `GET https://api.atlas.grafley.com/api/v1/dashboard/session` without owner cookie | `401 owner_session_missing`, confirming the facade fails closed outside the owner session. |
| Owner sign-in | Chrome owner login with Google account selected by Repository Maintainer | Redirected to `https://atlas.grafley.com/connectors?owner_session=signed_in`. |
| Dashboard shell | Browser smoke at `https://atlas.grafley.com/` | Rendered `RUNTIME READY`. |
| Connectors | `https://atlas.grafley.com/connectors` after owner sign-in | Rendered `Live runtime`; showed Gmail and Google Drive runtime descriptors; no page error. |
| Runs | `https://atlas.grafley.com/runs` after owner sign-in | Rendered `Live runtime`; showed `0 of 0 runtime runs`; no manual-run control. |
| Approvals | `https://atlas.grafley.com/approvals` after owner sign-in | Rendered `Live runtime`; showed no pending runtime approval requests. |
| Audit | `https://atlas.grafley.com/audit` after owner sign-in | Rendered `Live runtime`; showed 11 metadata-only runtime audit events. |
| Alerts / monitoring | `https://atlas.grafley.com/alerts` after owner sign-in | Rendered `Live runtime`; showed runtime-readiness monitoring evidence and no active readiness blockers. |

No Gmail or Drive mailbox data was read, searched, created, changed, or
deleted. No connector OAuth consent was submitted during this rerun. No
provider token, OAuth code, secret, owner subject, raw log, or mailbox content
was recorded.

## Current Blocking Evidence - 2026-07-22

WO-062 resolved the earlier dashboard-to-runtime blocker, but the WO-058 smoke
gate still cannot pass:

| Required check | Disposition |
| --- | --- |
| Owner session | Passed: owner sign-in completed and live runtime pages no longer show the unauthenticated gate. |
| Gmail/Drive connector health | Blocked: Gmail and Google Drive are visible as runtime descriptors, but both are `Offline` / `Not connected`; `Run health check` controls are disabled until connector OAuth exists. |
| Synthetic Gmail/Drive workflow | Blocked: no Gmail/Drive connector connection exists, and no synthetic runtime agent/manual-run seed is exposed. |
| Manual run evidence | Blocked: live Runs reports `0 of 0 runtime runs` and exposes no manual-run action. |
| Approval/draft state | Blocked: live Approvals reports no pending runtime approval requests; no synthetic approval state exists to inspect. |
| Audit and log signals | Partially passed: metadata-only runtime audit events are visible, but no synthetic run/approval action exists to correlate. |
| Owner monitoring confirmation | Passed: live monitoring shows hosted runtime readiness evidence. |

The cutover remains stopped. WO-059 and WO-060 remain blocked until a governed
runtime smoke seed / synthetic connector enablement scope is accepted,
implemented, deployed, and WO-058 is rerun successfully.

Proposed remediation scope:
[WO-063 Hosted Runtime Smoke Seed and Synthetic Connector Enablement](../work-orders/063-hosted-runtime-smoke-seed-and-synthetic-connector-enablement.md).
