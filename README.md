# Atlas GUI: Alternate Design Direction

This is a frontend-only design prototype for Atlas, the agent control center. It lives on the branch `codex/gui-alternate-second-opinion`, based off the canonical repository at commit `5f4a5a8`. It exists to establish and demonstrate the visual and interaction design for Atlas; product behavior, backend contracts, and governance are defined by the documentation on `main`, not here.

## Quick start

    npm install
    npm run dev

Then open the printed local URL. `npm run typecheck`, `npm run lint`, and `npm run test` must all pass before any change is considered done.

## Where to look

- `docs/design-principles.md` defines the binding design conventions, each grounded in a specific problem found and fixed during review.
- `docs/handoff.md` explains what exists page by page, the shared component inventory, how the work evolved, and a checklist for building the remaining pages.
- `apps/web/src/` is the implementation; several core components carry docblocks explaining the reasoning behind their design.

## What this is not

No real agents, runtimes, services, policy engines, or audit systems are contacted. All data is fictional fixture data and every mutating control is an explicit local simulation. Nothing on this branch is production-ready.
