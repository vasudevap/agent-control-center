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
