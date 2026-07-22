# Work Order 060: Release Tag and Production Closeout

**Status:** Approved for Hosted MVP Cutover - Tag Pending Main Verification
**Work Order ID:** WO-060
**Type:** Production go/no-go and closeout
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-19; final go/no-go, documented residual-risk acceptance, and `v0.3.0-alpha.1` tag authority recorded by Repository Maintainer on 2026-07-22
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-058 and WO-059 complete
**Review Record:** [WO-060 release tag and production closeout report](../reviews/WO-060-release-tag-and-production-closeout-readiness-report.md)

## 1. Purpose

Record the final hosted MVP go/no-go decision, optional release-tag authority,
hosted URLs, validation evidence, residual risks, and ADP-005 closeout.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Go/no-go | Repository Maintainer makes explicit decision |
| Release tag | Created only if explicitly authorized |
| Source of truth | Git remains technical source of truth |
| Phase transition | Phase 8 requires new authority |
| Final frontend URL | `https://atlas.grafley.com`, unless WO-056A records an accepted deferment |
| Final API URL | `https://api.atlas.grafley.com`, unless WO-056A records an accepted deferment |

## 3. Approved Scope if Accepted

- Review WO-053 through WO-059 evidence.
- Record go/no-go decision and residual-risk disposition.
- If explicitly authorized, create an annotated immutable release tag at the
  verified commit and push it.
- Record hosted URLs, including final Grafley custom domains or an accepted
  deferment, rollback posture, monitoring posture, and post-cutover follow-ups.
- Close ADP-005.

## 4. Explicitly Out of Scope

Deploying new changes, changing scope, broad public launch, moving tags,
starting Phase 8, multi-user operation, and accepting undisclosed risks are
excluded.

## 5. Verification and Completion

Require complete cutover evidence, CI evidence, hosted smoke evidence,
rollback evidence, residual-risk decision, optional tag verification if
authorized, and a closeout report under `docs/reviews/`.

## 6. Rollback Expectations

If go/no-go is rejected or release is withdrawn, publish a corrective forward
record or reviewed revert and follow WO-059 rollback/withdrawal procedures.

## 7. Stop-and-Ask Triggers

Stop before tagging without explicit authority, moving tags, claiming public
launch, hiding residual risk, starting Phase 8, or deploying unreviewed source.
