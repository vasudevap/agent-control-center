# Release Management

## Version model

Atlas follows Semantic Versioning with standardized release tags in this
format:

```text
vMAJOR.MINOR.PATCH[-stage.N]
```

Use these prerelease stages:

- `alpha.N` for internal, single-owner, portfolio, or governed-but-not-public
  milestones.
- `beta.N` for hosted or controlled-user releases with accepted residual risks.
- `rc.N` for release candidates where no known blocker remains.
- No suffix only for stable/public releases.

Version increments follow this project convention:

- **Major** — incompatible change or major product/platform change.
- **Minor** — backward-compatible capability, completed phase package, hosted
  cutover, or substantial governed product/platform milestone.
- **Patch** — backward-compatible defect correction or maintenance release.

Tags are annotated, are never moved or reused, and use the release message to
name the milestone plus the governing artifacts included in the release.

The consolidation release `v0.2.0-alpha.1` is immutable. The expected release after ES-001 is `v0.2.0-alpha.2`.
The hosted single-owner MVP cutover release is `v0.3.0-alpha.1`.

## Readiness and release procedure

Before tagging, confirm the included Work Orders and specifications meet the Definition of Done, required CI passes, `main` is synchronized and clean, local release validation passes, migration/security/rollback considerations are reviewed, and known issues are disclosed.

Release notes identify the version, commit, release date, included governing artifacts, changed components, validation, migrations, known issues, and rollback expectations. Create an annotated tag at the verified `main` commit and push it without changing earlier tags. Verify the remote tag dereferences to the intended commit.

For the Phase 7 MVP release candidate, use the operational runbooks and
rollback procedures in
[`phase-7-release-runbooks-and-rollback.md`](../implementation-plans/phase-7-release-runbooks-and-rollback.md)
before any production cutover, production migration, controlled-account
execution, or release withdrawal.

## Rollback

Prefer a reviewed revert or corrective forward release. Never rewrite published history or move a release tag. Deployment rollback instructions become mandatory when deployment automation is introduced; ES-001 creates no automatic production deployment.

## Work Orders and releases

Work Orders and Engineering Specifications authorize changes; releases package one or more completed artifacts. Completion does not automatically require a release unless the governing artifact or roadmap says so. Release creation never begins a subsequent Work Order.
