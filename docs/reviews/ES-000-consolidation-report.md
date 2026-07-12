# ES-000 Consolidation Report

## Summary

ES-000 consolidated the approved Atlas frontend and its governance record into the existing `agent-control-center` Git repository without replacing or reinitializing repository history. The application now lives in `apps/web`, is managed by one root npm workspace and lockfile, and passes the required install, typecheck, lint, build, route, responsive, theme, and interaction verification.

## Initial Repository State

- Branch: `main`, aligned with `origin/main` before cleanup.
- Legitimate staged Atlas brand and product-design work was present.
- Accidental `.DS_Store` files were staged in the root and documentation folders.
- Git represented the intended deletion of the retired root `ARCHITECTURE.md` as a rename to an empty file named `Metric`.
- The ES-000 package was present under the misspelled path `docs/engineering specificaitons/`.
- `.migration-source/atlas-ai/atlas-ui` and `.migration-source/atlas-ai/claude` were available as ignored source material.

## Cleanup Performed

- Removed all discovered `.DS_Store` files and added a repository ignore rule.
- Inspected `Metric`, confirmed it was zero bytes, and inspected Git history for `ARCHITECTURE.md`.
- Preserved the intended deletion of the retired monolithic `ARCHITECTURE.md`; no unique `Metric` content required archiving.
- Preserved and committed the legitimate Atlas design and documentation baseline on `main` as `e65e391`.
- Pushed the cleaned baseline to `origin/main` before consolidation.
- Corrected `docs/engineering specificaitons/` to `docs/engineering-specifications/` on the consolidation branch.
- During independent final review, normalized trailing whitespace and final blank lines in migrated review records so `git diff --check` passes.

## Safety Tag

Annotated tag `pre-consolidation-20260712-114832` points to `e65e391` and was pushed to origin before the consolidation branch was created.

## Migration Branch

All consolidation work after the baseline was performed on `chore/canonical-repository-consolidation`. The branch is intended for review and must not be merged automatically by this specification.

## Source Material Location

Read-only source material remains unchanged and ignored under `.migration-source/atlas-ai`. The external original source folder was not modified or deleted.

## Source Comparison Summary

- `atlas-ui`: 20 files; an uncustomized create-next-app scaffold with a single default route, default assets, and no Work Order 005 implementation or approval evidence.
- `claude`: 96 files; the complete Atlas application, design recommendations, work orders, reviews, decision log, and implementation guidance.
- Migrated application: 70 source/config/static files before generated build output.
- No union copy was performed.

Notable evidence in `claude` included the `(shell)` route group, Sidebar, Top Navigation, `PageContainer`, `Breadcrumb`, shared loading and error boundaries, all required routes, responsive mobile drawer with focus trapping, theme infrastructure, and final Work Order 005 approval records.

## Authoritative Frontend Determination

`.migration-source/atlas-ai/claude` was verified as the authoritative frontend. Work Order 005 and `reviews/handoff-005-app-shell.md` mark the implementation completed, design-approved, final-review passed, and merged. The live source also contains all three required final refinements:

1. Notifications are invoked with `unreadCount={0}` and default to zero.
2. Detail titles are `Agent Details` and `Run Details`, with IDs in descriptions and breadcrumbs.
3. Search placeholder text is exactly `Search agents, runs, artifacts...`.

No application file was migrated from `atlas-ui` because it contained no unique approved artifact beyond generic scaffold content.

## Frontend Migration Summary

- Migrated the coherent `claude/src`, `claude/public`, package manifest, and required Next.js, TypeScript, ESLint, and PostCSS configuration into `apps/web`.
- Preserved the approved Overview implementation and the shared shell without redesign or feature additions.
- Preserved routes for Overview, Agents, Agent Details, Runs, Run Details, Approvals, Alerts, Connectors, Policies, Artifacts, Audit, and Settings.
- Excluded dependencies, build output, caches, environment files, local Claude settings, and unrelated workspace documentation from the application folder.

