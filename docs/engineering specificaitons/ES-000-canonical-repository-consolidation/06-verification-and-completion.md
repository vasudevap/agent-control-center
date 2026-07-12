# 06. Verification & Completion

## Purpose

This section defines the required validation and completion criteria for ES-000.

Codex must not consider the consolidation complete until the repository is clean, the application builds, Work Order 005 behavior is preserved, and the consolidation report is complete.

## Required command verification

From repository root, Codex must run:

```bash
npm ci
npm run typecheck
npm run lint
npm run build
```

If tests exist, run them:

```bash
npm test
```

or the appropriate root/app test script.

Codex must record each command, result, and any meaningful remediation in:

```text
docs/reviews/ES-000-consolidation-report.md
```

## Route verification

Codex must verify these routes in the migrated application:

```text
/
/agents
/agents/test-agent
/runs
/runs/test-run
/approvals
/alerts
/connectors
/policies
/artifacts
/audit
/settings
```

If route conventions use a different dynamic segment value, Codex may use equivalent test IDs.

Verification may be performed through:

- existing tests;
- Next.js build output inspection;
- local production server plus HTTP requests;
- Playwright if already available;
- manual browser/screenshot checks if an existing tool is already configured.

Do not add a new browser-testing dependency solely for this migration unless required by existing project standards.

## Work Order 005 behavior verification

Codex must verify and record evidence for:

- Sidebar persists across placeholder routes;
- Top Navigation persists across placeholder routes;
- `PageContainer` is used consistently;
- Breadcrumbs appear in shell/page structure;
- Search placeholder reads exactly `Search agents, runs, artifacts...`;
- Notifications do not fabricate unread items;
- notification state is zero unread or equivalent placeholder state;
- `/agents/<test-id>` page title is `Agent Details`;
- `/runs/<test-id>` page title is `Run Details`;
- dynamic IDs are supporting text, description, breadcrumb, or metadata rather than primary title text;
- mobile drawer opens and closes;
- Escape closes the mobile drawer;
- focus moves into the drawer;
- focus is trapped while open;
- focus returns to the trigger when closed;
- shared loading boundary remains inside shell context;
- shared error boundary remains inside shell context;
- placeholder routes use shared infrastructure rather than isolated bespoke layouts.

## Responsive verification

Codex must perform available responsive verification at these widths:

```text
1440 px
1024 px
768 px
375 px
```

For both:

```text
light theme
dark theme
```

If automated responsive verification is not available, Codex must still document what could be verified from existing CSS/layout structure and what remains as a manual visual check.

## Secret verification

Codex must scan proposed tracked files for likely secrets.

Minimum scan:

```bash
rg -n "(sk-[A-Za-z0-9]|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\s*=|refresh_token|access_token)" . --glob '!node_modules/**' --glob '!.migration-source/**'
```

Codex must also verify that no real `.env` files are tracked:

```bash
git ls-files | rg '(^|/)\.env(\.|$|local|production|development)'
```

Safe `.env.example` files are allowed if they contain no secrets.

## Migration-source reference verification

No tracked source/config documentation should accidentally depend on the ignored migration source.

Codex must run:

```bash
rg -n "\.migration-source|atlas-ai/claude|atlas-ai/atlas-ui|/Users/pv/bootcamp/projects/atlas-ai" . --glob '!CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION.md'
```

Expected allowed references:

- ES-000 specification;
- consolidation report;
- migration provenance notes.

References inside app source, package configuration, build config, or root instructions must be removed or rewritten.

## Git verification

Codex must verify:

```bash
git status --short
git branch --show-current
git log --oneline --decorate -10
git remote -v
```

Completion requires a clean working tree after all commits.

Expected branch:

```text
chore/canonical-repository-consolidation
```

Codex must push this branch:

```bash
git push -u origin chore/canonical-repository-consolidation
```

Codex must not merge the branch into `main`.

## Required consolidation report

Codex must create:

```text
docs/reviews/ES-000-consolidation-report.md
```

The report must include these sections:

```md
# ES-000 Consolidation Report

## Summary

## Initial Repository State

## Cleanup Performed

## Safety Tag

## Migration Branch

## Source Material Location

## Source Comparison Summary

## Authoritative Frontend Determination

## Frontend Migration Summary

## Documentation and Governance Migration Summary

## Files Archived

## Files Discarded or Excluded

## Configuration Changes

## Dependency and Workspace Changes

## Secret Scan Results

## Verification Results

## Route Verification

## Responsive Verification

## Work Order 005 Behavior Verification

## Git Commits Created

## Final Git Status

## Unresolved Issues

## Manual Actions Remaining

## Merge Recommendation

## Recommendation on Original Source Folders
```

## Required commits

Codex should create logical commits equivalent to:

1. `docs(design): add Atlas brand and product design baseline` if legitimate baseline work was pending on `main`;
2. `chore(repo): prepare canonical consolidation`;
3. `feat(web): migrate approved Atlas frontend implementation`;
4. `chore(build): configure Atlas workspace and validation scripts`;
5. `docs(governance): migrate work orders reviews and decisions`;
6. `docs(repo): align Atlas repository guidance`;
7. `docs(reviews): add ES-000 consolidation report`.

Codex may combine commits when separation would create a broken intermediate state.

Codex must document actual commits created.

## Completion state

ES-000 is complete only when:

- legitimate current design/product documentation is preserved and committed;
- accidental `.DS_Store` files are removed and ignored;
- accidental `Metric`/`ARCHITECTURE.md` state is resolved or archived;
- a pre-consolidation safety tag exists and is pushed;
- consolidation work occurs on `chore/canonical-repository-consolidation`;
- external `atlas-ai` source is copied into ignored `.migration-source`;
- authoritative frontend source is identified using evidence;
- approved app is migrated into `apps/web`;
- root install/build/lint/typecheck commands exist;
- `npm ci` succeeds;
- `npm run typecheck` succeeds;
- `npm run lint` succeeds;
- `npm run build` succeeds;
- Work Order 005 behavior is preserved;
- essential governance/documentation artifacts are migrated;
- no tracked app/config file depends on `.migration-source`;
- no secrets are committed;
- consolidation report is complete;
- all changes are committed locally;
- consolidation branch is pushed to origin;
- working tree is clean.

## Manual actions after completion

Codex must leave these manual actions for the user:

1. Review `docs/reviews/ES-000-consolidation-report.md`.
2. Review the GitHub branch diff.
3. Merge `chore/canonical-repository-consolidation` into `main` if satisfied.
4. Decide whether to delete or retain the external original `atlas-ai` folder.
5. Decide whether to delete `.migration-source` after the branch is merged and the external source is no longer needed.
6. Create the next release tag if desired.

Codex must not perform these manual actions unless explicitly instructed later.
