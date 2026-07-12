# Definition of Ready

A Work Order or Engineering Specification is ready only when the review owner confirms the following items as applicable:

- The objective, intended outcome, owner, and approved scope are explicit.
- Acceptance criteria are observable and testable.
- Out-of-scope behavior is explicit.
- Canonical architecture, ADR, product, design, and DDR references are linked.
- Dependencies, prerequisites, sequencing, and external constraints are identified.
- Security, privacy, trust-boundary, permission, and secret-handling considerations are addressed.
- Data ownership, migrations, retention, and integration contracts are addressed.
- UI flows, loading/empty/error/disabled states, accessibility, themes, and responsive behavior are specified where relevant.
- The verification plan identifies commands, tests, manual reviews, and required evidence.
- A review owner is named.
- Unresolved decisions are resolved, assigned to an ADR/DDR or follow-up, or explicitly accepted with risk and a revisit trigger.

Work that fails a relevant item returns to refinement; implementation does not invent the missing decision.
