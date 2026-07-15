# Atlas Frontend Design Direction (atlas-gui-alt)

This subfolder is the frontend design workspace for Atlas. It is a git worktree on the branch `codex/gui-alternate-second-opinion`, nested inside the main project repository. Product background, objectives, specifications, architecture, and governance live in the main project; nothing here restates them. This folder carries only the frontend design direction: the working mockup app, the design rules established during its review, and the instructions a designer needs to continue the work.

## Contents

- `apps/web/` is the working mockup. It is the primary design reference: every established convention is applied in this code, and core components carry docblocks explaining the reasoning where it matters.
- `docs/design-principles.md` is the binding rulebook: 25 conventions covering typography, color and state, icons, cards, tables, and page structure.
- `docs/handoff.md` is the working guide: component inventory, the established design state of each page, the decision log, and a checklist for building the remaining pages.

## Quick start

    npm install
    npm run dev

`npm run typecheck`, `npm run lint`, and `npm run test` must all pass before any change is considered done.

All data in the mockup is local fixture data; no real service is contacted and every mutating control is a local simulation.
