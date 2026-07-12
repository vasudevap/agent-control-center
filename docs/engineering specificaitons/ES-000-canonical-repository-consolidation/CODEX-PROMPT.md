# Codex Prompt: Atlas Cleanup & Consolidation

Paste this into Codex after placing the assembled master specification in the root of the existing `agent-control-center` repository.

```text
Execute the complete autonomous cleanup and consolidation described in:

CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION.md

Start by inspecting the repository exactly as it currently exists. Do not assume the staged changes are disposable.

Follow the specification from beginning to end, including:

- preserving and committing the legitimate Atlas brand and product-design work currently staged or unstaged on main;
- safely resolving accidental files, including .DS_Store and the apparent ARCHITECTURE.md -> Metric rename;
- pushing the cleaned design baseline to main;
- creating and pushing the pre-consolidation safety tag;
- creating the consolidation branch;
- locating and copying the external atlas-ai source into the ignored .migration-source area;
- comparing atlas-ui and claude;
- selecting the authoritative Work Order 005 frontend using evidence;
- consolidating the frontend into apps/web;
- migrating essential work orders, reviews, decisions, recommendations, references, and Claude-specific instructions;
- configuring the npm workspace;
- running install, typecheck, lint, build, route, and available responsive verification;
- creating logical commits;
- pushing the consolidation branch;
- producing the required consolidation report;
- finishing with a clean working tree.

You are authorized to perform routine filesystem, Git, dependency-installation, configuration, validation, commit, tag, and push operations without asking me for approval.

Use safe and reversible actions when ambiguity exists. Preserve provenance and archive uncertain material rather than deleting it.

Do not:

- initialize another repository;
- rewrite Git history;
- force-push;
- alter existing tags;
- merge the consolidation branch into main;
- delete the external atlas-ai source;
- delete .migration-source;
- redesign the approved UI;
- add product features;
- begin the next Work Order.

Only stop for an unrecoverable blocker explicitly defined in the specification.

Continue autonomously until every completion criterion in the specification has been satisfied.
```

## Optional Codex CLI invocation

Use this only if you intentionally want fully unattended execution for this trusted repository:

```bash
codex \
  --cd /Users/pv/bootcamp/projects/agent-control-center \
  --sandbox danger-full-access \
  --ask-for-approval never \
  "$(cat <<'PROMPT'
Execute the complete autonomous cleanup and consolidation described in CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION.md.

Start by inspecting the repository exactly as it currently exists. Do not assume staged changes are disposable. Follow the specification from beginning to end. You are authorized to perform routine filesystem, Git, dependency-installation, configuration, validation, commit, tag, and push operations without asking me for approval. Use safe and reversible actions when ambiguity exists. Preserve provenance and archive uncertain material rather than deleting it. Do not initialize another repository, rewrite Git history, force-push, alter existing tags, merge the consolidation branch into main, delete the external atlas-ai source, delete .migration-source, redesign approved UI, add product features, or begin the next Work Order. Only stop for an unrecoverable blocker explicitly defined in the specification. Continue autonomously until every completion criterion has been satisfied.
PROMPT
)"
```
```
