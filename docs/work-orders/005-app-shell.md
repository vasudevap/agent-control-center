# Work Order 005 — Application Shell

**ID:** APP-005
**Status:** Completed
**Priority:** P0
**Design Review:** Approved
**Final Review:** Passed
**Merge:** Completed

---

# Objective

Build the permanent Atlas application shell.

This shell becomes the foundation for every future screen.

Do not implement business logic.

---

# Read

1. CLAUDE.md
2. KNOWLEDGE.md
3. BOUNDARIES.md
4. recommendations/brand-identity-system.md
5. recommendations/color-palette.md
6. recommendations/icon-system.md
7. recommendations/design-tokens.md
8. recommendations/component-library.md

---

# Scope

## Build

- App Layout
- Sidebar
- Top Navigation
- Page Container
- Theme Provider
- Theme Toggle
- Breadcrumb Framework
- Global Search Placeholder
- Notification Placeholder
- Global Loading Shell
- Global Empty State
- Global Error Layout

## Create Placeholder Routes

- Overview
- Agents
- Agent Detail
- Runs
- Run Detail
- Approvals
- Alerts
- Connectors
- Policies
- Artifacts
- Audit
- Settings

Routes should render placeholder pages using the shared application shell.

---

# Requirements

- Next.js App Router
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Radix UI
- Lucide Icons

Use only approved design tokens and components.

No hardcoded colors, spacing or typography.

---

# Deliverables

Create production-ready code.

Provide:

1. Application shell
2. Routing structure
3. Shared layouts
4. Theme infrastructure
5. Navigation infrastructure

---

# Out of Scope

- Backend
- APIs
- Authentication
- Business logic
- Data fetching
- Mock dashboards

---

# Acceptance Criteria

- Every page renders inside the shell.
- Sidebar and top navigation are reusable.
- Theme switching works.
- Responsive behavior works.
- Layout is production ready.

Wait for review before implementing application features.

---

# Resolution

Implemented in full. Design Director review requested three minor refinements, all applied prior to merge:

1. Notification placeholder — `unreadCount` set to `0` (no fake unread state).
2. Agent/Run detail pages — stable titles ("Agent Details" / "Run Details"), with the route ID retained in the description and breadcrumb.
3. Global Search placeholder copy updated to communicate intended scope ("Search agents, runs, artifacts...").

Verification: `tsc --noEmit`, `eslint` (0 warnings), and `next build` all passed after the refinements, with no unintended changes. Full implementation record: [`reviews/handoff-005-app-shell.md`](../reviews/handoff-005-app-shell.md).

**Status: Completed. Design Review: Approved. Final Review: Passed. Merge: Completed.**

Per Design Director instruction, the next work order will not begin until it has been formally reviewed and approved.
