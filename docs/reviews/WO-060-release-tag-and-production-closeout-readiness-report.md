# WO-060 Release Tag and Production Closeout Report

**Work Order:** [WO-060](../work-orders/060-release-tag-and-production-closeout.md)
**Status:** Completed - Release Tagged
**Date:** 2026-07-22
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Release tag:** `v0.3.0-alpha.1`
**Tag object:** `e8ea8b9c31ae4bc601f48916d053acdd30fcb38a`
**Release commit:** `bf3f34d21ecbe4d794b12105bfe44707277ce75b`

## Summary

WO-060 records the final hosted MVP cutover decision after the successful
WO-058 rerun and completed WO-059 rollback and release-withdrawal rehearsal.
The Repository Maintainer accepted the standardized release-tag convention,
approved the hosted single-owner MVP cutover, accepted the documented residual
risks, and authorized `v0.3.0-alpha.1` as the immutable annotated release tag
for this milestone.

The closeout evidence was merged through PR #110. Annotated tag
`v0.3.0-alpha.1` was then created and pushed at the verified `main` merge
commit `bf3f34d21ecbe4d794b12105bfe44707277ce75b`.

No provider write, deployment, production rollback, production restore,
credential rotation, OAuth grant revocation, release withdrawal, public launch,
Gmail content access, Drive content access, secret exposure, or Phase 8
implementation was performed as part of this closeout packet.

## Cutover Evidence Reviewed

| Area | Canonical evidence | Closeout posture |
| --- | --- | --- |
| Environment and secrets | [WO-053 report](WO-053-production-environment-and-secrets-provisioning-implementation-report.md) | Provider-native Netlify and Render configuration is recorded without secret values. |
| Frontend hosting | [WO-054 report](WO-054-netlify-frontend-deployment-implementation-report.md) | Netlify production dashboard deployment and rollback path are recorded. |
| API and database hosting | [WO-055 report](WO-055-render-api-and-postgresql-deployment-implementation-report.md) | Render API and PostgreSQL targets are ready; hosted readiness later returned `ready`. |
| Custom domains | [WO-056A report](WO-056A-grafley-custom-domain-cutover-implementation-report.md) | `https://atlas.grafley.com` and `https://api.atlas.grafley.com` are the accepted final product URLs. |
| Google OAuth redirect | [WO-056 report](WO-056-google-oauth-production-client-preflight-report.md), [ADR-006](../decisions/ADR-006-browser-mediated-google-oauth-callback-surface.md) | Browser callback route decision is accepted; provider configuration is recorded in the backlog without value exposure. |
| Owner identity | [WO-061 report](WO-061-google-oidc-owner-identity-enrollment-implementation-report.md) | Owner identity enrollment and provider-side subject binding are complete without subject value exposure. |
| Migration and recovery | [WO-057 report](WO-057-hosted-migration-backup-and-restore-readiness-implementation-report.md) | Hosted Alembic current-head verification passed; restore remains authority-gated. |
| Hosted smoke and monitoring | [WO-058 report](WO-058-hosted-smoke-tests-and-monitoring-confirmation-implementation-report.md) | Final rerun passed after WO-063 with synthetic connector, run, approval, audit, and monitoring evidence. |
| Synthetic runtime seed | [WO-063 report](WO-063-hosted-runtime-smoke-seed-and-synthetic-connector-enablement-implementation-report.md) | Hosted smoke seed is owner-authenticated, CSRF-protected, idempotency-gated, and synthetic-only. |
| Rollback rehearsal | [WO-059 report](WO-059-production-rollback-and-release-withdrawal-rehearsal-implementation-report.md) | Netlify, Render, database recovery, OAuth cleanup, synthetic artifact cleanup, and release withdrawal paths were dry-reviewed. |

## Maintainer Decision

The Repository Maintainer recorded the following decision on 2026-07-22:

```text
Approve hosted single-owner MVP cutover, accept documented WO-060 residual
risks, standardize release tags as vMAJOR.MINOR.PATCH[-stage.N], and authorize
the annotated immutable release tag v0.3.0-alpha.1 after the closeout evidence
is merged to verified main.
```

This decision approves the hosted single-owner MVP cutover for the documented
ES-008 and ADP-005 boundary. It does not authorize public launch
communications, Phase 8 implementation, multi-user operation, broader Google
OAuth scopes, production mailbox content use, live rollback, production restore,
credential revocation, provider cleanup, or release-tag movement.

## Decision Gates

