# WO-013 Atlas Indicator Consistency Maintenance — Implementation Review

**Status:** Completed — PR #19 merged
**Date:** 2026-07-16
**Work Order:** [WO-013](../work-orders/013-indicator-consistency-maintenance.md)
**Branch:** `codex/chore-atlas-indicator-consistency`

## Outcome

Atlas operational inventories now share the quiet Alerts treatment: a semantic
icon and visible text with no pill container. `StatusBadge plain` is applied to
Agents and matching detail metadata; `RiskChip plain` now carries the same
treatment through Approvals and approval context. Overview remains the single
compact icon-only exception. Contained mobile status pills remain intentional.

Runs and Alerts no longer display redundant title counters. Connectors and
Policies now expose sort controls for every meaningful desktop-table value;
actions remain deliberately unsortable. The Work Order index now reflects the
already merged completion of WO-010 through WO-012.

## Boundaries and conformance

- No network request, persistence, API, authentication, connector operation,
  policy evaluation, or runtime behavior was introduced.
- Shared components retain ownership of status/risk semantics. No colour-only
  state or alternate visual system was introduced.
- The mobile Agents card follows the Alerts pattern: health is quiet inline;
  the labelled Status field retains contained state for card scanning.
- No architecture decision or ADR is required.

## Validation

| Check | Result |
| --- | --- |
| `npm run typecheck` | Passed |
| `npm run lint` | Passed |
| `npm test` | Passed — 17 files, 79 tests |
| `npm run build` | Passed — 15 routes generated |
| `git diff --check` | Passed |

## Browser and accessibility evidence

- Desktop Alerts, Agents, and Approvals at the normal `lg` shell show aligned
  quiet inline severity, health/status, and risk indicators.
- Mobile Agents at 390px retains visible health text and a contained Status
  pill in the card field; mobile Approvals at 390px retains readable inline
  risk plus contained approval state.
- Browser DOM snapshots confirm semantic table cells retain the visible labels.
- The indicator wording, component comments, handoff, and tests were updated
  together so future pages use the same rule.

## Rollback and limitations

This is a frontend/documentation-only change. Reverting the merge restores the
previous presentation; no fixture, external state, credential, or migration
rollback is required.

Required CI passed, PR #19 merged as `999cdea`, and final `main` was
synchronized. WO-013 is complete.
