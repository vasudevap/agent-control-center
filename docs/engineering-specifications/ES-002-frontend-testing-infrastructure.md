# ES-002 — Frontend Testing Infrastructure

**Status:** Completed
**Owner:** Repository Maintainer
**Review Owner:** Repository Maintainer
**Related ADR:** `docs/decisions/ADR-001-frontend-component-testing.md`
**Unblocks:** `docs/work-orders/006-agents-inventory.md`
**Approved:** 2026-07-12
**Approved By:** Repository Maintainer
**Implementation Authorization:** Granted
**Implemented:** 2026-07-12
**Implementation Branch:** `chore/es-002-frontend-testing`
**Implementation Pull Request:** `https://github.com/vasudevap/agent-control-center/pull/4`
**Merged:** 2026-07-12

## Purpose

Establish the smallest maintainable frontend component-testing baseline needed
to support Work Order 006 and future Atlas UI work.

## Objective

Provide a canonical local and CI test command using Vitest, React Testing
Library, and jsdom without changing production behavior, runtime dependencies,
application architecture, deployment, or user-facing design.

## Intended Outcome

Contributors can write deterministic, user-oriented tests for synchronous React
components and client-side interactions. Pull requests fail when those tests fail.

## Governing References

- `AGENTS.md`
- `docs/governance/engineering-governance.md`
- `docs/governance/definition-of-ready.md`
- `docs/governance/definition-of-done.md`
- `docs/architecture/12-technology-strategy.md`, Sections 4, 25, and 29
- `docs/decisions/ADR-001-frontend-component-testing.md`
- `docs/work-orders/006-agents-inventory.md`
- Official Next.js Vitest and testing guidance
- Official React Testing Library guidance

## Approved Scope

- Add approved frontend testing packages as development dependencies only.
- Add a Vitest configuration for the `apps/web` TypeScript and path-alias setup.
- Add an explicit test setup module for DOM cleanup and approved matchers.
- Add `test` and `test:watch` scripts to the web workspace.
- Add a root `test` script that runs the web test suite once and exits.
- Add the root test command to CI after typecheck and before production build.
- Add at least one meaningful baseline component test proving configuration,
  DOM rendering, accessible querying, interaction, and cleanup.
- Document the canonical commands and test-location convention.
- Update governance and review records required by the Definition of Done.

## Test Conventions

- Use explicit imports from Vitest; do not enable globals.
- Prefer role, accessible-name, label, and visible-text queries.
- Test observable behavior rather than component internals.
- Prefer focused assertions over broad snapshots.
- Treat test fixtures as fictional and non-sensitive.
- Keep tests deterministic; do not access networks, external services, secrets,
  system time, or production data.
- Colocate tests with feature code or use a feature-local `__tests__` directory;
  do not create a new repository-level application package.

## Canonical Commands

The implementation must provide:

```text
npm test
npm --workspace @atlas/web run test
npm --workspace @atlas/web run test:watch
```

`npm test` and the workspace `test` command must run once and exit with a
non-zero status on failure. Watch mode must never run in CI.

## CI Behavior

The existing `Validate` job must run this sequence:

1. `npm ci`
2. `npm run typecheck`
3. `npm run lint`
4. `npm test`
5. `npm run build`

No test step may receive production credentials, write repository content,
deploy, call external services, or weaken another required check.

## Work Order 006 Coverage Contract

Once Work Order 006 implementation begins, its pull request must add automated
coverage for:

- Operational-attention ordering
- Case-insensitive search by name, description, and agent ID
- Independent status and health filters
- Combined filters
- Accurate result count
- Clear Filters restoration
- Filtered-empty recovery
- Deterministic populated, initial-empty, loading, and error representations
- Accessible names and semantic output that can be asserted in jsdom
- Agent-detail link destinations

Responsive layout, visual theme quality, browser history, focus visibility,
screen-reader behavior, and horizontal overflow remain manual/browser review
requirements until separately approved browser testing exists.

## Security and Privacy

- All packages are development-only.
- Tests use fictional local fixtures only.
- Tests must not read environment secrets or make network requests.
- CI permissions remain read-only.
- No production bundle, trust boundary, authentication, authorization, API, or
  persistence behavior changes.

## Architecture Impact

This specification adopts a development-time framework through ADR-001. It does
not change the Atlas runtime, container boundaries, deployment architecture, or
production technology baseline.

## Dependencies

- Approved ADR-001
- Existing Node.js 22, npm workspace, TypeScript, Next.js, React, and CI baseline
- Compatible development dependency versions resolved during implementation

## Out of Scope

- Work Order 006 product implementation
- Playwright, Cypress, or browser end-to-end testing
- Visual regression testing
- Screenshot automation
- Automated browser accessibility engines
- Async Server Component testing
- API, backend, contract, deployment, or smoke testing
- Coverage percentage gates
- Production dependency changes
- Unrelated dependency upgrades or vulnerability remediation

## Acceptance Criteria

1. ADR-001 is accepted before test-framework implementation begins.
2. Approved test dependencies are development-only and locked reproducibly.
3. `npm test` runs the frontend suite once and exits deterministically.
4. A watch-mode command is available for local development only.
5. At least one meaningful baseline component test passes.
6. TypeScript path aliases and JSX work in tests.
7. React Testing Library cleanup is deterministic between tests.
8. Tests can query accessible roles, names, labels, and visible text.
9. CI runs tests as a required step without secrets or write permissions.
10. Existing typecheck, lint, build, and application behavior do not regress.
11. The README or canonical engineering documentation explains how to run and
    locate frontend tests.
12. The implementation report records commands, results, dependency impact,
    limitations, and rollback evidence.

## Verification Plan

Run from the repository root:

```text
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

Inspect the dependency diff and lockfile, confirm test dependencies are not in
the production dependency set, confirm CI permissions remain read-only, and
observe the required pull-request CI result.

## Documentation Updates

- Update repository setup or engineering guidance with test commands.
- Update the CI description to include the test step.
- Add an ES-002 implementation report under `docs/reviews/`.
- Update Work Order 006 readiness evidence after ES-002 is approved, implemented,
  validated, reviewed, and merged.

## Risks and Mitigations

### Dependency compatibility

Mitigation: use current compatible releases, lock them with npm, and validate
typecheck, lint, tests, and production build together.

### jsdom mistaken for browser verification

Mitigation: preserve explicit manual responsive, theme, accessibility, and
browser-navigation checks.

### Brittle implementation-detail tests

Mitigation: enforce user-oriented Testing Library queries and focused behavior assertions.

### CI duration growth

Mitigation: keep this layer focused on fast component tests and defer browser suites.

## Rollback

Revert the ES-002 implementation pull request, removing its development
dependencies, test configuration, scripts, tests, CI step, and documentation.
No production data, deployment, or runtime rollback is required.

## Readiness Decision

This specification passed its readiness decision on 2026-07-12:

- ADR-001 is accepted.
- The repository maintainer approved the scope, dependencies, CI behavior, test
  conventions, acceptance criteria, and exclusions.
- Compatible package versions will be resolved, locked, and validated during
  implementation under the approved dependency set.
- The status is `Ready` and implementation is authorized.

ES-002 was implemented, validated, reviewed, merged, and closed on 2026-07-12.
Pull request `https://github.com/vasudevap/agent-control-center/pull/4` passed
the required `Validate` CI job before merge.

Work Order 006 is no longer blocked by the frontend testing infrastructure
prerequisite.