## Documentation and Governance Migration Summary

- Migrated Work Orders 001–005 into `docs/work-orders/`.
- Migrated durable review and handoff records into `docs/reviews/`.
- Migrated the Atlas design decision index into `docs/decisions/`; accepted DDRs remain under `docs/design/decisions/`.
- Migrated design recommendations into `docs/recommendations/` with explicit advisory status.
- Preserved historical Claude workspace boundaries and implementation guidance in `docs/references/claude-workspace/` with provenance notes.
- Created `.claude/CLAUDE.md` as scoped Claude guidance while keeping root `AGENTS.md` tool-neutral and authoritative.
- Updated `README.md`, `PROJECT.md`, `ROADMAP.md`, and `AGENTS.md` only to reflect the canonical structure and current implementation baseline.

## Files Archived

No uncertain application source required a copy under `docs/references/archive/`. Potentially useful but non-canonical Claude workspace guidance was preserved under `docs/references/claude-workspace/` and explicitly classified as historical reference material.

## Files Discarded or Excluded

- Accidental `.DS_Store` files and empty `Metric` file.
- The non-authoritative `atlas-ui` application scaffold.
- Generic create-next-app README content from both source applications.
- Local `.claude/settings.local.json` and `.claude/launch.json` metadata.
- An exact duplicate of accepted `DDR-002` found in the source review folder; the canonical copy remains in `docs/design/decisions/`.
- Empty source `output/` and `references/` folders.
- `node_modules`, `.next`, build, coverage, cache, TypeScript build-info, real environment, certificate, and key files.
- Default public SVG assets were retained because they were part of the coherent authoritative application source; they can be removed later only through an ordinary reviewed cleanup.

## Configuration Changes

- Added a private root npm workspace targeting `apps/*`.
- Added root `dev`, `start`, `typecheck`, `lint`, and `build` scripts delegated to `@atlas/web`.
- Added `typecheck` and an explicit `eslint .` script to the web package.
- Preserved the app-local `@/* -> ./src/*` TypeScript alias and existing Next.js/PostCSS configuration.
- Expanded ignore rules for dependencies, generated frontend output, local environment files, metadata, migration sources, and task logs.

## Dependency and Workspace Changes

- Adopted one root `package-lock.json`; removed the nested app lockfile.
- `npm install` generated the workspace lockfile, after which `npm ci` proved reproducible installation.
- `npm audit` reports two moderate findings: a PostCSS advisory in Next.js's nested dependency and the resulting finding against direct dependency `next`. No high or critical findings were reported. npm's offered remediation is an invalid major downgrade for this application, so no forced dependency change was made during migration.

## Secret Scan Results

- The required pattern scan found no likely secret. Its only textual match was `queue-microtask` in the npm registry URL inside `package-lock.json`, a false positive caused by the `sk-` substring.
- No real `.env` file is tracked.
- No tracked `.DS_Store`, dependency folder, build directory, cache, coverage directory, or TypeScript build-info file exists.
- No tracked app or configuration file depends on the ignored migration source.

## Verification Results

| Command | Result | Notes |
| --- | --- | --- |
| `npm ci` | Passed | 410 packages installed from the root lockfile. |
| `npm run typecheck` | Passed | TypeScript completed with no errors. |
| `npm run lint` | Passed | ESLint completed with no errors or warnings. |
| `npm run build` | Passed | Next.js 16.2.10 produced 11 static application routes plus 2 dynamic routes. |
| `npm test` | Not applicable | The approved source defines no test script or test suite. |

The first sandboxed build could not fetch the approved Google Fonts; the permitted-network rerun completed successfully. No application remediation was required.

## Route Verification

A local production server was exercised in the in-app browser. All required routes rendered successfully inside the shared Sidebar, Top Navigation, and main content shell:

`/`, `/agents`, `/agents/test-agent`, `/runs`, `/runs/test-run`, `/approvals`, `/alerts`, `/connectors`, `/policies`, `/artifacts`, `/audit`, and `/settings`.

