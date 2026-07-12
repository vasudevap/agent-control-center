# CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION

## Master Engineering Specification

This master specification assembles the complete autonomous cleanup and consolidation instructions for Codex.

It is intended to be copied into the root of the existing canonical Atlas repository:

```text
/Users/pv/bootcamp/projects/agent-control-center/CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION.md
```

Codex should execute this specification end-to-end, preserving existing Git history, accepted architecture/design decisions, the approved Work Order 005 implementation, and the original external `atlas-ai` source material.

---

# 01. Repository Protection & Preparation

## Purpose

This section tells Codex how to safely begin the Atlas cleanup and consolidation work from the repository's current state.

The repository may currently have staged or unstaged changes, including:

- legitimate Atlas brand and product-design documentation;
- accidental macOS `.DS_Store` files;
- an apparent accidental `ARCHITECTURE.md -> Metric` rename;
- root-level documentation updates that may not yet be committed.

Codex must not assume staged changes are disposable. It must inspect, classify, preserve, clean, and commit correctly.

## Repository roles

The existing repository is the canonical Atlas repository:

```text
/Users/pv/bootcamp/projects/agent-control-center
```

The unversioned implementation source is external source material:

```text
/Users/pv/bootcamp/projects/atlas-ai
```

The external source will be copied into an ignored folder inside the repository only so Codex can inspect and migrate it:

```text
.migration-source/atlas-ai
```

The migration source is read-only source material. It must not become committed canonical content.

## Initial inspection

Codex must start with:

```bash
pwd
git status --short
git branch --show-current
git remote -v
find . -maxdepth 2 -name '.DS_Store' -print
```

Codex must inspect staged state before modifying it:

```bash
git diff --stat
git diff --cached --stat
git diff --name-status
git diff --cached --name-status
```

If a staged rename exists such as:

```text
ARCHITECTURE.md -> Metric
```

Codex must inspect both paths where possible:

```bash
ls -l ARCHITECTURE.md Metric 2>/dev/null || true
sed -n '1,120p' Metric 2>/dev/null || true
git show HEAD:ARCHITECTURE.md 2>/dev/null | sed -n '1,120p' || true
```

## Cleaning accidental files

Codex is authorized to remove generated or accidental local filesystem noise, including:

```text
.DS_Store
Thumbs.db
*.tmp
```

Codex must not remove meaningful project documents without first preserving or classifying them.

Remove macOS metadata files:

```bash
find . -name '.DS_Store' -type f -delete
```

Ensure `.DS_Store` is ignored:

```bash
grep -qxF '.DS_Store' .gitignore || printf '\n# macOS\n.DS_Store\n' >> .gitignore
```

## Handling the accidental `Metric` file

The project previously retired root `ARCHITECTURE.md` in favor of modular architecture documents under:

```text
docs/architecture/
```

If `Metric` is empty, accidental, or contains stale root `ARCHITECTURE.md` content, Codex should remove `Metric` and preserve the intended root `ARCHITECTURE.md` deletion.

If `Metric` contains unique meaningful content, Codex must archive it under:

```text
docs/references/archive/Metric.md
```

and document the provenance in the consolidation report.

Codex must not silently treat `Metric` as a canonical project document.

## Preserving legitimate design baseline work

The current staged or unstaged repository state may include legitimate completed work from the Brand Identity & Product Design stream. Codex must preserve and commit that baseline before migration.

Codex must identify and keep legitimate changes in areas such as:

```text
docs/design/
docs/specifications/
README.md
PROJECT.md
ROADMAP.md
AGENTS.md
```

Codex should commit legitimate current baseline documentation on `main` before creating the consolidation branch.

Recommended commit message:

```bash
git commit -m "docs(design): add Atlas brand and product design baseline"
```

If no legitimate baseline changes exist, Codex must document that in its report.

## Required state before branch creation

Before beginning consolidation, Codex must ensure:

- accidental `.DS_Store` files are removed;
- the `Metric` issue is resolved or archived;
- legitimate current baseline documentation is committed;
- `main` is clean;
- `main` is pushed to origin.

Expected command sequence after cleanup and classification:

```bash
git add -A
git status
git commit -m "docs(design): add Atlas brand and product design baseline" || true
git push origin main
git status --short
```

A clean `main` is required before creating a safety tag and consolidation branch.

## Safety tag

After `main` is clean and pushed, Codex must create a pre-consolidation annotated tag:

```bash
PREFLIGHT_TAG="pre-consolidation-$(date +%Y%m%d-%H%M%S)"
git tag -a "$PREFLIGHT_TAG" -m "Atlas state before canonical repository consolidation"
git push origin "$PREFLIGHT_TAG"
echo "$PREFLIGHT_TAG"
```

