# Work Order 054: Netlify Frontend Deployment

**Status:** Proposed - Pending Acceptance
**Work Order ID:** WO-054
**Type:** Frontend hosting cutover
**Implementation Authorization:** Not granted
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-053 environment map accepted
**Review Record:** TBD

## 1. Purpose

Deploy the Atlas web dashboard to Netlify using the accepted frontend build and
runtime configuration.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Provider | Netlify frontend |
| Build | Existing web workspace build contract |
| API binding | `NEXT_PUBLIC_API_BASE_URL` points to the accepted hosted API |
| Rollback | Use Netlify deploy rollback, not Git history rewriting |

## 3. Approved Scope if Accepted

- Configure Netlify project settings, build command, publish path, and
  environment variables.
- Deploy the frontend from the reviewed source state.
- Verify dashboard render, static routes, runtime health indicator, and
  browser smoke evidence.
- Record rollback target and previous-deploy recovery path.

## 4. Explicitly Out of Scope

Backend deployment, database migration, production launch announcement,
frontend redesign, multi-user UI, and release tagging are excluded.

## 5. Verification and Completion

Require local frontend tests/typecheck/lint/build, Netlify deploy evidence,
hosted browser smoke evidence, runtime-health evidence, rollback evidence, and
an implementation report under `docs/reviews/`.

## 6. Rollback Expectations

Rollback uses Netlify provider rollback to a known-good deploy and does not
move Git tags or hide API/backend failures.

## 7. Stop-and-Ask Triggers

Stop before exposing frontend environment values that are not public, changing
hosting providers, deploying from an unreviewed source state, or publishing
production URLs as launched without WO-060 authority.
