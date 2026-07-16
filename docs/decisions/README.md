# Decisions

Accepted architecture and design decisions outrank working guidance and recommendations.

- Approved design decision records live under `docs/design/decisions/`.
- `atlas-design-decision-log.md` is the migrated index from the former Claude implementation workspace.

The migrated index is preserved for provenance and does not create new architecture decisions.

## Architecture Decisions

- [`ADR-001 — Frontend Component Testing`](./ADR-001-frontend-component-testing.md) — Accepted; selects the development-time component-testing baseline required to resolve the Work Order 006 frontend testing gap.
- [`ADR-002 — Human Approvals Decision Integrity`](./ADR-002-human-approvals-decision-integrity.md) — Accepted; separates exact human authorization from execution and preserves explicit indeterminate outcomes.
- [`ADR-003 — Public Site Application and Hosting Boundary`](./ADR-003-public-site-application-boundary.md) — Accepted; establishes `apps/site` as an independently deployed public surface inside the Atlas monorepo.
