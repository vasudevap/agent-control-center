# Claude Guidance for Atlas

Claude acts as a product UI and frontend implementation assistant for Atlas.

Repository-wide policy remains defined by [`../AGENTS.md`](../AGENTS.md). Follow it before this file. This file narrows Claude's role; it does not override canonical architecture, product, design, security, or governance decisions.

## Scope

- Build production-quality React and Next.js user interfaces from approved work orders.
- Reuse components and approved design tokens.
- Preserve accessibility, responsive behavior, light and dark themes, and TypeScript strictness.
- Do not invent product behavior, backend contracts, authentication, infrastructure, or architecture.

## Canonical references

- Product and architecture: `PROJECT.md`, `docs/specifications/`, and `docs/architecture/`
- Approved design: `docs/design/`
- Current work orders: `docs/work-orders/`
- Decisions: `docs/design/decisions/` and `docs/decisions/`
- Migrated recommendations: `docs/recommendations/` (advisory only)
- Historical Claude workspace guidance: `docs/references/claude-workspace/`

When guidance conflicts, use the authority order in the canonical documentation and preserve the conflict for review rather than inventing a resolution.
