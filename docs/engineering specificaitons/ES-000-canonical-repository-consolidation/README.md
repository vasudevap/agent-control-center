# Atlas Codex Cleanup & Consolidation Specification Package

This package contains the complete engineering specification for asking Codex to clean up the current `agent-control-center` repository state and consolidate the standalone Atlas implementation work from `atlas-ai` into the existing canonical repository.

The intent is to let Codex perform the work autonomously while protecting:

- existing Git history;
- the current architecture and design documentation;
- the approved Work Order 005 frontend implementation;
- the original unversioned `atlas-ai` source material;
- product, UX, and architecture decisions already approved.

## Files

1. [`01-repository-protection-and-preparation.md`](./01-repository-protection-and-preparation.md)  
   Protects the existing repository, handles dirty/staged state, cleans accidental files, commits legitimate design baseline work, creates a safety tag, and prepares the migration workspace.

2. [`02-source-analysis-and-comparison.md`](./02-source-analysis-and-comparison.md)  
   Defines how Codex must compare `atlas-ui` and `claude`, identify the authoritative Work Order 005 frontend, and avoid union-copying duplicates.

3. [`03-canonical-repository-migration.md`](./03-canonical-repository-migration.md)  
   Defines the target canonical repository structure and how to migrate the approved frontend into `apps/web`.

4. [`04-workspace-and-build-configuration.md`](./04-workspace-and-build-configuration.md)  
   Defines npm workspace setup, dependency installation, root scripts, config repair, and forbidden build artifacts.

5. [`05-documentation-and-governance-migration.md`](./05-documentation-and-governance-migration.md)  
   Defines how to migrate work orders, reviews, decisions, recommendations, references, Claude-specific instructions, and source-of-truth rules.

6. [`06-verification-and-completion.md`](./06-verification-and-completion.md)  
   Defines required validation, route checks, responsive checks, report requirements, and completion criteria.

7. [`07-autonomous-execution-rules.md`](./07-autonomous-execution-rules.md)  
   Defines Codex autonomy, prohibited actions, stop conditions, commit rules, push rules, and safety constraints.

8. [`appendix-commands-checklists-deliverables.md`](./appendix-commands-checklists-deliverables.md)  
   Contains command references, migration checklist, final deliverables, and a manual review checklist.

9. [`CODEX-PROMPT.md`](./CODEX-PROMPT.md)  
   A ready-to-paste prompt for the Codex session.

10. [`CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION.md`](./CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION.md)  
   The assembled master specification containing all sections.

## Recommended use

Copy the assembled master file into the root of the existing canonical repository:

```text
/Users/pv/bootcamp/projects/agent-control-center/CODEX-ATLAS-CLEANUP-AND-CONSOLIDATION.md
```

Then open the `agent-control-center` folder in Codex and paste the contents of `CODEX-PROMPT.md`.

## Important operating principle

Codex should consolidate into the existing repository. It must not create a second repository, rewrite Git history, force-push, delete the external `atlas-ai` source folder, redesign approved UI, or start the next Work Order.
