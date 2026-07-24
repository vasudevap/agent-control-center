# Atlas Repository Handoff

## Current Handoff Snapshot

As of 2026-07-24:

- ADP-006 has merged WO-064 through WO-070 for the Agent Visibility and
  Lifecycle MVP.
- Root `/` is the public Atlas landing page. The active authenticated product
  shell is rooted at `/control-center`.
- Active MVP navigation is limited to Overview, Agents, Executions, Alerts, and
  Activity under `/control-center`.
- Owner-enrolled agents use one-time Atlas telemetry credentials. Atlas accepts
  authenticated heartbeats and execution summaries, derives observed health,
  opens/resolves alerts, records material activity, and supports owner
  lifecycle actions: rotate credential, disconnect, reconnect, and archive.
- Atlas does not host, deploy, schedule, execute, pause, resume, stop, or
  maintain external agent runtimes.
- WO-071 is blocked. Hosted API readiness reports
  `agent_credential_pepper_missing` and
  `agent_credential_pepper_key_id_missing`; production Render environment
  values must be provisioned outside the repository before hosted
  reference-agent verification can complete.
- Do not record owner subject values, cookies, generated agent tokens, provider
  credentials, database URLs, or credential pepper values in source, logs,
  screenshots, pull requests, or chat.

Recommended orientation order:

1. `AGENTS.md`
2. `PROJECT.md`
3. `ROADMAP.md`
4. `docs/architecture/README.md`
5. `docs/decisions/README.md`
6. `docs/governance/README.md`
7. This handoff guide
8. `docs/implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md`
9. `docs/reviews/WO-071-hosted-reference-agent-verification-and-adp-closeout-blocker-report.md`

## Frontend Design and Maintenance Guide

This is the working guide for maintaining or extending the Atlas frontend. It
assumes the reader has reviewed the product and architecture sources listed
above. Read `design-principles.md` first; this document maps those rules onto the
code and the completed frontend surfaces.

## Running and verifying

From this folder's root:

    npm ci
    npm run dev        # Next.js dev server
    npm run typecheck  # tsc --noEmit
    npm run lint       # eslint
    npm run test       # Vitest: 80 passing tests across 17 files; no pending tests
    npm run build      # production build

All three checks pass on every commit on this branch. Keep it that way: every change lands only after typecheck, lint, and tests are green. When a change alters UI text or structure that a test asserts on, update the test in the same change.

## Layout of this folder

    apps/web/src/
      app/(shell)/            route pages for all completed frontend prototype surfaces
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

**PageHeader** (`components/layout/page-header.tsx`). Eyebrow / title / identifier chip / description at a compact rhythm; icon remains attached to the wrapping title group; `meta` is reserved for page-specific state/classification/safety context; `actions` holds small buttons. On mobile, description and meta precede actions so long object names and purpose retain a readable sequence.

**Shell**. Sidebar extends to the viewport top and owns the logo; three responsive tiers (hidden below `md`, compact rail with labels beneath icons at `md`, full horizontal icon-and-label rows at `lg`). The middle tier uses the vertical treatment so every label remains readable without taking substantial width from the workspace. The mobile drawer uses the full horizontal icon-and-label rows with section headings and badges, so navigation choices never depend on icon recognition. StatusBar holds the fleet pulse in three clusters (fleet, approvals, alerts) and shares the sidebar offset through the same wrapper as TopBar and main.

**SortHeader** (`components/ui/sort-header.tsx`). Shared mono column-header button with direction arrows. It exposes the announced sort direction for the active column and is used by both Agents and Approvals.

## Established design state, page by page

**Overview.** Answers "what requires my attention right now." Attention Queue merges pending approvals, alerts, and unhealthy agents into one urgency-ranked, actionable-header card; each row leads with a severity glyph, has a mono kind label (Approval / Alert / Agent health) and an urgency-colored timestamp on the trailing edge, and navigates to its real destination. Deliberately not sortable or filterable. Active Work and Upcoming Schedule are informational cards with title+description headers and tiled rows. A metrics row and fleet roster were removed as redundant with the status bar and Agents page.

**Agents.** Full inventory table. Columns: Health (leading, quiet inline icon + text, sortable), Agent (sortable, name + description + optional issue caption, stretched-link row), Status (quiet inline icon + text, sortable), Owner (sortable, `lg:` and up), Last run / Next run (sortable via `lastRunAt`/`nextRunAt` ISO fields; "Not scheduled" sorts last). Control bar holds search, status and health filters, and a clear button. Mobile uses the same quiet inline treatment for health and a contained pill for its Status field.

**Agent Detail.** Two-column grid: sticky aside (At a glance fact list with StatusBadge `plain` values, Capabilities as neutral tags; both cards use divided headers with descriptions) plus a tabbed main card (Activity / Human Approvals / Governance). Activity's execution history table uses icon+label run status, uniform `text-xs` cells. Governance ends with the System prompt reference disclosure (shaded trigger row). Header controls use explicit `Simulate pause/resume/run` labels and form a two-column action group below the description at narrow widths.

