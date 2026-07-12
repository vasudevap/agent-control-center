# ES-001 — Engineering Governance and Continuous Integration

**Status:** Approved for implementation by the ES-001 task

**Owner:** Repository maintainer

**Approved:** 2026-07-12

**Target release:** `v0.2.0-alpha.2`

## Purpose

Establish the engineering controls required to evolve Atlas through reviewed, reproducible, and auditable changes while preserving the approved architecture, product design, and application baseline.

## Scope

ES-001 defines repository governance, a continuous-integration quality gate, pull-request standards, a lightweight trunk-based branching model, readiness and completion criteria, release management, dependency-risk handling, and main-branch controls.

## Objectives

- Keep `main` releasable and changes traceable to an approved artifact.
- Validate reproducible installation, type safety, lint quality, and production builds on every pull request to `main` and every push to `main`.
- Make review, release, and dependency-risk decisions explicit without imposing an impractical multi-reviewer process on a solo maintainer.
- Prevent governance automation from accessing production secrets, deploying, or changing repository content.

## Current baseline

- Canonical branch: `main` at documented commit `ed5a8f5` when ES-001 began.
- Consolidation merge: `5b0cd74fc3484cb9efd48ba867813b0d791268c2`.
- Existing annotated release: `v0.2.0-alpha.1`, pointing to the consolidation baseline.
- Application: `apps/web`, managed by the root npm workspace and lockfile.
- `npm ci`, typecheck, lint, and production build pass.
- No automated test suite, GitHub Actions workflow, pull-request template, or ES-001 implementation existed at preflight.
- Two moderate PostCSS/Next.js audit findings remain without a suitable non-breaking automated remediation.

## Governance principles

Atlas applies architecture before implementation, a single authority for each artifact, least privilege, short-lived change branches, evidence-based review, protected and releasable `main`, documented exceptions, and documentation as a deliverable. Governance must remain proportionate to a solo-maintained project without weakening required quality gates.

## Required repository artifacts

- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `docs/governance/` governance handbook and control documents
- Root repository guidance aligned to these controls
- A tracked GitHub issue for unresolved dependency advisories
- `docs/reviews/ES-001-engineering-governance-and-ci-report.md`

## CI requirements

The CI workflow runs at the repository root on pull requests targeting `main` and pushes to `main`. It uses maintained official actions, Node.js 22, npm caching, read-only repository permissions, and concurrency cancellation for superseded runs. The required sequence is `npm ci`, `npm run typecheck`, `npm run lint`, and `npm run build`; any failure fails the job. The workflow has no production secrets, write permissions, deployment, preview, release, automated review, or repository mutation.

Atlas currently has no automated test suite. Tests are therefore not a required ES-001 CI step; a future approved specification must add real test automation before tests become a required check.

## Branching model

Atlas uses lightweight trunk-based development. `main` is always releasable. Each approved Work Order, Engineering Specification, defect, documentation change, or maintenance task uses one short-lived `feat/`, `fix/`, `chore/`, `docs/`, or `hotfix/` branch. Branches merge through pull requests, are deleted when practical, and must not force-push to `main`. Atlas has no `develop` branch and no long-lived release branch unless a later approved requirement justifies one.

## Pull-request model

Every pull request identifies its governing artifact, scope and exclusions, impacts, validation evidence, documentation changes, risks, and relevant visual evidence. Required CI must pass before merge. Review confirms scope, architecture and design compliance, security and privacy treatment, documentation, and release implications.

## Merge model

Use a normal merge commit for milestones, Work Orders, Engineering Specifications, or meaningful multi-commit changes so the governed branch history remains visible. Squash merging is permitted for small atomic maintenance or documentation changes when intermediate commits have no durable value. Do not rebase or merge while required CI is failing. Emergency exceptions follow the documented hotfix process and require retrospective evidence.

## Definition of Ready

Work is ready only when the objective, approved scope, acceptance criteria, exclusions, architecture and design references, dependencies, security and privacy impacts, data and integration impacts, relevant UI states and responsive expectations, verification plan, review owner, and unresolved-decision disposition are explicit as applicable.

## Definition of Done

Work is done only when the approved scope and acceptance criteria are satisfied; required typecheck, lint, build, tests where present, UI accessibility/responsive review where relevant, architecture/design review, security/privacy review, documentation, decision records, implementation report, CI, approved merge, release notes/version updates where required, and artifact/secret hygiene are complete.

## Release and versioning model

Atlas follows Semantic Versioning: major for incompatible or major product-platform changes, minor for backward-compatible capabilities or substantial milestones, and patch for backward-compatible fixes or maintenance. Prereleases use `alpha`, `beta`, or `rc` identifiers. Tags use annotated `vMAJOR.MINOR.PATCH[-prerelease.N]` names and never move. `v0.2.0-alpha.1` is preserved; the expected ES-001 release is `v0.2.0-alpha.2`. Release notes disclose changes, validation, known issues, and rollback considerations. No automatic production deployment is introduced.

## Dependency and vulnerability policy

The lockfile and `npm ci` define reproducible dependency installation. `npm audit` is evidence requiring evaluation, not an automatic pass/fail decision. High or critical findings receive prompt triage; moderate and low findings receive a documented risk assessment. Unresolved findings are tracked in GitHub and reviewed during releases and dependency maintenance. Atlas prefers compatible upstream fixes and does not force a breaking downgrade, invalid override, or unrelated feature-branch upgrade merely to clear audit output.

## GitHub repository controls

Where supported, `main` requires a pull request and the CI `Validate` status, requires the branch to be current when practical, blocks force pushes and deletion, and applies to administrators where practical. Required approving-review count remains zero for the sole maintainer. If permissions or plan limitations prevent automation, exact manual steps are recorded without weakening the repository artifacts or validation baseline.

## Acceptance criteria

- All required governance, CI, template, repository-guidance, issue, and report artifacts exist and agree.
- CI performs only the four required root commands and passes on the ES-001 pull request.
- Local pre-merge and post-merge validation passes.
- The ES-001 pull request is merged through a normal merge commit.
- Main-branch protection is applied and verified, or exact manual steps and the blocking limitation are documented.
- The known dependency risk is tracked and linked.
- Annotated tag `v0.2.0-alpha.2` is created only after successful post-merge verification.

## Exclusions

ES-001 does not change application behavior, product design, architecture, dependencies, test strategy, deployment, preview environments, releases automation, security scanning, Codex review, backend services, authentication, APIs, or Work Order 006.

## Verification

Verify the workflow syntax and configuration, run `npm ci`, typecheck, lint, and build locally, inspect the complete diff, scan for likely secrets, verify links and instruction consistency, observe the pull-request CI result, repeat validation on synchronized `main`, confirm a clean worktree, query protection settings where possible, and verify the annotated release tag.

## Rollback and failure handling

Failed CI blocks merge and is repaired only within ES-001 scope. A faulty governance change is reverted through a reviewed pull request. Earlier tags are immutable. If a new release must be withdrawn, publish a corrective commit and new version rather than moving its tag. If protection would lock out the maintainer, do not apply it; record safe manual settings. Production rollback is outside scope because ES-001 performs no deployment.

## Completion criteria

ES-001 is complete when all acceptance criteria are met, the final report records immutable GitHub and Git references, the release tag is pushed, `main` is clean and synchronized, and any unavoidable manual action is explicit.
