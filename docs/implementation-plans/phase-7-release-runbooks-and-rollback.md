# Phase 7 Release Runbooks and Rollback

**Status:** Implemented - Pending Review
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Work Order:** [WO-050](../work-orders/050-release-runbooks-and-rollback.md)
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)

---

## 1. Purpose

Define the operator runbooks and rollback procedures required before the Atlas
Gmail Agent MVP can be released for normal single-owner operation.

These runbooks are checklists and decision paths. They do not authorize
production deployment, live Google credentials, production database access,
destructive provider actions, or release tagging by themselves.

## 2. Release Preparation Runbook

1. Confirm `main` is synchronized and clean.
2. Confirm all accepted Phase 7 Work Orders required for the release candidate
   are merged.
3. Confirm required GitHub CI checks passed on the latest `main`.
4. Confirm local validation evidence is current for backend, frontend,
   migrations, security/privacy scans, and release-readiness dry-run checks.
5. Confirm ES-007 residual risks are resolved, deferred, or queued for WO-052
   decision.
6. Confirm no `.env`, provider secrets, OAuth tokens, production database URLs,
   full Gmail bodies, clinical content, PHI, or unrestricted attachment copies
   are committed.
7. Confirm deployment authority, controlled-account authority, and release
   authority are explicitly documented before taking any live action.

## 3. Deployment Verification Runbook

Pre-deployment:

- Verify the intended commit SHA.
- Verify the intended environment.
- Verify `NEXT_PUBLIC_` values contain only browser-safe configuration.
- Verify backend production-like readiness variables are configured through
  provider-native secret storage.
- Verify a database backup or provider recovery point exists before production
  migration.

Post-deployment:

- Check `/health/live`.
- Check `/health/ready`.
- Confirm the dashboard loads against the intended API base URL.
- Confirm connector status, run status, approvals, held messages, and audit
  surfaces are reachable.
- Run an approved smoke scenario using fake or controlled data only.
- Record commit, environment, timestamps, health results, and known issues.

## 4. Controlled-Account Runbook

Before execution:

- Confirm explicit controlled-account authorization.
- Confirm the account contains only synthetic seed data.
- Confirm accepted Google scopes remain `gmail.modify` and `drive.file`.
- Confirm no personal or production mailbox is in scope.
- Confirm cleanup responsibility and timing.

During execution:

- Run only the approved seed scenarios.
- Do not persist full message bodies or attachment contents as evidence.
- Record provider behavior differences as minimized notes.
- Stop if broader scopes, personal data, clinical content, PHI, or unexpected
  provider side effects appear.

After execution:

- Remove or quarantine seeded Gmail messages.
- Remove or quarantine seeded Drive files and folders.
- Revoke or rotate test OAuth grants if required.
- Record cleanup evidence without secrets or full content.

## 5. Gmail OAuth Revocation Runbook

Use when a Gmail or Google Drive connection is revoked intentionally, expires,
or is suspected of exposure.

1. Mark the connector connection unhealthy or revoked in Atlas if not already
   reflected.
2. Revoke the Google OAuth grant through the controlled account or provider
   console.
3. Revoke or rotate the OAuth client secret if exposure is suspected.
4. Confirm Atlas no longer treats the connector as operation-authorized.
5. Record audit/review evidence with reason codes only.
6. Reconnect only through the approved OAuth flow and accepted scopes.

## 6. Drive Cleanup Runbook

Use for controlled-account or release smoke data cleanup.

1. Identify app-created or test-shared Drive folders/files by approved test
   naming convention.
2. Confirm no personal or production files are included.
3. Remove or quarantine test files.
4. Confirm references in Atlas are either expected historical records or
   explicitly marked as no-longer-provider-accessible.
5. Record cleanup evidence without file contents or sensitive names.

## 7. Migration Rollback Runbook

Before production migration:

- Confirm backup/recovery point.
- Confirm current Alembic head.
- Confirm target Alembic head.
- Confirm application commit compatibility.
- Confirm rollback owner and decision path.

If migration fails:

1. Stop promotion.
2. Preserve logs without printing database URLs.
3. Identify the failed revision and partial state.
4. Prefer a corrective forward migration when safe.
5. Restore from backup only after validating data impact.
6. Do not assume application rollback reverses schema or data changes.

## 8. Deployment Rollback Runbook

Frontend rollback:

- Use Netlify deployment rollback or corrective deploy.
- Verify browser-safe environment variables remain correct.
- Confirm dashboard can still reach the intended API environment.

Backend rollback:

- Use Render previous deploy rollback or corrective deploy.
- Confirm `/health/live` and `/health/ready`.
- Confirm migrations remain compatible with the rolled-back application.
- Stop if database rollback is required but no backup/restore decision exists.

Release tags:

- Do not move or rewrite release tags.
- If a release must be withdrawn, publish a corrective release or reviewed
  revert.

## 9. Incident Triage Runbook

1. Identify the affected environment, commit, run ID, correlation ID, and
   timeframe.
2. Determine whether the incident is configuration, deployment, migration,
   connector, provider, webhook, approval, suppression, or data related.
3. Check audit records before logs when accountability matters.
4. Check logs for safe reason codes and correlation IDs.
5. Avoid retrying external side effects until idempotency and prior outcome are
   known.
6. Record user-visible impact, recovery action, and residual risk.

## 10. Indeterminate Send Runbook

1. Stop automated continuation for the affected source/draft.
2. Inspect Atlas send outcome and audit records.
3. Manually inspect the Gmail controlled or production account, if authorized.
4. Record whether the message was sent, failed, duplicated, or remains unknown.
5. Do not retry blindly.
6. Resume only after the exact source, draft, approval, and facts-used state is
   reconciled.

## 11. Provider Outage Runbook

1. Mark affected connector behavior as degraded or unhealthy.
2. Pause scheduled runs if repeated provider failures occur.
3. Continue dashboard/API reconciliation from Atlas records.
4. Do not treat webhook delivery as authoritative.
5. Retry only idempotent operations after provider recovery.
6. Record outage timeframe, provider symptoms, affected runs, and recovery
   result.

## 12. Release Withdrawal Runbook

Use when MVP release candidate validation fails or an accepted MVP release must
be withdrawn.

1. Record the blocker or withdrawal reason.
2. Stop production promotion or pause production runs if already released.
3. Keep release tags immutable.
4. Open a corrective Work Order or reviewed revert.
5. Run required validation again after correction.
6. Update WO-052 residual-risk and release decision records.

## 13. Safety Rules

- Never print or paste real secret values into runbook evidence.
- Never use personal mailbox data as test evidence.
- Never approve clinical/PHI suppression override.
- Never blindly retry an indeterminate external action.
- Never treat application rollback as database rollback.
- Never move release tags.