**Approvals.** Queue/History as underline tabs merged into the results panel header with a queue count chip. The page header reuses the exact Approvals icon exported by the navigation model. Control bar: search, Risk, a view-specific Review filter on Queue or State filter on History, and clear button. The agent filter was deliberately replaced; agent search still works through the text field. Table columns: Risk (leading, quiet inline geometric icon + text, sortable), Approval (sortable by attention rank; action + mono id/policy caption; stretched-link), Agent (sortable), Requested on Queue or Decided on History (both sortable), Expiry (sortable, urgency-colored), and Review on Queue (sortable, pictographic tag) or Outcome on History (State via StatusBadge `plain` + outcome caption). History rows also expose reason, reviewer, and correlation context. Mobile cards preserve state, risk, action, target, agent, identifier, expiry, review/outcome context, Queue request time, and History decision metadata. Queue defaults to attention ordering: expiry urgency first, then risk. History defaults to the newest explicit decision timestamp.

**Approval Detail.** Main column of InfoCards (Proposed action with a full-width payload summary, Policy rationale, Evidence and context with the untrusted-evidence callout, Activity timeline), sticky aside with the Decide card (shaded actionable header, simulation buttons, icon-carrying status lines) and Request context. The payload summary also appears in the final simulated-decision confirmation. Request context models Agent, Run, and optional Artifact relationships without linking unavailable prototype routes. Mobile keeps the Decide card inline after evidence, with no fixed shortcut covering content, and keeps Indeterminate investigation guidance in normal reading order. Dialogs enforce decision-specific required text, simulated step-up for high risk, focus containment, controlled expiry-at-confirmation behavior, and polite live announcements. Tall dialogs stay within the viewport and scroll internally.

**Runs.** Full local-fixture inventory with Search, Status, and Trigger controls; true-value sorting; semantic desktop table; mobile cards; and explicit prototype disclosure. Run Detail reuses the sticky-fact-aside skeleton and separates execution steps, normalized error context, operational log excerpts, approvals, and artifacts. Operational logs are explicitly not Audit records. Fixture timestamps are anchored to a deterministic reference so server and client markup remain identical.

**Artifacts.** Metadata-first local-fixture inventory and canonical Artifact Detail route. Lifecycle state uses `StatusBadge`; sensitivity is a neutral classification. Artifact Detail never renders or downloads content and represents external storage as unavailable. Canonical Agent, Run, Approval, and Artifact links exist only when the target fixture is implemented.

**Alerts.** Severity-led local-fixture inventory with Search, Severity, Status, and Source controls; true-value sorts; semantic desktop table; mobile cards; and inline details. Severity uses pictographic, labeled operational icons rather than the geometric risk vocabulary. Overview alert rows route to `/alerts?alert=<id>` and open the matching fixture detail. `Simulate investigation` changes only component-local display state and announces the reset-on-refresh boundary.

**Audit.** Read-only fictional governance history with Search, Action, Result, Actor, and Resource controls; true-value sorts; desktop table; mobile cards; and correlation details. The page explicitly states that its append-only-looking fixtures are not operational audit records or a system of record, and exposes no write, edit, delete, or export affordance.

**Connectors.** Local-fixture lifecycle inventory with search, Status and Authentication filters, true-value sorting for status, connector, authentication, account, and last check, semantic desktop table, complete mobile cards, declared capabilities/scopes disclosure, and explicit connection/reconnect/health-check/revoke simulations. Revocation uses the shared focus-managed dialog and no credential or secret field exists.

**Policies.** Local policy-declaration inventory with search, Status and Type filters, true-value sorting for status, policy, type/scope, and assigned-agent names, state vocabulary, scope, version, agent assignments, readable rule summaries, and explicit local enable/disable simulation. Summaries never claim evaluation or enforcement. Policy-level risk is intentionally omitted because the prototype does not define whether it would represent protected-action risk, control criticality, or change risk.

**Settings.** Session-only workspace, appearance, notification, scheduling, and retention preference form. Reset restores deterministic defaults; simulated save states that nothing was persisted or sent. The action area follows the final section in normal flow so it never covers mobile fields. The shell theme control remains the real local UI-theme mechanism, separate from the fictional appearance preference.

## Decision log

The rationale for each design decision is preserved in the archived branch history; every commit message describes one review round. Read `git log --oneline archive/gui-alternate-design` for the sequence. Several component docblocks (RiskChip, StatusBadge, CardHeader, AttentionQueue, PageHeader) also carry the reasoning inline where it matters most.

## Checklist for building a new page

1. Start from the closest existing page type: inventory (Agents/Approvals), detail (Agent/Approval Detail), or dashboard (Overview). Reuse its skeleton and spacing.
2. Use `PageHeader` with an eyebrow naming the section and a one-line description. Header buttons: `size="sm"`, sentence case.
3. Render every status through `StatusBadge`/`RiskChip`; never a color-only pill. New states get added to `STATUS_CONFIG` with an icon that collides with nothing else on the page.
4. Tables: severity column first if one exists; use the quiet inline icon + text treatment outside Overview; use `SortHeader` on every column that has a real underlying value; set `text-xs` on meta cells themselves; and use stretched-link rows.
5. Cards: `actionable` header only if every row navigates; `divided` header + `pt-3 sm:pt-3` content for quiet fact cards; always pair titles with descriptions.
6. Check both themes, all three sidebar tiers (`<md`, `md`, `lg`), and mobile card fallbacks for tables.
7. Run typecheck, lint, and tests before considering the work done; add or update tests for behavior you add.

## Known gaps and next candidates

All authorized Atlas frontend routes now have reviewed local-fixture prototype surfaces. Remaining product gaps are service-backed capabilities—including authentication, persistence, runtime, connectors, policy evaluation, notifications, scheduling, and audit durability—which require architecture and new authorized Work Orders. Fleet pulse numbers in the status bar remain static fixtures and do not yet link to filtered views.
