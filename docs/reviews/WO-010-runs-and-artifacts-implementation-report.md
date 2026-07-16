# WO-010 Runs and Artifacts Frontend Prototype — Implementation Review

**Status:** Pass — Governed Merge Authorized
**Date:** 2026-07-16
**Work Order:** [WO-010](../work-orders/010-runs-and-artifacts-frontend-prototype.md)
**Branch:** `feat/wo-010-runs-artifacts`

## Outcome

WO-010 replaces the Runs, Run Detail, and Artifacts placeholders and adds a
canonical Artifact Detail route. The implementation uses typed fictional
fixtures and established Atlas inventory/detail components. Agent Detail and
Approval Detail now link Run and Artifact references only when their local
fixture destination exists.

## Prototype and architecture conformance

- No API, `fetch`, server action, runtime, queue, storage operation, browser
  persistence, authentication, authorization, retry, cancellation, download,
  or external mutation was introduced.
- Run steps and logs are fictional operational evidence. They are explicitly
  distinct from Audit records.
- Artifact content is never rendered inline. Storage, downloads, and access
  control remain unavailable metadata.
- Approval decision state and execution outcome remain separate.
- Shared `StatusBadge`, table, card, page-header, sort, search, empty, and error
  patterns are reused; no parallel design system was created.
- No architecture decision changed and no ADR is required.

## Automated validation

| Check | Result |
| --- | --- |
| `npm ci` | Passed — 505 packages installed from lockfile |
| `npm run typecheck` | Passed |
| `npm run lint` | Passed |
| `npm test` | Passed — 12 files, 66 tests |
| `npm run build` | Passed — 14 routes generated, including Artifact Detail |
| Scoped prohibited-primitive scan | Passed — no matches |
| `git diff --check` | Passed |

The locked baseline reports two existing moderate dependency advisories; WO-010
adds no dependency or lockfile change. Required GitHub CI must pass before merge.

## Browser and accessibility evidence

- Desktop `lg` shell, light and dark themes: Runs inventory.
- Desktop `lg` detail: failed Run and review-required Artifact.
- Tablet `md` shell: Runs table at 768px.
- Mobile `<md`: Artifact card fallback at 375px.
- 320px fixture reflow: no document-level horizontal overflow.
- 640px constrained viewport as a 200%-equivalent reflow check: no document-level
  horizontal overflow.
- Search, combined filters, native-select keyboard semantics, sortable table
  semantics, canonical links, unavailable records, and recoverable-error state
  are covered by component tests and browser checks.
- Browser console was checked after the deterministic-time correction; the
  hydration issue overlay cleared.

Durable screenshots:

- `docs/reviews/assets/wo-010/runs-desktop-1440-light.png`
- `docs/reviews/assets/wo-010/runs-desktop-1440-dark.png`
- `docs/reviews/assets/wo-010/runs-tablet-768-light.png`
- `docs/reviews/assets/wo-010/artifacts-mobile-375-light.png`
- `docs/reviews/assets/wo-010/run-detail-failed-desktop-1440-light.png`
- `docs/reviews/assets/wo-010/artifact-detail-review-required-desktop-1440-dark.png`

## Review findings resolved

1. Relative fixture timestamps initially produced a server/client hydration
   mismatch. Fixtures now use a deterministic reference timestamp.
2. The Runs desktop table produced inner horizontal overflow at the full shell
   width. A fixed, bounded column model now fits the available workspace.
3. Legacy Approval Detail tests expected unavailable Run and Artifact metadata.
   They now verify canonical links for implemented fixtures.

## Known limitations and rollback

All records remain local fictional fixtures and reset on refresh. Real runtime,
log storage, output storage, file access, retention enforcement, access control,
and lifecycle operations require later architecture and Work Orders.

Rollback is a frontend/documentation revert. No migration, credential rotation,
provider remediation, or data rollback is required.

## Closure gate

The implementation is ready for governed PR review and merge. WO-010 remains
open until required CI passes, the PR merges, final `main` is synchronized, and
the completion status records the merged evidence.
