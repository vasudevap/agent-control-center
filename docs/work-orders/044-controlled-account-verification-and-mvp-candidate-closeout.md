# Work Order 044: Controlled-Account Verification and MVP Candidate Closeout

**Status:** Accepted - Implementation Authorized
**Work Order ID:** WO-044
**Type:** Integration verification and governance closeout
**Implementation Authorization:** Granted under ADP-003 on 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing Plan:** [Phase 6 Work Order Backlog](../implementation-plans/phase-6-work-order-backlog.md)
**Prerequisites:** WO-036 through WO-043 completed and merged

## 1. Purpose

Verify the Gmail Agent MVP Candidate as one coherent governed workflow using
fake-provider automation and explicitly authorized controlled-account evidence,
then produce closeout, residual-risk, and release-readiness records.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Primary evidence | Deterministic fake-provider end-to-end tests |
| Controlled account | Allowed only if separately authorized by Repository Maintainer |
| Personal mailbox | Not authorized |
| Production release | Not authorized |
| Closeout | Must state whether Gmail Agent is ready for a release decision |

## 3. Approved Scope if Accepted

- End-to-end fake-provider verification across OAuth boundary, eligibility,
  classification, suppression, low-risk actions, ask-instead-of-guess, draft,
  approval, send continuation, webhooks, audit, and run status.
- Security and privacy negative tests for credentials, redaction, clinical/PHI
  suppression, approval fail-closed behavior, and prohibited-content exclusion.
- Controlled Gmail account test plan, seed data set, execution evidence, and
  cleanup checklist if live controlled-account use is explicitly authorized.
- Documentation/status/index updates.
- Phase 6 closeout report with residual risks and MVP candidate checklist.

## 4. Explicitly Out of Scope

Personal mailbox testing, production mailbox testing, production release,
production OAuth verification, broad load testing, chaos testing, live webhook
receivers, infrastructure provisioning, dashboard productization, and new
product capability are excluded.

## 5. Verification and Completion

Require the full backend test suite, Gmail fake-provider end-to-end tests,
suppression and redaction negatives, OAuth/token secret scan, migration checks,
frontend checks if touched, GitHub CI, controlled-account evidence only if
authorized, cleanup evidence, and a closeout report under `docs/reviews/`.

## 6. Rollback Expectations

Rollback must leave no live test credentials, tokens, message bodies, clinical
content, PHI, or uncontrolled attachment copies in the repository or local
fixtures. Controlled-account cleanup must remove or quarantine test data
according to the accepted test plan.

## 7. Stop-and-Ask Triggers

Stop before using a personal mailbox, adding production credentials, running
against a live controlled account without explicit authorization, retaining live
message bodies, weakening privacy checks, skipping cleanup evidence, or
claiming production release readiness.
