# ADR-001 — Frontend Component Testing

**Status:** Accepted
**Owner:** Repository Maintainer
**Decision Type:** Technology and engineering quality
**Related Specification:** `docs/engineering-specifications/ES-002-frontend-testing-infrastructure.md`
**Related Work Order:** `docs/work-orders/006-agents-inventory.md`
**Accepted:** 2026-07-12
**Accepted By:** Repository Maintainer

## Context

Atlas uses Next.js, React, and strict TypeScript but does not currently have an
automated frontend test runner, component-testing library, DOM test environment,
or canonical test command. Work Order 006 requires deterministic representations
of interactive inventory behavior and explicitly blocks implementation until the
frontend testing gap is resolved or covered by an approved temporary exception.

The technology strategy already calls for frontend component, accessibility,
API-integration, responsive, and eventual end-to-end tests. It does not select
the tooling used to provide those capabilities.

Introducing a test framework is an architectural technology decision under the
repository ADR policy.

## Decision Drivers

- Compatibility with the existing Next.js App Router and TypeScript baseline
- Support for synchronous React client and component tests
- User-oriented DOM queries and interaction testing
- Fast local feedback and deterministic CI execution
- Minimal configuration and dependency footprint
- No production runtime, deployment, security-boundary, or bundle impact
- A clear path to later browser end-to-end testing without conflating the two layers

## Considered Options

### Vitest with React Testing Library and jsdom

Use Vitest as the test runner, React Testing Library for user-oriented component
tests, and jsdom as the Node-based browser environment.

Advantages:

- Current official Next.js guidance documents this combination.
- Fast TypeScript-oriented test execution and watch mode.
- React Testing Library encourages tests based on roles, labels, text, and user behavior.
- The dependencies remain development-only.

Limitations:

- Vitest does not cover asynchronous React Server Components reliably.
- jsdom does not prove real-browser layout, responsive rendering, or navigation behavior.
- Browser end-to-end tests remain necessary later.

### Jest with React Testing Library and jsdom

Jest is mature and broadly adopted, but it requires more Next.js-specific
configuration and provides no material advantage for the current synchronous
client-component scope.

### Playwright-only browser testing

Playwright provides strong browser and responsive evidence, but using it as the
only initial layer would make small filtering and state tests slower and more
operationally expensive. It remains a future end-to-end option.

### Continue with manual testing only

This avoids dependencies but leaves collection-screen behavior without automated
regression coverage and does not provide the desired long-term quality baseline.

## Decision

Adopt Vitest with React Testing Library and jsdom for Atlas frontend unit,
component, and lightweight integration tests.

Use explicit imports from Vitest rather than enabling test globals. Tests should
prefer accessible roles, names, labels, and observable user behavior over
implementation details or broad snapshots.

The initial setup may include only development dependencies required by the
official Next.js Vitest setup and interaction assertions. Exact compatible
versions must be resolved and locked during ES-002 implementation.

Browser end-to-end testing, visual regression testing, and automated browser
accessibility engines are deferred to separately approved work. Manual responsive,
theme, keyboard, and screen-reader evidence remains required for Work Order 006.

## Consequences

### Positive

- Atlas gains a canonical, repeatable frontend test command.
- Work Order 006 search, filtering, ordering, state, and navigation rendering can
  receive automated regression coverage.
- CI can block merges when frontend component tests fail.
- Tests reinforce accessible component contracts.

### Negative

- The repository gains development dependencies and test configuration.
- Test setup and fixtures require ongoing maintenance.
- jsdom can create false confidence if treated as browser-layout verification.

## Risks

- Next.js, React, Vite, or jsdom compatibility may change across upgrades.
- Tests may overfit implementation details if review does not enforce user-oriented assertions.
- Teams may mistake component tests for responsive, browser, or end-to-end coverage.

## Mitigations

- Lock dependencies through the repository lockfile and validate them in CI.
- Follow current official Next.js and Testing Library setup guidance.
- Keep browser and manual verification requirements explicit.
- Reassess the setup during framework upgrades or when async Server Components
  become direct test subjects.

## Revisit Triggers

- Atlas introduces async Server Components requiring direct automated coverage.
- Browser-level workflows or authentication become implementation scope.
- Component-test runtime or reliability materially degrades.
- A Next.js or React upgrade makes the selected toolchain unsupported.
- Visual regression or automated browser accessibility testing becomes a release gate.

## References

- [Next.js Vitest guide](https://nextjs.org/docs/app/guides/testing/vitest)
- [Next.js testing overview](https://nextjs.org/docs/app/guides/testing)
- [React Testing Library introduction](https://testing-library.com/docs/react-testing-library/intro/)
