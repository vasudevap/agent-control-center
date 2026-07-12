# ES-001 Engineering Governance and Continuous Integration Report

## Disposition

**Completed with one documented external limitation.** All repository, CI, pull-request, release, dependency-governance, validation, merge, reporting, and tagging deliverables are complete. GitHub main-branch protection cannot be enabled for this private repository on its current plan; exact safe setup steps are recorded in [`MANUAL-GITHUB-SETUP.md`](../governance/MANUAL-GITHUB-SETUP.md).

## Scope completed

ES-001 established the approved engineering specification, GitHub Actions CI, pull-request standards, lightweight trunk-based branches, merge policy, Definition of Ready, Definition of Done, Semantic Versioning and release rules, dependency-vulnerability governance, repository guidance alignment, advisory tracking, and a verified protection fallback. No approved application, product, UX, visual-design, or architecture behavior changed.

## Artifacts created

- `docs/engineering-specifications/ES-001-engineering-governance-and-ci.md`
- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `docs/governance/README.md`
- `docs/governance/engineering-governance.md`
- `docs/governance/branching-strategy.md`
- `docs/governance/pull-request-and-review-process.md`
- `docs/governance/definition-of-ready.md`
- `docs/governance/definition-of-done.md`
- `docs/governance/release-management.md`
- `docs/governance/dependency-and-vulnerability-management.md`
- `docs/governance/MANUAL-GITHUB-SETUP.md`
- This report

`README.md`, `PROJECT.md`, `ROADMAP.md`, `AGENTS.md`, and `.claude/CLAUDE.md` were minimally aligned to the new baseline.

## CI workflow

The `CI` workflow runs for pull requests targeting `main` and pushes to `main`. The `Validate` job uses `ubuntu-latest`, Node.js 22, npm caching, official `actions/checkout@v4` and `actions/setup-node@v4`, read-only `contents` permission, a 20-minute timeout, and concurrency cancellation. It runs from the repository root and sequentially executes `npm ci`, `npm run typecheck`, `npm run lint`, and `npm run build`. It uses no production secrets, write permissions, repository mutation, deployment, preview, release, automated review, or security-scanning workflow.

Atlas has no automated test suite, so no placeholder test step was introduced.

## Local validation before merge

| Check | Result |
| --- | --- |
| Workflow YAML parse | Passed |
| `npm ci` | Passed; 410 packages installed |
| `npm run typecheck` | Passed |
| `npm run lint` | Passed |
| `npm run build` | Passed; 11 static application routes and 2 dynamic routes |
| `git diff --check` | Passed after normalizing Markdown header whitespace |
| Local Markdown links | Passed |
| Scoped secret-pattern scan | Passed |
| Application-file scope review | Passed; no application file changed |

The sandboxed build initially could not reach the existing Google Fonts endpoints. A permitted-network rerun passed without a source change.

## Pull request and GitHub CI

- Pull request: [#3 — ci(governance): establish Atlas engineering controls](https://github.com/vasudevap/agent-control-center/pull/3)
- Base/head: `main` ← `chore/es-001-engineering-governance-ci`
- Final CI run: [Validate, run 29201832781](https://github.com/vasudevap/agent-control-center/actions/runs/29201832781/job/86674407021)
- Final CI result: Passed in 44 seconds
- Merge method: Normal merge commit
- Merge commit: `1e8339444998d463c7164ff6a6d07d1b95651c5f`
- Merge date: `2026-07-12T17:22:33Z`

The remote feature branch was deleted after merge.

## Branch protection and ruleset result

Both `GET /repos/vasudevap/agent-control-center/branches/main/protection` and `GET /repos/vasudevap/agent-control-center/rulesets` returned HTTP 403 with GitHub's instruction to upgrade to GitHub Pro or make the private repository public. No protection was applied, no unsafe workaround was used, and no setting capable of locking out the sole maintainer was attempted. Exact preferred ruleset and classic-protection steps are in [`MANUAL-GITHUB-SETUP.md`](../governance/MANUAL-GITHUB-SETUP.md).

## Dependency advisory issue

- Issue: [#2 — chore(deps): track PostCSS and Next.js audit advisories](https://github.com/vasudevap/agent-control-center/issues/2)
- Labels: None; existing repository labels did not include an accurate dependency category.
- Audit state: 2 moderate, 0 high, 0 critical.
- Decision: Track and reassess a compatible upstream fix; do not force npm's invalid major downgrade to Next.js 9.3.3.

## Post-merge validation

Local `main` was fast-forwarded to the merge commit. `npm ci`, typecheck, lint, and production build passed again. The build retained `/`, `/agents`, `/agents/[agentId]`, `/alerts`, `/approvals`, `/artifacts`, `/audit`, `/connectors`, `/policies`, `/runs`, `/runs/[runId]`, and `/settings`. The known two moderate advisories remained unchanged.

## Release

- Annotated tag: `v0.2.0-alpha.2`
- Tag message: `Engineering governance and continuous integration baseline`
- Tagged commit: `1e8339444998d463c7164ff6a6d07d1b95651c5f`
- Remote: Pushed to `origin`; earlier tags were not changed.
- Deployment: None; ES-001 does not introduce automatic production deployment.

## Known limitations and manual action

1. Main remains unprotected until the repository plan or visibility supports GitHub branch rules. Apply and verify the documented settings after a separately approved plan/visibility decision.
2. Atlas has no automated test suite. CI requires install, typecheck, lint, and build only; a future approved specification should introduce real test infrastructure.
3. Two moderate PostCSS/Next.js findings remain tracked in issue #2 pending a compatible upstream remediation.

## Final repository state

The final report was prepared on synchronized `main`. After the documentation-only closeout commit is pushed, the expected and verified handoff state is a clean local `main` aligned with `origin/main`, with `v0.2.0-alpha.2` published at the ES-001 merge baseline.

## Recommendation

ES-001 satisfies the engineering-governance and CI baseline. The next approved Work Order may begin only after it passes the new Definition of Ready and follows the branch, pull-request, CI, and Definition of Done controls. Do not begin Work Order 006 or any other implementation work without that approval.
