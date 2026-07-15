# Atlas Frontend Design: Designer Handoff

This is the working guide for continuing the Atlas frontend design. It assumes you know the product from the main project's documentation; nothing here covers product behavior, objectives, or architecture. Read `design-principles.md` first; this document maps those rules onto the code and tells you how to build the remaining pages.

## Running and verifying

From this folder's root:

    npm install
    npm run dev        # Next.js dev server
    npm run typecheck  # tsc --noEmit
    npm run lint       # eslint
    npm run test       # Vitest: 49 passing tests across 8 files; no pending tests

All three checks pass on every commit on this branch. Keep it that way: every change lands only after typecheck, lint, and tests are green. When a change alters UI text or structure that a test asserts on, update the test in the same change.

## Layout of this folder

    apps/web/src/
      app/(shell)/            route pages: overview (page.tsx), agents/, approvals/, runs/, plus placeholder routes
      components/ui/          primitives: card, button, badge, table, dialog, tooltip, search-field, skeleton
      components/badge/       StatusBadge (the single status vocabulary)
      components/risk/        RiskChip + riskRank (the risk vocabulary)
      components/layout/      PageHeader, Sidebar, StatusBar, TopBar, DashboardLayout, MobileNavDrawer
      components/state/       EmptyState, ErrorState
      features/overview/      Overview page sections and fixtures
      styles/                 tokens.css (design tokens; all shared dimensions live here)

## Component inventory

**Card** (`components/ui/card.tsx`). `CardTitle` is globally the structural mono treatment. `CardHeader` takes `actionable` (shaded band: card contents navigate) or `divided` (hairline rule: quiet read-only card). `CardContent` bakes in `sm:pt-0`, so headers with a rule need `pt-3 sm:pt-3` on the content.

**StatusBadge** (`components/badge/status-badge.tsx`). Owns icon + color + label for every status: healthy, degraded, offline, running (spinning loader), active, paused, queued, pending, approved, rejected, expired, cancelled. Modes: pill (default), `iconOnly`, `plain`. Per-glyph optical size compensation lives in `STATUS_CONFIG`.

**RiskChip** (`components/risk/risk-indicator.tsx`). Risk pill or `iconOnly` glyph for Low/Medium/High/Critical; `riskRank` for sorting. The geometric shapes here are reserved for risk alone.

**Approval badges** (`app/(shell)/approvals/approval-badges.tsx`). `ReviewProgressTag` (pictographic icon + label, never icon-only), `reviewRank`, `StateChip` (maps approval state into StatusBadge `plain`), `ExpiryLabel` (urgency coloring).

**PageHeader** (`components/layout/page-header.tsx`). Eyebrow / title / identifier chip / description at `gap-1`; icon in its own column; `meta` slot for chips; `actions` slot for small buttons. On mobile, actions and meta stack below the identity content so long object names retain a readable width.

**Shell**. Sidebar extends to the viewport top and owns the logo; three responsive tiers (hidden below `md`, compact rail with labels beneath icons at `md`, full horizontal icon-and-label rows at `lg`). The middle tier uses the vertical treatment so every label remains readable without taking substantial width from the workspace. The mobile drawer uses the full horizontal icon-and-label rows with section headings and badges, so navigation choices never depend on icon recognition. StatusBar holds the fleet pulse in three clusters (fleet, approvals, alerts) and shares the sidebar offset through the same wrapper as TopBar and main.

**SortHeader** (`components/ui/sort-header.tsx`). Shared mono column-header button with direction arrows. It exposes the announced sort direction for the active column and is used by both Agents and Approvals.

## Established design state, page by page

**Overview.** Answers "what requires my attention right now." Attention Queue merges pending approvals, alerts, and unhealthy agents into one urgency-ranked, actionable-header card; each row leads with a severity glyph, has a mono kind label (Approval / Alert / Agent health) and an urgency-colored timestamp on the trailing edge, and navigates to its real destination. Deliberately not sortable or filterable. Active Work and Upcoming Schedule are informational cards with title+description headers and tiled rows. A metrics row and fleet roster were removed as redundant with the status bar and Agents page.