Codex must record the tag name in the final report.

## Consolidation branch

Codex must create and work on this branch:

```bash
git switch -c chore/canonical-repository-consolidation
```

If the branch already exists locally, Codex may switch to it after confirming it is the intended branch:

```bash
git switch chore/canonical-repository-consolidation
```

Codex must not do consolidation work directly on `main`.

## Ignore rules

Codex must ensure the following ignore rules exist:

```gitignore
# Temporary source material used during Atlas consolidation
.migration-source/

# Codex task logs and local execution artifacts
.codex-log/

# macOS
.DS_Store
```

Codex may de-duplicate `.gitignore` after editing.

## Migration source setup

Codex must verify the external source exists:

```bash
SOURCE="/Users/pv/bootcamp/projects/atlas-ai"
test -d "$SOURCE" && echo "Source found: $SOURCE" || echo "ERROR: atlas-ai source folder not found"
```

If not found, Codex may search likely nearby locations:

```bash
find /Users/pv -maxdepth 5 -type d -name atlas-ai 2>/dev/null | head -20
```

If the source cannot be located, Codex must stop and report the blocker.

When found, copy it into `.migration-source` excluding generated, dependency, cache, build, nested Git, and secret-bearing files:

```bash
mkdir -p .migration-source/atlas-ai
rsync -a \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='dist' \
  --exclude='build' \
  --exclude='coverage' \
  --exclude='.cache' \
  --exclude='.turbo' \
  --exclude='tsconfig.tsbuildinfo' \
  --exclude='.DS_Store' \
  --include='.env.example' \
  --exclude='.env*' \
  "$SOURCE/" \
  ".migration-source/atlas-ai/"
```

The external original source folder must remain untouched.

## Preparation commit

After establishing ignore rules and the migration specification, Codex should commit preparation changes if needed:

```bash
git add .gitignore CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION.md 2>/dev/null || true
git add docs/engineering-specifications 2>/dev/null || true
git commit -m "chore(repo): prepare canonical consolidation" || true
```

If the master specification is placed at root, Codex may keep it as a tracked engineering artifact or move it under:

```text
docs/engineering-specifications/ES-000-canonical-repository-consolidation.md
```

Codex must document the chosen location.

---

# 02. Source Analysis & Comparison

## Purpose

This section defines how Codex must analyze the unversioned Atlas implementation sources and determine which files are authoritative.

The migration source contains two substantive trees:

```text
.migration-source/atlas-ai/atlas-ui
.migration-source/atlas-ai/claude
```

The `claude` tree is provisionally expected to contain the final approved Work Order 005 implementation, but Codex must verify this through evidence.

## No union-copy rule

Codex must never combine both frontend application trees by simply copying everything. That would create inconsistent code, duplicate routes, conflicting configuration, and uncertain provenance.

Codex must compare first, select the authoritative frontend source, and migrate one coherent application into:

```text
apps/web
```

## Required source inventory

Codex must produce an inventory of both source trees.

Recommended commands:

```bash
find .migration-source/atlas-ai/atlas-ui -maxdepth 3 -type f | sort > .codex-log/atlas-ui-files.txt
find .migration-source/atlas-ai/claude -maxdepth 3 -type f | sort > .codex-log/claude-files.txt
```

Codex must inspect at least:

```text
package.json
package-lock.json
next.config.*
tsconfig.json
eslint.config.*
postcss.config.*
tailwind.config.*
components.json
app/
src/
public/
styles/
AGENTS.md
CLAUDE.md
README.md
BOUNDARIES.md
coding-standards.md
component-guidelines.md
project-structure.md
ui-standards.md
work_orders/
reviews/
decisions/
recommendations/
references/
output/
```

## Work Order 005 approval evidence

The authoritative frontend must preserve the approved Work Order 005 application shell implementation.

Codex must verify the selected frontend includes or can preserve:

- shared application shell;
- persistent Sidebar;
- persistent Top Navigation;
- `PageContainer` component;
- `Breadcrumb` component;
- Global Search placeholder component;
- Notifications placeholder panel;
- mobile navigation drawer;
- focus trap for the mobile navigation drawer;
- shared route-group architecture using a shell layout;
- shared loading boundary;
- shared error boundary;
- placeholder pages and routes.

Required routes:

```text
/
/agents
/agents/<test-id>
/runs
/runs/<test-id>
/approvals
/alerts
/connectors
/policies
/artifacts
/audit
/settings
```

Approved refinements that must be preserved:

1. Notifications placeholder must show zero unread items rather than fabricated unread notifications.
2. Agent detail page title must be `Agent Details`; IDs must be in supporting descriptions or breadcrumbs, not title text.
3. Run detail page title must be `Run Details`; IDs must be in supporting descriptions or breadcrumbs, not title text.
4. Search placeholder must read exactly:

