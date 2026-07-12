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