| Gate | Decision | Current status |
| --- | --- | --- |
| Hosted MVP go/no-go | Go for hosted single-owner MVP cutover. | Approved |
| Residual-risk disposition | Accept the documented residual risks for this milestone. | Accepted |
| Release tag | Use `v0.3.0-alpha.1` after closeout evidence is merged to verified `main`. | Created and pushed |
| Public launch boundary | Public launch communications remain out of scope. | Not authorized |
| ADP-005 closeout | Close ADP-005 once this record is merged and optional tag verification is recorded. | Completed |

## Accepted Residual Risks

| Risk / deferred item | Current mitigation | Decision |
| --- | --- | --- |
| Restore has not been rehearsed against a Render recovery instance | WO-057 prefers corrective-forward migration first; isolated PITR or logical restore requires separate restore authority. | Accepted for hosted MVP cutover; live restore remains separately authority-gated. |
| Render Recovery page screenshot/export artifact is not stored in Git | WO-057 records a non-secret PITR evidence label. | Accepted as label-only evidence for this milestone. |
| Synthetic smoke evidence does not exercise live Gmail or Drive provider content | WO-058 and WO-063 intentionally use synthetic-only, metadata-only evidence. | Accepted for hosted single-owner MVP; broader live-provider testing requires a later Work Order. |
| Tag verification evidence is recorded after tag creation | Release management requires immutable annotated tags on verified `main`. | Accepted as a post-tag evidence record; tag `v0.3.0-alpha.1` peels to the verified PR #110 merge commit. |
| Phase 8 is not authorized | ES-008 excludes Phase 8 implementation, multi-user operation, and broader public launch. | Accepted; next implementation requires new governing authority. |

## Closeout Record

| Field | Value |
| --- | --- |
| Frontend URL | `https://atlas.grafley.com` |
| API URL | `https://api.atlas.grafley.com` |
| Hosted smoke result | Passed on 2026-07-22 after WO-063 deployment |
| Rollback posture | Provider-native Netlify and Render rollback; database corrective-forward preferred; restore requires explicit authority |
| Tag posture | `v0.3.0-alpha.1` created and pushed; existing tags remain immutable |
| Release boundary | Single-owner hosted MVP cutover under ES-008 and ADP-005 |
| Public launch | Not authorized by WO-060 |
| Phase 8 | Not authorized by WO-060 |

## Release Tag Verification

PR #110 merged to `main` at
`bf3f34d21ecbe4d794b12105bfe44707277ce75b` after required CI passed.
GitHub Actions run `29960602464` completed successfully, including typecheck,
lint, tests, backend typecheck, backend lint, backend tests, backend
migrations, and build. Netlify deploy preview status was successful.

Tag verification:

```text
git ls-remote --tags origin v0.3.0-alpha.1
e8ea8b9c31ae4bc601f48916d053acdd30fcb38a refs/tags/v0.3.0-alpha.1

git ls-remote --tags origin v0.3.0-alpha.1^{}
bf3f34d21ecbe4d794b12105bfe44707277ce75b refs/tags/v0.3.0-alpha.1^{}
```

The first SHA is the annotated tag object. The peeled tag target is the PR #110
merge commit on verified `main`.

## Validation

This is a documentation-only post-tag verification update. Source CI is not
applicable because no application, migration, dependency, or runtime source
changed after the release tag.

Required local validation for this packet:

```text
git diff --check
rg -n "(sk-[A-Za-z0-9]{20,}|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\\s*=|refresh_token|access_token|postgresql://[^<]|postgresql\\+psycopg://[^<])" docs/governance/release-management.md docs/work-orders/060-release-tag-and-production-closeout.md docs/implementation-plans/hosted-production-cutover-work-order-backlog.md docs/implementation-plans/ADP-005-hosted-mvp-production-cutover.md docs/reviews/WO-060-release-tag-and-production-closeout-readiness-report.md
```

Result on 2026-07-22: `git diff --check` passed. The scoped secret scan
returned only the documented validation command above; no secret-like value was
recorded in the touched WO-060 governance files.

## Stop-and-Ask Boundary

Stop before tagging any commit other than the verified `main` closeout commit,
moving a tag, reusing a tag, claiming public launch, withdrawing a release,
changing provider state, changing production data, revoking credentials,
performing live cleanup, or starting Phase 8 without separate authority.

## Final Disposition

WO-060 is complete. The hosted single-owner MVP cutover is tagged as
`v0.3.0-alpha.1` at the verified PR #110 merge commit. Public launch,
production rollback or restore, provider cleanup, Phase 8 implementation,
multi-user operation, broader Google scopes, and live Gmail/Drive content use
remain outside this closeout and require separate authority.