```text
Search agents, runs, artifacts...
```

## Evidence checks

Codex should search for the approved signatures:

```bash
rg -n "Search agents, runs, artifacts|Agent Details|Run Details|zero unread|0 unread|focus trap|FocusTrap|mobile navigation|PageContainer|Breadcrumb" .migration-source/atlas-ai
```

Codex should inspect route files:

```bash
find .migration-source/atlas-ai -path '*app*' -type f | sort
find .migration-source/atlas-ai -path '*src*' -type f | sort | head -200
```

Codex should inspect package scripts:

```bash
node -e "for (const p of ['.migration-source/atlas-ai/atlas-ui/package.json','.migration-source/atlas-ai/claude/package.json']) { try { const j=require('./'+p); console.log('\n'+p); console.log(j.scripts); } catch(e) { console.log('missing', p) } }"
```

## Comparison dimensions

Codex must compare the application trees across these dimensions:

### Product behavior

- Which tree implements Work Order 005?
- Which tree includes approved refinements?
- Which tree has the required shell layout?
- Which tree has the required route placeholders?
- Which tree has the approved no-fake-notification state?

### Technical quality

- Which tree typechecks?
- Which tree lints?
- Which tree builds?
- Which tree has coherent package scripts?
- Which tree has fewer broken references?
- Which tree uses current design-system artifacts?

### Provenance

- Which tree contains work orders and review artifacts?
- Which tree contains final approval records?
- Which tree contains decisions and recommendations?
- Which tree appears to be an early scaffold?
- Which tree appears to be a final implementation workspace?

### Configuration

- Which tree has the most complete Next.js configuration?
- Which tree has correct TypeScript configuration?
- Which tree has correct styling and component configuration?
- Which tree has package-lock consistency?

## Expected finding

The expected finding is:

```text
.migration-source/atlas-ai/claude is the authoritative Work Order 005 implementation source.
```

But Codex must state whether it verified this and what evidence supports it.

## Handling non-authoritative frontend files

If `atlas-ui` contains useful unique files not present in `claude`, Codex may migrate them only if they are clearly safe, non-conflicting, and consistent with approved documentation.

Examples that may be worth preserving:

- unique static assets;
- safe `.env.example` content;
- additional documentation not superseded elsewhere.

Examples that should not be merged into the frontend automatically:

- alternate shell implementations;
- alternate route structures;
- conflicting design tokens;
- unapproved UX changes;
- stale package configuration;
- fake data not approved by work orders.

Uncertain material should be archived under:

```text
docs/references/archive/
```

with provenance notes.

## Required comparison report content

The final consolidation report must include:

- file inventory summary;
- authoritative frontend determination;
- evidence used to select the source;
- notable differences between `atlas-ui` and `claude`;
- files migrated from each tree;
- files archived;
- files discarded as generated, temporary, duplicate, or superseded;
- unresolved conflicts.

---

# 03. Canonical Repository Migration

## Purpose

This section defines the canonical repository structure and the migration rules for moving the approved Atlas frontend and supporting material into the existing repository.

The goal is to establish one clean, coherent Atlas repository while preserving the existing Git history and approved architecture/design baseline.

## Canonical repository rule

The repository containing the existing architecture and design documentation remains canonical.

Codex must not:

- create a second repository;
- run `git init`;
- replace `.git`;
- create a nested Git repository;
- rewrite history;
- force-push;
- modify existing tags;
- merge the consolidation branch into `main`.

## Target structure

Codex should establish this structure, using only folders justified by current material:

```text
agent-control-center/
├── .claude/
│   └── CLAUDE.md
├── apps/
│   └── web/
├── docs/
│   ├── architecture/
│   ├── design/
│   ├── specifications/
│   ├── engineering-specifications/
│   ├── work-orders/
│   ├── reviews/
│   ├── decisions/
│   ├── recommendations/
│   └── references/
├── AGENTS.md
├── PROJECT.md
├── ROADMAP.md
├── README.md
├── package.json
├── package-lock.json
└── .gitignore
```

Codex should not create empty speculative folders such as `services/`, `packages/`, or `infrastructure/` unless current material requires them. These can be introduced through future architecture decisions.

## Frontend destination

The approved Atlas frontend must live in:

```text
apps/web/
```

This location is chosen because Atlas is evolving toward a monorepo while currently containing one web app.

## Migration approach

Codex must perform a clean migration from the authoritative source application into `apps/web`.

Recommended approach:

