# Work Order 063: Hosted Runtime Smoke Seed and Synthetic Connector Enablement

**Status:** Source Implemented - Pending Hosted Deployment and WO-058 Rerun
**Work Order ID:** WO-063
**Type:** Hosted runtime smoke unblocker
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-22
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-062 deployed and authenticated runtime dashboard evidence captured; WO-058 rerun blocker recorded
**Review Record:** [WO-063 Implementation Report](../reviews/WO-063-hosted-runtime-smoke-seed-and-synthetic-connector-enablement-implementation-report.md)

## 1. Purpose

Resolve the remaining WO-058 smoke blocker by providing a safe,
synthetic-only hosted runtime path that can produce connector-health,
manual-run, approval/draft, audit/log, and monitoring evidence without using
production mailbox content or pretending fixture-only UI state is runtime
evidence.

WO-062 connected the dashboard to the runtime. WO-063 creates or provisions the
minimal runtime state needed for the hosted smoke gate to execute safely.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Evidence data | Synthetic only; no production mailbox scans, broad provider extraction, or personal mailbox content. |
| Connector credentials | Do not create, store, revoke, or refresh live provider tokens unless the Repository Maintainer explicitly authorizes the exact connector account and OAuth consent step during implementation. |
| Runtime seed | Prefer deterministic hosted seed records and no-op/synthetic runtime execution over real provider actions when that can satisfy WO-058 evidence. |
| Browser boundary | The dashboard remains owner-authenticated and must not receive provider tokens, OAuth codes, secrets, owner subject values, or raw logs. |
| Audit posture | Any seed, manual run, approval, connector health, or corrective-forward action must emit metadata-only audit evidence. |
| Rollback posture | Seeded smoke records must be reversible or clearly marked as synthetic smoke evidence without hiding production side effects. |

## 3. Approved Scope if Accepted

- Define the minimal hosted runtime smoke seed needed for WO-058:
  connector connection state, one synthetic manual-run-capable agent, one
  synthetic manual run path, one approval/draft state where required, and
  audit/log correlation metadata.
- Implement a safe seed or smoke-only runtime path that is explicit,
  deterministic, and environment-scoped to hosted MVP validation.
- If live Gmail/Drive OAuth is required, document the exact account, scopes,
  consent screen, credential storage boundary, cleanup path, and maintainer
  approval checkpoint before any provider consent is submitted.
- Expose enough owner-authenticated dashboard evidence to rerun WO-058:
  connector health, run list/detail, approval/draft state, audit/log
  correlation, and monitoring readiness.
- Preserve CSRF, idempotency, owner-session authorization, structured errors,
  timeout handling, and secret redaction.
- Update tests, work-order status records, implementation report, and WO-058
  rerun evidence.

## 4. Explicitly Out of Scope

Public launch, release tagging, WO-059 rollback rehearsal, WO-060 closeout,
multi-user operation, RBAC, broad provider ingestion, production mailbox
searches, personal mailbox content, changing Google OAuth scopes without a
separate accepted decision, enterprise monitoring, automated remediation,
schema changes unrelated to smoke evidence, and weakening existing
authorization/audit controls are excluded.

## 5. Security and Architecture Requirements

- Missing, expired, revoked, or invalid owner sessions must fail closed.
- Browser JavaScript must never receive provider access tokens, refresh
  tokens, OAuth codes, client secrets, external-client HMAC secrets, database
  URLs, owner subject values, or raw logs.
- Any state-changing smoke operation must require owner session, CSRF, and
  idempotency where applicable.
- Synthetic smoke state must be clearly distinguishable from production
  business records in code, API responses, audit metadata, and review reports.
- Provider OAuth consent, if required, is a stop-and-ask action with exact
  account and scope confirmation at action time.
- No smoke validation may read, summarize, quote, or mutate real Gmail or
  Drive content unless a separate Work Order explicitly authorizes that data
  use.

## 6. Verification and Completion

Require:

- API tests for hosted smoke seed behavior, authorization, idempotency,
  synthetic labeling, and audit emission;
- web tests for the live runtime states touched by the seed path;
- local lint, typecheck, tests, build, and `git diff --check`;
- focused secret/token scans across touched source and documentation files;
- post-merge CI evidence;
- hosted deployment evidence;
- browser evidence rerunning WO-058 successfully through owner-authenticated
  dashboard surfaces;
- a review report under `docs/reviews/`.

WO-063 completes only when WO-058 can be rerun successfully without using
fixture-only operational evidence or exposing sensitive values.

## 7. Rollback Expectations

Rollback must preserve provider credentials, database integrity, and hosted
dashboard availability. If a smoke seed is unsafe or misleading, revert or
disable the seed path and keep WO-058 blocked. If live provider OAuth was
explicitly authorized and used, rollback must include connector cleanup or
revocation steps approved by the Repository Maintainer.

## 8. Stop-and-Ask Triggers

Stop before:

- submitting Gmail or Drive OAuth consent;
- storing, revoking, refreshing, or deleting live provider credentials;
- reading, searching, creating, modifying, or deleting Gmail/Drive content;
- changing Google OAuth scopes, clients, redirect URIs, provider configuration,
  Render/Netlify secrets, database topology, or monitoring architecture;
- using non-synthetic data to satisfy smoke evidence;
- weakening owner-session, CSRF, idempotency, authorization, audit, or
  redaction controls;
- starting WO-059 or WO-060 before WO-058 is rerun successfully.
