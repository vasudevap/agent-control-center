# Work Order 045: Controlled-Account Release Verification

**Status:** Controlled Evidence Complete - Pending PR Review
**Work Order ID:** WO-045
**Type:** Release-readiness verification
**Implementation Authorization:** Granted under ADP-004 on 2026-07-18
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)
**Governing Plan:** [Phase 7 Work Order Backlog](../implementation-plans/phase-7-work-order-backlog.md)
**Prerequisites:** WO-044 completed and ES-007 accepted
**Review Record:** [WO-045 Release Verification Report](../reviews/WO-045-controlled-account-release-verification-report.md)

## 1. Purpose

Execute the WO-044 controlled-account test plan if explicitly authorized, or
record a maintainer-accepted deferral before release candidate validation.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Personal mailbox | Not authorized |
| Production mailbox | Not authorized |
| Controlled account | Requires explicit Repository Maintainer authorization |
| Test data | Synthetic messages only |
| Provider evidence | Must be cleaned up and summarized without storing sensitive message bodies |

## 3. Approved Scope if Accepted

- Confirm controlled-account authorization before any live provider call.
- Execute the prepared WO-044 controlled-account seed, run, verification, and
  cleanup checklist.
- Capture provider behavior differences that fake providers did not cover.
- Record cleanup evidence, revoked credentials if applicable, residual risks,
  and any required Work Order revisions.
- If authorization is not granted, record the explicit deferral and the risk it
  creates for MVP release.

## 4. Explicitly Out of Scope

Personal mailbox testing, production mailbox testing, unrestricted mailbox
scans, full message-body evidence, production OAuth clients, public launch,
provider verification for multiple users, and production release are excluded.

## 5. Verification and Completion

Require fake-provider baseline tests, controlled-account evidence only if
authorized, cleanup evidence, credential/token redaction checks, and a readiness
report under `docs/reviews/`.

## 6. Rollback Expectations

Rollback must revoke or delete test OAuth grants, remove or quarantine seeded
messages and Drive files, leave no token material in source or fixtures, and
document any provider side effects that cannot be undone.

## 7. Stop-and-Ask Triggers

Stop before using any live account without explicit authorization, using a
personal or production mailbox, retaining full message bodies, requesting
broader scopes, skipping cleanup, or treating controlled-account success as
production release approval.