1. Create `apps/web`.
2. Copy authoritative application files into `apps/web`.
3. Exclude generated files and dependencies.
4. Move package management to the repository root if adopting npm workspaces.
5. Repair configuration paths only as needed.
6. Validate from repository root.

## Files that must not be migrated

Do not migrate:

```text
node_modules/
.next/
dist/
build/
coverage/
.cache/
.turbo/
tsconfig.tsbuildinfo
.DS_Store
.env
.env.local
.env.production
.env.development
*.pem
*.key
```

Safe environment examples may be migrated:

```text
.env.example
.env.sample
```

Only if they do not contain secrets.

## Approved UI preservation

Codex must not redesign or refactor UI for preference.

The migration must preserve:

- application shell layout;
- sidebar behavior;
- top navigation behavior;
- global search placeholder;
- notification zero-unread state;
- mobile navigation drawer behavior;
- detail-page title refinements;
- placeholder route architecture;
- loading and error boundary placement;
- light and dark mode support if implemented;
- responsive behavior already approved.

Codex may make only migration-required technical changes, such as import paths, aliases, workspace scripts, and config repair.

## Import and path repair

After moving to `apps/web`, Codex must inspect and repair path references.

Common areas:

```text
tsconfig.json path aliases
components.json aliases
eslint config
postcss config
next.config.*
style imports
font imports
asset paths
public asset references
```

Codex should prefer minimal changes.

## Source references

No tracked file may reference:

```text
.migration-source/
atlas-ai/claude
atlas-ai/atlas-ui
/Users/pv/bootcamp/projects/atlas-ai
```

except the consolidation report, where source provenance references are expected.

Codex must verify with:

```bash
rg -n "\.migration-source|atlas-ai/claude|atlas-ai/atlas-ui|/Users/pv/bootcamp/projects/atlas-ai" . --glob '!CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION.md'
```

If references remain in source/config files, repair them.

## Static assets

Codex must migrate only assets required by the approved app or approved brand/design documentation.

Assets should live in:

```text
apps/web/public/
```

or, if they are documentation/design assets:

```text
docs/design/assets/
docs/references/assets/
```

Do not migrate large temporary screenshots or generated output unless they are explicitly referenced by approved documentation or final review records.

## Naming conventions

Keep existing approved names unless migration requires normalization.

Do not rename product concepts, routes, or navigation labels without explicit approval.

Approved product name:

```text
Atlas
```

Approved category framing:

```text
Enterprise Agent Control Center
AI Operations Platform
Unified control plane for AI workforces
```

## Cleanliness after migration

After migrating, the canonical repository should not contain:

- duplicate app trees;
- stale `atlas-ui` or `claude` folders outside `.migration-source`;
- nested package locks unless deliberately required;
- generated dependency/build output;
- secret-bearing environment files;
- conflicting root instructions.

## Git commit for frontend migration

Recommended commit message after migrating the app and before configuration repair if the repository is not buildable yet:

```bash
git commit -m "feat(web): migrate approved Atlas frontend implementation"
```

If separate commits would knowingly create a broken intermediate state, Codex may combine migration and config repair into one coherent commit and document why.

---

# 04. Workspace & Build Configuration

## Purpose

This section defines how Codex must configure the canonical repository so the migrated Atlas web application can be installed, checked, linted, and built reproducibly from the repository root.

## Preferred package strategy

The repository should use npm workspaces if this can be done without changing application behavior.

Preferred root `package.json` shape:

```json
{
  "private": true,
  "workspaces": [
    "apps/*"
  ],
  "scripts": {
    "dev": "npm --workspace apps/web run dev",
    "build": "npm --workspace apps/web run build",
    "lint": "npm --workspace apps/web run lint",
    "typecheck": "npm --workspace apps/web run typecheck"
  }
}
```

The exact scripts may vary based on the authoritative app's existing package scripts, but the root must expose at least:

```text
npm run build
npm run lint
npm run typecheck
```

If the app has a test script, expose:

```text
npm test
```

or:

```text
npm run test
```

## Lockfile strategy

Prefer one root `package-lock.json` generated by npm.

Codex must not hand-edit lockfiles.

If migrating from an app-level lockfile, Codex should:

1. move or preserve dependency declarations correctly;
2. run `npm install` or `npm ci` as appropriate;
3. let npm generate the canonical root lockfile;
4. avoid committing nested stale lockfiles unless required.

## Install commands

After workspace configuration, Codex must verify dependency installation from root.

Preferred:

```bash
npm ci
```

If `npm ci` cannot run because a lockfile does not yet exist or must be regenerated after migration, Codex may run:

```bash
npm install
```

Then it must run:

```bash
npm ci
```

again if feasible, proving reproducibility.

Codex must document which install command was used and why.

## Application package scripts

