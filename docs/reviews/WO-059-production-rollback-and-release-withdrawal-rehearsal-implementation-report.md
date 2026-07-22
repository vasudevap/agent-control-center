# WO-059 Production Rollback and Release Withdrawal Rehearsal Report

**Work Order:** [WO-059](../work-orders/059-production-rollback-and-release-withdrawal-rehearsal.md)
**Status:** Completed - Non-Destructive Rehearsal Recorded
**Date:** 2026-07-22
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)

## Summary

WO-059 dry-reviewed the approved production rollback and release-withdrawal
paths after the successful synthetic-only WO-058 hosted smoke rerun. The
rehearsal confirms the responsible operator, evidence required before each
decision, recovery order, and stop-and-ask boundaries without changing a
provider deployment, database, credential, OAuth grant, provider artifact,
Git tag, or release state.

## Preconditions Confirmed

| Gate | Evidence | Result |
| --- | --- | --- |
| Hosted smoke | WO-058 passed after WO-063 supplied owner-authenticated synthetic connector, run, approval, audit, and monitoring evidence. | Confirmed |
| Rollback runbook | [Phase 7 release runbooks and rollback](../implementation-plans/phase-7-release-runbooks-and-rollback.md) defines deploy, migration, OAuth, Drive cleanup, and withdrawal procedures. | Confirmed |
| Database recovery path | WO-057 records paid Render PostgreSQL PITR and isolated recovery as the preferred restore path; in-place restore remains unauthorized. | Confirmed |
| Release controls | [Release management](../governance/release-management.md) requires immutable tags and a reviewed revert or corrective-forward release. | Confirmed |

## Rehearsal Results

| Scenario | Authorized response sequence | Evidence before proceeding | Live action performed |
| --- | --- | --- | --- |
| Frontend regression | Select a known-good Netlify deploy through provider rollback control; verify the intended API origin and rerun dashboard and readiness smoke checks. | Incident reason, affected deploy, selected known-good deploy, post-rollback smoke result. | No |
| API regression | Use a Render previous-deploy rollback or corrective deploy; verify liveness, readiness, migration compatibility, and dashboard-to-API behavior. | Affected commit/deploy, health evidence, migration compatibility review, post-action smoke result. | No |
| Migration/data issue | Stop promotion; preserve sanitized failure evidence; prefer a reviewed corrective-forward migration. If restore is necessary, create and validate an isolated Render recovery database before any service redirection. | Failed revision/partial-state assessment, backup or recovery reference, data-impact review, maintainer authorization for restore or service redirection. | No |
| Suspected OAuth exposure or connector cleanup | Mark the affected connection unhealthy or revoked in Atlas, revoke the Google grant, rotate a client secret only if exposure requires it, and record reason-code-only audit evidence. | Exact account and connector scope, exposure assessment, maintainer authorization, provider cleanup result. | No |
| Synthetic Gmail/Drive artifact cleanup | Identify only approved app-created synthetic artifacts, verify no personal or production data is in scope, remove or quarantine them, then record minimized evidence. | Approved naming/identification evidence, data-scope confirmation, cleanup owner and result. | No |
| Release withdrawal | Record the reason, stop promotion or pause runs if applicable, keep tags immutable, open a corrective Work Order or reviewed revert, rerun validation, and update release decision records. | Withdrawal reason, impact assessment, approved corrective path, validation result, residual risk. | No |

## Decision and Escalation Boundaries

- Application rollback is not database rollback; application and schema/data
  recovery require separate evidence and decisions.
- A release tag must never be moved, reused, or rewritten. Withdrawal uses a
  corrective release or reviewed revert.
- Any live deployment rollback, production restore, service environment change,
  OAuth grant revocation, credential rotation, Gmail/Drive artifact deletion,
  provider-resource deletion, tag action, or release withdrawal requires
  explicit Repository Maintainer authority at action time.
- Evidence must remain metadata-only and must not contain provider tokens,
  secrets, database URLs, owner-subject values, raw logs, Gmail content, or
  Drive content.

## Completion Evidence

This dry-review used the following canonical records:

- [WO-050 release runbooks and rollback report](WO-050-release-runbooks-and-rollback-implementation-report.md)
- [WO-054 Netlify deployment report](WO-054-netlify-frontend-deployment-implementation-report.md)
- [WO-055 Render API and PostgreSQL deployment report](WO-055-render-api-and-postgresql-deployment-implementation-report.md)
- [WO-057 migration, backup, and restore report](WO-057-hosted-migration-backup-and-restore-readiness-implementation-report.md)
- [WO-058 hosted smoke report](WO-058-hosted-smoke-tests-and-monitoring-confirmation-implementation-report.md)

The reviewed Netlify recovery procedure is provider-native deploy rollback;
the reviewed Render recovery procedure is provider-native service rollback or
corrective deployment. The reviewed database recovery procedure is a
corrective-forward migration where safe, otherwise isolated PITR or logical
export recovery followed by explicit approval before service redirection.

## Validation

```text
git diff --check
rg -n "(sk-[A-Za-z0-9]{20,}|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\\s*=|refresh_token|access_token|postgresql://[^<]|postgresql\\+psycopg://[^<])" docs/work-orders/059-production-rollback-and-release-withdrawal-rehearsal.md docs/implementation-plans/hosted-production-cutover-work-order-backlog.md docs/reviews/WO-059-production-rollback-and-release-withdrawal-rehearsal-implementation-report.md
```

No source code or dependency changes are part of WO-059. The full source CI
suite is therefore not applicable to this documentation-only rehearsal. The
next source-bearing Work Order must follow the GitHub Actions free-tier
discipline: focused local checks while iterating, followed by the full local
CI-equivalent suite before one consolidated push.

## Final Disposition

WO-059 is complete as the accepted, non-destructive rehearsal required before
go/no-go. [WO-060](../work-orders/060-release-tag-and-production-closeout.md)
is now dependency-ready, but it remains an explicit Repository Maintainer
decision gate for go/no-go and any optional annotated release-tag authority.
