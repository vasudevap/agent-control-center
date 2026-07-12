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
