# Work Order 010: Runs and Artifacts Frontend Prototype

**Status:** Implementation Review — Merge Pending
**Work Order ID:** WO-010
**Type:** Frontend prototype
**Owner:** Product owner
**Review owner:** Frontend implementation
**Authorization date:** 2026-07-16
**Review authority:** [WO-010 authorization review](../reviews/WO-010-runs-and-artifacts-frontend-prototype-review.md)
**Implementation review:** [WO-010 implementation report](../reviews/WO-010-runs-and-artifacts-implementation-report.md)

## Purpose

Replace the Runs, Run Detail, and Artifacts placeholders with the selected Atlas
design language and add a canonical local Artifact Detail route. This Work Order
delivers fictional operational views only. It does not create a runtime, output
service, storage integration, log backend, or persistent record.

## Approved scope

- `/runs`: typed fixture inventory with local search, filters, true-value sorts,
  semantic desktop table, equivalent mobile cards, and empty/filtered states.
- `/runs/[runId]`: detail layout with summary facts, execution timeline, steps,
  normalized error context, log excerpts, approval references, and produced
  artifact links when the fixture destination exists.
- `/artifacts`: typed fixture inventory with local search, filters, true-value
  sorts, semantic desktop table, equivalent mobile cards, and sensitivity and
  retention context.
- `/artifacts/[artifactId]`: safe metadata-first detail view. Potentially unsafe
  content is not rendered inline; external storage is represented as fictional
  unavailable metadata.
- Canonical links from existing Agent Detail and Approval Detail fixtures only
  when their Run or Artifact target exists.
- Focused tests and durable visual evidence for representative and alternate
  states.

## Explicit exclusions and safety boundary

- No APIs, `fetch`, server actions, runtime, queues, storage access, persistence,
  authentication, authorization, retries, cancellation, download, or external
  mutations.
- No raw secrets, real personal content, credentials, full email bodies, or
  unsafe attachment rendering.
- Any control that resembles an operation must say `Simulate` and affect only
  component-local state. A refresh restores fixture state.
- Fixture logs are operational evidence examples, not audit records. Approval
  decisions and execution outcomes remain separate.
- Missing fixture destinations remain visibly unavailable metadata, never
  deceptive links.

## UX and design requirements

- Follow `docs/handoff.md` and the established inventory/detail skeletons.
- Use `PageHeader`, shared cards, controls, tables, `StatusBadge`, and `RiskChip`.
  State is never represented by color alone; geometric shapes remain risk-only.
- Run states cover queued, running, waiting for approval, succeeded, partially
  succeeded, failed, cancelled, and timed out using the shared vocabulary.
- Preserve shared identifiers including Run, Agent, Approval, Artifact, and
  correlation references without implying live correlation.
- Support light/dark themes, keyboard access, visible focus, 320px and
  200%-equivalent reflow, all sidebar tiers, and mobile card fallbacks.

## Acceptance criteria

1. Every route in scope is no longer a placeholder and has an honest
   `Frontend prototype` disclosure.
2. Inventory controls operate exclusively on typed local fixtures.
3. Run Detail distinguishes timeline events, operational logs, policy and
   approval context, errors, and outputs without duplicating concepts.
4. Artifact Detail exposes metadata and lineage without unsafe inline content
   or a false download/storage action.
5. Canonical fixture relationships navigate correctly and unavailable
   relationships remain non-interactive.
6. Desktop tables are semantic; mobile cards retain all decision-relevant data.
7. Automated tests and browser evidence cover primary, empty, filtered, error,
   responsive, theme, keyboard, focus, and reflow states.
8. `npm ci`, typecheck, lint, tests, and production build pass; required CI is
   green before governed merge.

## File scope

- `apps/web/src/app/(shell)/runs/**`
- `apps/web/src/app/(shell)/artifacts/**`
- Bounded fixture-link updates in Agents and Approvals
- Shared status vocabulary only where a canonical run/artifact state is missing
- `docs/work-orders/**`, `docs/reviews/**`, `docs/handoff.md`, and `ROADMAP.md`

Unrelated refactors, dependencies, and architecture changes are not authorized.

## Evidence and closure

The implementation report must record checks, CI, route inventory, source scans
for prohibited behavior, responsive/accessibility review, screenshot locations,
known limitations, rollback, PR, merge commit, and final main validation. Closure
requires that evidence and a completed conformance review.
