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
