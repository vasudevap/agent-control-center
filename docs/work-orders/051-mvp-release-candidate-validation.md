# Work Order 051: MVP Release Candidate Validation

**Status:** Implemented - Pending PR Review
**Work Order ID:** WO-051
**Type:** Release candidate verification
**Implementation Authorization:** Granted under ADP-004 on 2026-07-18
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)
**Governing Plan:** [Phase 7 Work Order Backlog](../implementation-plans/phase-7-work-order-backlog.md)
**Prerequisites:** WO-045 through WO-050 completed or explicitly deferred
**Review Record:** [WO-051 MVP Release Candidate Validation Report](../reviews/WO-051-mvp-release-candidate-validation-report.md)

## 1. Purpose

Run the final release candidate evidence suite and produce the MVP release
candidate validation report.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Evidence scope | Local validation, CI, migration, security/privacy, dashboard, fake-provider, and authorized controlled-account evidence |
| Release posture | Validation does not itself approve release |
| Known issues | Must be disclosed and triaged |
| Residual risk | Must be ready for maintainer acceptance or rejection |

## 3. Approved Scope if Accepted

- Run full backend validation, frontend validation for touched dashboard
  surfaces, lint/typecheck/build, migration-head verification, fake-provider
  Gmail E2E tests, redaction/secret scans, and controlled-account checks if
  authorized.
- Verify release-critical runbooks and rollback checklists are complete.
- Confirm GitHub CI status for the release candidate branch or PR.
- Produce a release candidate validation report with evidence, known issues,
  limitations, and release recommendation.

## 4. Explicitly Out of Scope

Release tagging, production deployment, production mailbox use, public launch,
new feature implementation, and acceptance of residual risk are excluded.

## 5. Verification and Completion

Completion is the release candidate validation report under `docs/reviews/`
with command results, CI evidence, migration status, security/privacy checks,
dashboard evidence, controlled-account disposition, and known issue triage.

## 6. Rollback Expectations

Rollback is not expected to mutate production resources. If validation exposes
a blocker, the release candidate is rejected or corrected through a new Work
Order or in-scope fix before WO-052.

## 7. Stop-and-Ask Triggers

Stop before suppressing a failing required check, ignoring a safety/privacy
blocker, using production data to fill evidence gaps, tagging a release, or
claiming MVP acceptance without maintainer decision.