Dynamic routes rendered the correct stable titles and retained test IDs in supporting descriptions and breadcrumbs. No browser console errors were recorded.

## Responsive Verification

Live browser checks were completed at 1440, 1024, 768, and 375 px in both light and dark themes.

- 1440 and 1024 px: persistent desktop Sidebar, visible search, no mobile trigger.
- 768 px: desktop Sidebar hidden, mobile trigger visible, search retained.
- 375 px: desktop Sidebar and search hidden, mobile trigger visible.
- Both themes applied successfully at every width.
- No viewport produced document-level horizontal overflow.

## Work Order 005 Behavior Verification

- Sidebar and Top Navigation persisted on every required route.
- `PageContainer` wraps shared route content.
- Breadcrumbs render on both dynamic detail routes.
- Search placeholder is exactly `Search agents, runs, artifacts...`.
- Notifications expose no unread indicator and show `No notifications yet`.
- Agent and run detail titles and ID placement match the approved refinements.
- Mobile drawer opens with focus on Close, traps backward focus from Close to Settings, traps forward focus from Settings to Close, closes on Escape, and restores focus to Open navigation.
- Shared `(shell)/loading.tsx` and `(shell)/error.tsx` remain inside the shared shell layout.
- Placeholder routes reuse `PlaceholderPage` rather than bespoke route layouts.

## Git Commits Created

- `e65e391` — `docs(design): add Atlas brand and product design baseline` (`main`)
- `590dece` — `chore(repo): prepare canonical consolidation`
- `5545567` — `feat(web): migrate approved Atlas frontend implementation`
- `47418ea` — `chore(build): configure Atlas workspace and validation scripts`
- `e6e561d` — `docs(governance): migrate work orders reviews and decisions`
- `ca8abbe` — `docs(repo): align Atlas repository guidance`
- `docs(reviews): add ES-000 consolidation report` — this report commit; use Git history for its final hash.

## Final Git Status

The expected final state is branch `chore/canonical-repository-consolidation`, pushed to origin with a clean working tree. Final ref and cleanliness verification is performed after this report is committed.

## Unresolved Issues

- `npm audit` reports two moderate PostCSS/Next.js dependency findings with no suitable non-breaking automated fix offered by npm. They do not block install, typecheck, lint, build, or runtime verification and should be tracked for an upstream Next.js dependency update.
- Historical documents retain different naming eras (`Agent Control Center` and `Atlas`) and authority levels. They were not rewritten: current approved brand/design documentation and the updated README use Atlas, while the PRD and older strategy records remain preserved.
- The Work Order 005 handoff intentionally contains pre-refinement file excerpts and a stale known-limitations paragraph, while its final disposition and the migrated source record the approved fixes. This provenance was preserved rather than rewritten.
- Migrated recommendations include ideas not accepted into canonical architecture or work orders. Their README explicitly classifies them as advisory.

## Manual Actions Remaining

1. Review this report and the GitHub branch diff.
2. Review the application visually if additional screenshot-based design sign-off is desired.
3. Track the moderate upstream PostCSS/Next.js audit finding.
4. Merge `chore/canonical-repository-consolidation` into `main` if satisfied.
5. Decide later whether to remove the ignored migration copy and external original source.
6. Create a release tag separately if desired.

## Merge Recommendation

Recommend merging after normal branch review. ES-000 completion criteria are satisfied, validation is green, provenance is preserved, and no migration blocker remains. The moderate transitive dependency advisory should be tracked but does not require a forced or breaking change in this consolidation.

## Recommendation on Original Source Folders

Retain both `.migration-source` and the external original `atlas-ai` folder until the consolidation branch is reviewed and merged. After merge and a final provenance check, the ignored `.migration-source` copy may be deleted locally. Retain or back up the external original until the user is satisfied that the canonical repository contains every needed artifact; deletion should be a separate explicit decision.
