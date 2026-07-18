# WO-034 Phase 5 Dashboard Contract Compatibility Pass — Implementation Report

**Work Order:** [WO-034](../work-orders/034-phase-5-dashboard-contract-compatibility-pass.md)
**Status:** Implemented Locally - Pending PR, CI, and Merge
**Date:** 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing ADP:** [ADP-002](../implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md)

## Summary

WO-034 adds a narrow dashboard/backend compatibility seam for the stable Phase 5
contracts. The dashboard remains fixture-driven, but it now has typed contract
shapes, mapping helpers, and tests that show how current agents, runs,
approvals, audit, manual-handling, and knowledge surfaces relate to backend
contracts.

This work does not complete Phase 4 dashboard productization and does not add
live browser API calls.

## Implemented Scope

- Added `apps/web/src/lib/phase5-contracts.ts` with:
  - Phase 5 response envelope metadata;
  - agent descriptor, run lifecycle, approval, manual-handling, knowledge fact,
    knowledge question, and durable audit shapes;
  - dashboard compatibility adapters for agents, runs, and approvals;
  - a surface compatibility registry for mapped and deferred dashboard routes.
- Added `apps/web/src/lib/phase5-contracts.test.ts` to prove:
  - required Phase 5 surfaces are represented;
  - missing manual-handling and knowledge routes are marked deferred;
  - agent descriptors, run lifecycle payloads, and approval evidence map to
    dashboard-compatible fields.
- Added the
  [Phase 5 Dashboard Contract Compatibility Map](../implementation-plans/phase-5-dashboard-contract-compatibility-map.md).

## Validation Evidence

Local frontend validation:

```text
npm --workspace @atlas/web run test -- src/lib/phase5-contracts.test.ts
npm --workspace @atlas/web run typecheck
npm --workspace @atlas/web run lint
```

Result:

```text
1 test file passed, 4 tests passed
typecheck passed
lint passed
```

Production build validation:

```text
npm --workspace @atlas/web run build
```

The first sandboxed build failed while fetching approved Google Fonts through
`next/font`, matching the known local restricted-network behavior. The same
build passed with network permission.

Successful build result:

```text
Compiled successfully
Generated 13 static pages
Retained /, /agents, /agents/[agentId], /approvals, /approvals/[approvalId],
/audit, /runs, /runs/[runId], and existing shell routes.
```

## Scope Boundary Confirmed

- No live API client was introduced.
- No browser-side external-client signing or credential handling was
  introduced.
- No Gmail-specific UI was introduced.
- No manual-handling or knowledge route was invented.
- No full Phase 4 dashboard productization claim was made.
- No production deployment authority was used.

## Follow-Ups

- Phase 4 productization should decide how the dashboard authenticates and
  calls backend contracts.
- Manual-handling and knowledge routes need separate product/design authority
  before UI implementation.
- Live audit browsing needs an accepted read API if it becomes part of the
  operator dashboard.
