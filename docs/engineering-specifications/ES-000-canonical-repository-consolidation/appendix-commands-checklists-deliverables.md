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
