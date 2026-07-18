# Phase 7 Dashboard Runtime Operations Readiness

**Status:** Implemented - Pending Review
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Work Order:** [WO-046](../work-orders/046-dashboard-productization-and-runtime-operations.md)
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)

---

## 1. Purpose

Record the MVP dashboard runtime-readiness boundary for single-owner operation.

The browser dashboard may call browser-safe endpoints such as `/health/ready`.
It must not receive external-client HMAC secrets or provider credentials to
call signed operational APIs directly.

## 2. Implemented Dashboard Runtime Signal

The shell status strip now includes a runtime health indicator driven by
`NEXT_PUBLIC_API_BASE_URL`:

| State | Trigger | Operator meaning |
| --- | --- | --- |
| Runtime not configured | `NEXT_PUBLIC_API_BASE_URL` absent or blank | Dashboard build is local/static and cannot prove backend readiness |
| Checking runtime | Readiness request in flight | Dashboard is checking the configured Atlas API |
| Runtime ready | `/health/ready` returns `status: ready` | Backend reports release-critical configuration is ready |
| Runtime not ready | `/health/ready` returns `status: not_ready` | Backend reports stable readiness problem codes |
| Runtime unavailable | Request fails, non-2xx response, or unexpected payload | Backend is unreachable or not serving the readiness contract |

The indicator displays problem counts only. It does not expose readiness problem
values, secrets, database URLs, OAuth values, or provider details in the shell.

## 3. Fixture Quarantine

MVP-critical dashboard surfaces remain separated into two categories:

| Surface | Current release-readiness treatment |
| --- | --- |
| Shell runtime status | Browser-safe real `/health/ready` integration |
| Agents, runs, approvals, held messages, questions, audit, connectors | Existing fixture/productized UI remains visibly non-authoritative until secure owner-session API wiring is accepted |
| High-risk approval actions | Must not call signed external-client APIs from the browser using embedded secrets |
| Gmail/Drive provider state | Must remain backend/connector authoritative |

This is the safe productization boundary for WO-046. Replacing every fixture
surface with live API data requires a browser-safe owner session/API integration
that does not expose HMAC or provider secrets.

## 4. Required Future Dashboard Work

Before MVP release can claim fully live dashboard operation, a later accepted
dashboard/API Work Order must provide:

- browser-safe owner-session API access for operational routes;
- loading, empty, stale, unauthorized, and retry states for live data surfaces;
- mutation flows for manual run, approval decisions, question answers, and
  connector lifecycle that do not bypass backend authorization;
- integration tests against API contract fixtures or test server responses;
- browser evidence for desktop and mobile critical states.

## 5. Stop Conditions Preserved

- Do not place `ATLAS_API_EXTERNAL_CLIENT_SECRET` or webhook signing secrets in
  `NEXT_PUBLIC_` variables.
- Do not call signed external-client routes directly from browser code unless a
  safe owner-session bridge is accepted.
- Do not hide fixture-only surfaces behind language that implies live system of
  record behavior.
- Do not weaken clinical/PHI suppression, approval gates, audit, or connector
  authority in the dashboard.