**Agents.** Full inventory table. Columns: Health (leading, icon-only, sortable), Agent (sortable, name + description + optional issue caption, stretched-link row), Status (icon-only, sortable), Owner (sortable, `lg:` and up), Last run / Next run (sortable via `lastRunAt`/`nextRunAt` ISO fields; "Not scheduled" sorts last). Control bar holds search, status and health filters, both icon legends, and a clear button. Mobile renders cards with labeled field pairs.

**Agent Detail.** Two-column grid: sticky aside (At a glance fact list with StatusBadge `plain` values, Capabilities as neutral tags; both cards use divided headers with descriptions) plus a tabbed main card (Activity / Human Approvals / Governance). Activity's execution history table uses icon+label run status, uniform `text-xs` cells. Governance ends with the System prompt reference disclosure (shaded trigger row). Header actions: Back link, Pause/Resume agent, Run now, all `size="sm"`, sentence case, with confirmation dialogs.

**Approvals.** Queue/History as underline tabs merged into the results panel header with a queue count chip. The page header reuses the exact Approvals icon exported by the navigation model. Control bar: search, Risk, a view-specific Review filter on Queue or State filter on History, risk legend, and clear button. The agent filter was deliberately replaced; agent search still works through the text field. Table columns: Risk (leading, icon-only, sortable), Approval (sortable by attention rank; action + mono id/policy caption; stretched-link), Agent (sortable), Requested on Queue or Decided on History (both sortable), Expiry (sortable, urgency-colored), and Review on Queue (sortable, pictographic tag) or Outcome on History (State via StatusBadge `plain` + outcome caption). History rows also expose reason, reviewer, and correlation context. Mobile cards preserve state, risk, action, target, agent, identifier, expiry, review/outcome context, Queue request time, and History decision metadata. Queue defaults to attention ordering: expiry urgency first, then risk. History defaults to the newest explicit decision timestamp.

**Approval Detail.** Main column of InfoCards (Proposed action with a full-width payload summary, Policy rationale, Evidence and context with the untrusted-evidence callout, Activity timeline), sticky aside with the Decide card (shaded actionable header, simulation buttons, icon-carrying status lines) and Request context. The payload summary also appears in the final simulated-decision confirmation. Request context models Agent, Run, and optional Artifact relationships without linking unavailable prototype routes. Mobile gets the decision card inline plus a fixed bottom bar and keeps Indeterminate investigation guidance in normal reading order. Dialogs enforce decision-specific required text, simulated step-up for high risk, focus containment, controlled expiry-at-confirmation behavior, and polite live announcements. Tall dialogs stay within the viewport and scroll internally.

## Decision log

The rationale for each design decision is preserved in the archived branch history; every commit message describes one review round. Read `git log --oneline archive/gui-alternate-design` for the sequence. Several component docblocks (RiskChip, StatusBadge, CardHeader, AttentionQueue, PageHeader) also carry the reasoning inline where it matters most.

## Checklist for building a new page

1. Start from the closest existing page type: inventory (Agents/Approvals), detail (Agent/Approval Detail), or dashboard (Overview). Reuse its skeleton and spacing.
2. Use `PageHeader` with an eyebrow naming the section and a one-line description. Header buttons: `size="sm"`, sentence case.
3. Render every status through `StatusBadge`/`RiskChip`; never a color-only pill. New states get added to `STATUS_CONFIG` with an icon that collides with nothing else on the page.
4. Tables: severity column first if one exists; `SortHeader` on every column that has a real underlying value; `text-xs` on meta cells themselves; stretched-link rows; legend in the control bar for any icon-only column.
5. Cards: `actionable` header only if every row navigates; `divided` header + `pt-3 sm:pt-3` content for quiet fact cards; always pair titles with descriptions.
6. Check both themes, all three sidebar tiers (`<md`, `md`, `lg`), and mobile card fallbacks for tables.
7. Run typecheck, lint, and tests before considering the work done; add or update tests for behavior you add.

## Known gaps and next candidates

Alerts, Runs, Artifacts, Audit, Connectors, Policies, and Settings exist as routes but are placeholders (PlaceholderPage) or have not been through this review process; they are the pages to build next, using the checklist above. Fleet pulse numbers in the status bar are static fixtures and do not yet link to filtered views.
