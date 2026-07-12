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
