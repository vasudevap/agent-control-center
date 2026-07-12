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