The `apps/web/package.json` should retain useful local scripts, such as:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "lint": "next lint or eslint .",
    "typecheck": "tsc --noEmit"
  }
}
```

Codex may adapt script commands to the app's Next.js and ESLint versions.

Do not remove scripts that are required by existing documentation or verification unless replacing them with equivalent root scripts.

## Next.js configuration

Codex must inspect `next.config.*` after moving to `apps/web`.

If Next.js output file tracing is needed for deployment from a monorepo, Codex may add or repair:

```js
outputFileTracingRoot
```

only when appropriate for the current Next.js version and deployment assumptions.

Do not introduce deployment-specific settings that are not needed for local build validation.

## TypeScript configuration

Codex must inspect:

```text
apps/web/tsconfig.json
```

and path aliases such as:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

The aliases must resolve correctly from `apps/web`.

Root TypeScript config may be added only if needed by workspace tooling.

## ESLint configuration

Codex must ensure linting runs from root and/or app folder.

If ESLint config depends on current working directory, Codex must repair it.

Do not disable rules merely to pass lint unless the rule is clearly incompatible with current tooling and the change is documented.

Do not silence legitimate TypeScript or accessibility issues created by migration.

## Styling configuration

Codex must inspect and repair as applicable:

```text
postcss.config.*
tailwind.config.*
app/globals.css
src/styles/*
components.json
```

If shadcn or Tailwind aliases are present, `components.json` must point to the correct paths after migration.

## Environment examples

Safe `.env.example` files may be migrated.

They must not contain secrets.

Codex should ensure environment examples are located where developers expect them, likely:

```text
apps/web/.env.example
```

or root `.env.example` if the whole repo will use shared env configuration later.

No real `.env` file may be copied or committed.

## Root README updates

If root scripts or structure change, Codex must update the root `README.md` with a short section explaining:

- app location;
- install command;
- dev command;
- validation commands;
- consolidation branch status if relevant.

Do not turn the README into a long migration report. The report belongs under `docs/reviews/`.

## Secret scan

Before committing, Codex must scan tracked and proposed files for likely secrets.

At minimum:

```bash
rg -n "(sk-[A-Za-z0-9]|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\s*=|refresh_token|access_token)" . --glob '!node_modules/**' --glob '!.migration-source/**'
```

If a likely secret is found, Codex must:

- not commit it;
- redact it in reports;
- document the path and issue category;
- stop only if the secret is already committed or cannot be safely removed.

## Required validation commands

From repository root:

```bash
npm ci
npm run typecheck
npm run lint
npm run build
```

If tests exist:

```bash
npm test
```

or the app-specific equivalent.

If a command fails because of migration path issues, Codex must diagnose and fix.

If a command fails because the approved source itself has pre-existing issues unrelated to migration, Codex must document the issue, preserve the source, and stop only if completion criteria cannot be met.

## Configuration commit

Recommended commit message:

```bash
git commit -m "chore(build): configure Atlas workspace and validation scripts"
```

Codex may combine with frontend migration if necessary to avoid knowingly broken intermediate commits.

---

# 05. Documentation & Governance Migration

## Purpose

This section defines how Codex must migrate and organize documentation, governance artifacts, reviews, work orders, decisions, recommendations, references, and Claude-specific instructions from the unversioned source into the canonical repository.

The goal is to preserve provenance and governance without letting temporary or tool-specific files override accepted architecture and product documentation.

## Authority order

When documentation conflicts exist, Codex must use this authority order:

1. Accepted architecture decision records
2. Canonical architecture documentation
3. Approved product and design specifications
4. Approved work orders
5. Accepted design or implementation decisions
6. Final review and handoff records
7. Recommendations and working guidance
8. Generated and temporary outputs

Recommendations must never silently replace accepted decisions.

Claude-specific instructions must never replace repository-wide `AGENTS.md` unless they clearly apply to all tools and are explicitly merged as general guidance.

## Target documentation structure

Use these destinations:

```text
docs/architecture/
docs/design/
docs/specifications/
docs/engineering-specifications/
docs/work-orders/
docs/reviews/
docs/decisions/
docs/recommendations/
docs/references/
docs/references/archive/
.claude/CLAUDE.md
```

## Work orders

Migrate authoritative work order files from source folders such as:

```text
.migration-source/atlas-ai/claude/work_orders/
.migration-source/atlas-ai/claude/work-orders/
```

to:

```text
docs/work-orders/
```

Preserve original filenames where sensible. If filenames use inconsistent casing or spacing, Codex may normalize them while preserving a note in the report.

Work Order 005 must be preserved and clearly discoverable.

If work order files contain implementation instructions and approval status, preserve those details.

## Reviews

Migrate review records from:

```text
reviews/
output/
```

where they contain actual design review, implementation review, final approval, or verification evidence.

Destination:

```text
docs/reviews/
```

At minimum, preserve records related to:

- Work Order 005 implementation review;
- design review refinements;
- final design approval;
- TypeScript, ESLint, build verification;
- responsive review;
- route verification if present.

If `output/` contains temporary scratch output, do not migrate it as authoritative documentation. Archive only material with durable value.

## Decisions

Migrate design and implementation decisions from:

```text
decisions/
```

to:

```text
docs/decisions/
```

Do not rewrite decisions into ADRs unless the source already follows ADR format. Codex may add an index file explaining status and provenance.

If decisions conflict with existing architecture, preserve both and document the conflict.

## Recommendations

Migrate recommendations from:

```text
recommendations/
```

to:

```text
docs/recommendations/
```

Recommendations are advisory. They are not binding unless later accepted through a work order, decision, or architecture document.

Codex should add a short `README.md` in `docs/recommendations/` if needed to clarify this status.

## References

Migrate durable reference material from:

```text
references/
```

to:

```text
docs/references/
```

Reference material may include:

- approved design reference notes;
- implementation reference examples;
- review evidence;
- diagrams;
- curated assets;
- supporting analysis.

Uncertain but potentially useful material should go under:

```text
docs/references/archive/
```

with a provenance note.

## Claude-specific instructions

The source may contain:

```text
CLAUDE.md
BOUNDARIES.md
coding-standards.md
component-guidelines.md
project-structure.md
ui-standards.md
```

Codex must classify these carefully.

Root `AGENTS.md` remains the repository-wide tool-neutral policy.

Claude-specific operational instructions belong in:

```text
.claude/CLAUDE.md
```

If Claude-specific files include generally useful standards, Codex may migrate them into:

```text
docs/references/
docs/recommendations/
```

or merge selected non-conflicting ideas into `AGENTS.md` only if they clearly apply to all implementation agents.

Codex must document any merge into `AGENTS.md`.

## Existing canonical docs

Codex must preserve existing canonical documents, including:

```text
PROJECT.md
README.md
ROADMAP.md
AGENTS.md
docs/architecture/
docs/design/
docs/specifications/
```

It may update these documents only to reflect the consolidated repository structure and current implementation baseline.

Do not rewrite product strategy, architecture, brand, or UX direction during consolidation.

## Status and provenance headers

For migrated governance files where status is unclear, Codex may add a brief header such as:

```md
> Migration note: This document was migrated from `.migration-source/atlas-ai/claude/...` during ES-000. Its authority is informational unless referenced by an approved work order, decision, or canonical specification.
```

Do not alter approved content in a way that changes meaning.

## Documentation conflicts

If two documents conflict, Codex must:

1. preserve both documents;
2. identify their source and likely status;
3. document the conflict in the consolidation report;
4. avoid inventing a new decision;
5. continue unaffected migration work.

Examples of conflicts:

- different navigation labels;
- different route inventory;
- conflicting design-system tokens;
- different product positioning;
- conflicting Claude and Codex instructions;
- old `Agent Control Center` wording versus updated `Atlas` positioning.

## Required documentation updates

Codex should update or create:

```text
docs/reviews/ES-000-consolidation-report.md
docs/work-orders/README.md
docs/reviews/README.md
docs/decisions/README.md
docs/recommendations/README.md
```

Only if useful and not already present.

The root `README.md` should include a concise current implementation section:

- `apps/web` contains the approved Atlas frontend shell baseline;
- Work Order 005 is consolidated;
- root commands for install/build/lint/typecheck;
- branch contains consolidation work pending review if still on branch.

## Governance migration commit

Recommended commit message:

```bash
git commit -m "docs(governance): migrate work orders reviews and decisions"
```

A separate commit may update root guidance:

```bash
git commit -m "docs(repo): align Atlas repository guidance"
```

---

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

---

# 07. Autonomous Execution Rules

## Purpose

This section defines Codex's autonomy, authority, constraints, prohibited actions, and stop conditions.

The user wants Codex to execute the cleanup and consolidation without routine supervision. This is allowed only within the constraints below.

## Role

Codex is the implementation and repository-consolidation engineer.

Codex is not acting as:

- product owner;
- design director;
- enterprise architect;
- UX decision-maker;
- release manager;
- repository owner.

Codex may implement approved decisions. It must not create new product, design, or architecture decisions.

## Authorized autonomous actions

Codex is authorized to perform these actions without asking for routine confirmation:

- inspect repository state;
- unstage files when needed for safe classification;
- remove generated local noise such as `.DS_Store`;
- classify current changes;
- preserve legitimate documentation work;
- commit legitimate baseline work;
- push `main` after preserving baseline work;
- create and push a pre-consolidation safety tag;
- create and switch to the consolidation branch;
- add ignore rules;
- copy the external `atlas-ai` source into `.migration-source`;
- inspect `.migration-source`;
- compare `atlas-ui` and `claude`;
- select the authoritative frontend based on evidence;
- create canonical folders;
- copy/move files into canonical locations;
- archive uncertain artifacts;
- update imports and configuration required by migration;
- configure npm workspaces;
- install dependencies;
- run typecheck, lint, build, and available tests;
- diagnose and fix migration-related build errors;
- update root README and guidance to reflect repository structure;
- create logical local commits;
- push the consolidation branch;
- create the consolidation report.

## Required safety posture

When ambiguity exists, Codex must choose the safest reversible action.

Preferred ambiguity resolution:

1. preserve;
2. archive;
3. document;
4. continue unaffected work.

Codex must not delete uncertain material merely because it appears redundant.

## Prohibited actions

Codex must not:

- run `git init`;
- replace or remove `.git`;
- create a nested Git repository;
- rewrite Git history;
- force-push;
- modify existing tags;
- merge the consolidation branch into `main`;
- create the final release tag;
- delete `.migration-source`;
- delete the external original `atlas-ai` folder;
- delete source material that has not been safely classified;
- commit real `.env` files;
- commit secrets;
- redesign approved UI;
- add product features;
- start Work Order 006 or any new implementation work;
- change accepted architecture;
- change product positioning;
- change approved brand/design decisions;
- silently replace root `AGENTS.md` with tool-specific instructions;
- use recommendations as accepted decisions;
- ignore failing verification;
- mark the task complete with a dirty working tree.

## Stop conditions

Codex should continue through routine issues. It should stop only for unrecoverable blockers.

Stop if:

- the canonical repository cannot be identified;
- `.git` metadata is corrupted;
- the external `atlas-ai` source cannot be located;
- both source application trees are missing or unusable;
- a likely real secret is already committed in Git history;
- required dependency installation cannot proceed after reasonable diagnosis;
- build cannot be made reproducible without redesigning or rewriting approved app behavior;
- a documentation conflict would require a new product, design, or architecture decision to proceed;
- credentials are required and unavailable;
- pushing the branch fails because of authentication or permission issues.

If stopping, Codex must create a blocker report if possible and leave the working tree in the safest state.

## Conflict handling

If documents conflict:

- preserve both;
- classify status and source;
- document the conflict;
- do not invent a resolution;
- continue unaffected consolidation.

If application source conflicts:

- choose the source that matches Work Order 005 approval evidence;
- preserve useful unique non-conflicting artifacts;
- archive uncertain material;
- document decisions.

## Design constraints

Codex must preserve the approved application shell and placeholder infrastructure.

Codex must not make visual decisions, such as:

- changing colors;
- changing typography;
- changing spacing;
- changing navigation labels;
- changing status language;
- adding mock data;
- changing layout density;
- replacing components for preference.

Only migration-required technical adjustments are allowed.

## Documentation constraints

Codex may update documentation to reflect consolidation facts.

Codex must not rewrite strategic documents into a new vision.

Approved positioning:

```text
Atlas is an enterprise-inspired AI Operations Platform and Agent Control Center that provides a unified control plane for AI workforces.
```

Approved audience framing:

```text
Professionals building and operating their own AI workforce who deploy and govern specialized AI agents, automations, and integrations, and are frustrated by operational complexity across disconnected tools, schedules, logs, credentials, approvals, and workflows.
```

## Commit discipline

Commits should be logical, reviewable, and not too large where avoidable.

Good commit examples:

```text
docs(design): add Atlas brand and product design baseline
chore(repo): prepare canonical consolidation
feat(web): migrate approved Atlas frontend implementation
chore(build): configure Atlas workspace and validation scripts
docs(governance): migrate work orders reviews and decisions
docs(repo): align Atlas repository guidance
docs(reviews): add ES-000 consolidation report
```

Avoid:

```text
misc
updates
fix
big changes
```

## Branch push

Codex is authorized to push:

```text
chore/canonical-repository-consolidation
```

to origin.

Codex must not push directly to `main` after the consolidation branch is created, except for the initial preservation of legitimate baseline work before branch creation.

## Final response requirements

When finished, Codex must summarize:

- authoritative frontend selected;
- where the app now lives;
- commits created;
- verification results;
- pushed branch;
- unresolved issues;
- manual actions remaining;
- recommendation on merge readiness.

The final response should be concise and point to the consolidation report for details.

---

# Appendix: Commands, Checklists & Deliverables

## A. Initial repository commands

```bash
cd /Users/pv/bootcamp/projects/agent-control-center
pwd
git status --short
git branch --show-current
git remote -v
```

## B. Clean accidental macOS files

```bash
find . -name '.DS_Store' -type f -delete
grep -qxF '.DS_Store' .gitignore || printf '\n# macOS\n.DS_Store\n' >> .gitignore
```

## C. Inspect accidental `Metric` state

```bash
git diff --name-status
git diff --cached --name-status
ls -l ARCHITECTURE.md Metric 2>/dev/null || true
sed -n '1,120p' Metric 2>/dev/null || true
git show HEAD:ARCHITECTURE.md 2>/dev/null | sed -n '1,120p' || true
```

## D. Preserve current legitimate baseline work

```bash
git add -A
git status
git commit -m "docs(design): add Atlas brand and product design baseline" || true
git push origin main
git status --short
```

## E. Create safety tag

```bash
PREFLIGHT_TAG="pre-consolidation-$(date +%Y%m%d-%H%M%S)"
git tag -a "$PREFLIGHT_TAG" -m "Atlas state before canonical repository consolidation"
git push origin "$PREFLIGHT_TAG"
echo "$PREFLIGHT_TAG"
```

## F. Create consolidation branch

```bash
git switch -c chore/canonical-repository-consolidation
```

## G. Add ignore rules

```bash
cat >> .gitignore <<'EOF'

# Temporary source material used during Atlas consolidation
.migration-source/

# Codex task logs and local execution artifacts
.codex-log/
EOF
awk '!seen[$0]++' .gitignore > .gitignore.tmp && mv .gitignore.tmp .gitignore
```

## H. Copy external source

```bash
SOURCE="/Users/pv/bootcamp/projects/atlas-ai"
test -d "$SOURCE" && echo "Source found: $SOURCE" || echo "ERROR: atlas-ai source folder not found"
mkdir -p .migration-source/atlas-ai
rsync -a \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='dist' \
  --exclude='build' \
  --exclude='coverage' \
  --exclude='.cache' \
  --exclude='.turbo' \
  --exclude='tsconfig.tsbuildinfo' \
  --exclude='.DS_Store' \
  --include='.env.example' \
  --exclude='.env*' \
  "$SOURCE/" \
  ".migration-source/atlas-ai/"
```

## I. Validate source copy

```bash
test -d .migration-source/atlas-ai/atlas-ui && echo "atlas-ui copied" || echo "atlas-ui missing"
test -d .migration-source/atlas-ai/claude && echo "claude copied" || echo "claude missing"
find .migration-source -type d \( -name node_modules -o -name .next -o -name dist -o -name build -o -name coverage \) -print
```

## J. Source comparison searches

```bash
mkdir -p .codex-log
find .migration-source/atlas-ai/atlas-ui -maxdepth 3 -type f | sort > .codex-log/atlas-ui-files.txt
find .migration-source/atlas-ai/claude -maxdepth 3 -type f | sort > .codex-log/claude-files.txt
rg -n "Search agents, runs, artifacts|Agent Details|Run Details|zero unread|0 unread|focus trap|FocusTrap|mobile navigation|PageContainer|Breadcrumb" .migration-source/atlas-ai
```

## K. Required final validation

```bash
npm ci
npm run typecheck
npm run lint
npm run build
npm test || true
```

## L. Secret scans

```bash
rg -n "(sk-[A-Za-z0-9]|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\s*=|refresh_token|access_token)" . --glob '!node_modules/**' --glob '!.migration-source/**'
git ls-files | rg '(^|/)\.env(\.|$|local|production|development)' || true
```

## M. Required final deliverables

Codex must leave behind:

```text
apps/web/
docs/work-orders/
docs/reviews/
docs/decisions/
docs/recommendations/
docs/references/
.claude/CLAUDE.md
docs/reviews/ES-000-consolidation-report.md
```

Expected branch:

```text
chore/canonical-repository-consolidation
```

Expected final state:

```bash
git status --short
```

returns no output.

## N. Manual review checklist after Codex finishes

The user should manually review:

- GitHub branch diff;
- `docs/reviews/ES-000-consolidation-report.md`;
- `apps/web` app structure;
- root `package.json` and workspace setup;
- route rendering in browser;
- light/dark responsive screenshots if available;
- migrated work orders and reviews;
- no unwanted `.migration-source` content committed;
- no secrets committed;
- merge readiness.

## O. Manual actions Codex must not perform

- Merge branch into `main`.
- Delete `.migration-source`.
- Delete external `/Users/pv/bootcamp/projects/atlas-ai`.
- Create release tag.
- Start Work Order 006.
- Redesign UI.
- Change product/architecture decisions.
