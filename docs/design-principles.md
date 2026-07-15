# Atlas GUI Design Principles

These principles were established and validated iteratively across every page of this prototype. They are not aspirational; each one is already applied consistently in the code, and each exists because violating it produced a concrete, observed problem during review. When extending Atlas with new pages, treat these as binding conventions unless a documented decision supersedes them.

The companion document, `handoff.md`, maps these principles to the specific components and pages that implement them.

## Typography

### 1. Mono, uppercase, tracked type is structural, never content

The small uppercase letter-spaced monospace treatment (`font-mono text-[11px] font-semibold uppercase tracking-[0.08em]`) marks UI scaffolding: card titles, section headings, table column headers, nav labels, eyebrows, legends, identifiers, and kind labels. It never appears on content values such as names, dates, descriptions, or numbers. If a string is user data rather than interface chrome, it gets a plain readable font. Eyebrows use a slightly tighter size and wider tracking (`text-[10px] tracking-[0.14em]`).

### 2. One font treatment per row or column of values

Every value in a given table column, and every sibling value in a given row, uses the same font treatment. A monospace date next to a plain-font name in one row, or one field styled differently from its neighbors in a repeated list, reads as a bug. Identity columns (agent name, approval action) may sit at `text-sm font-medium` while meta columns (owner, timestamps, expiry, review state) sit at `text-xs text-foreground-secondary`, but within each column the treatment is uniform.

### 3. Set the font size on the table cell, not only on its content

When a cell's inner element carries `text-xs` but the `<td>` itself inherits the table's larger ambient size, the cell's line-height no longer matches its content and that cell's content rides visibly lower or higher than its siblings in the same row. Always put the size class on the cell. This exact misalignment was found and fixed three separate times (Approvals Expiry and Review columns, Agent Detail Status column), so check for it whenever adding a table column.

### 4. Sentence case everywhere

Button labels, dialog titles, empty states, and descriptions use sentence case ("Pause agent", "Run now", "Clear filters"), never Title Case. The only all-caps text is the structural mono treatment from principle 1.

## Color and state

### 5. State is never communicated by color alone

Every status, risk, or outcome indicator pairs an icon with its color. A label is added when space allows and dropped only in dense layouts (tables, compact lists) where the legend carries the vocabulary. A colored pill with no icon is not an acceptable state indicator anywhere.

### 6. One shared status vocabulary

All entity states render through `StatusBadge` (`components/badge/status-badge.tsx`), which owns the icon, color, and label for every `AtlasStatus`: health (healthy, degraded, offline), run state (running, active, paused, queued), and approval state (pending, approved, rejected, expired, cancelled). Do not build ad-hoc colored pills with the generic `Badge` component for states. `expired` and `cancelled` are deliberately neutral-colored, since neither is inherently a bad outcome.

`StatusBadge` has three render modes, chosen by context:
- default pill (icon + label + tinted background/border) for standalone placement, such as mobile card fields;
- `iconOnly` (bare colored glyph + `sr-only` label) for dense table columns, always with a visible legend nearby;
- `plain` (icon + colored label, no pill) for fact lists and header meta rows where a filled pill would read as a different kind of element than its plain-text siblings. `plain` inherits font size from context, so set an explicit size (e.g. `text-xs`) when siblings have one.

### 7. Urgency coloring for time

Time-based fields stay `text-foreground-secondary`/`tertiary` until urgent: nearing expiry is `font-semibold text-warning`, imminent or expired is `font-semibold text-error`. This rule is identical wherever expiry appears (Approvals table, Attention Queue, Approval Detail).

## Icons

### 8. Geometric shapes belong exclusively to risk

The risk vocabulary is Circle (Low), Triangle (Medium), TriangleAlert (High), Diamond filled (Critical). These bare geometric primitives are reserved: no other indicator on any page may use a plain geometric shape, or it will be misread as a risk level. Review progress uses pictographic icons for exactly this reason (Inbox for Unopened, Eye for In review, MessageCircleQuestion for Awaiting information, Ban for Blocked). Unopened was originally a Circle and had to be changed after it collided with Low risk.

### 9. One icon, one meaning per page

An icon may not mean two different things within one screen. Examples enforced in code: the caption line under a degraded agent's name carries no AlertTriangle because the health indicator beside the name already uses that glyph for "degraded"; Rejected owns XCircle, so Cancelled uses Undo2 and Expired uses History.

### 10. Icon-only indicators are bare and optically balanced

An indicator without a visible label drops its pill background and border entirely, becoming a colored glyph. Glyph sizes are compensated per shape, because triangles occupy less of their bounding box than circles, diamonds, or crosses: the default is `size-[11px]` with triangle-based glyphs at `size-[13px]`. This compensation lives in the config objects (`RISK_CONFIG`, `STATUS_CONFIG`), not at call sites.

### 11. Icon-only columns require a legend

Wherever a table or list column shows bare glyphs, the vocabulary legend appears once in that surface's control bar or card header, right-aligned, in `text-[10px] text-foreground-tertiary`, hidden below `sm:`. See the Agents control bar (health + status vocabularies separated by a divider) and the Approvals results panel (risk vocabulary).

## Cards

### 12. Actionable cards look different from informational cards

A card whose rows navigate somewhere gets the shaded header (`CardHeader actionable`: `bg-surface-secondary` + `border-b border-border-default`). A card that is only read keeps a plain header. A card earns the shaded treatment only if every row in it is genuinely, fully clickable.

### 13. Quiet informational cards get the divided header

`CardHeader divided` draws a hairline rule (`border-b border-border-subtle`, no background tint) under the header of a read-only card whose body has no bordered structure of its own (bare fact lists, tag wraps). It is a weaker signal than `actionable` and must never be combined with it. Content below a divided header sits 12px under the rule; note that `CardContent` bakes in `sm:pt-0`, so the override must be `pt-3 sm:pt-3`, not `pt-3` alone.

### 14. No bare hanging card titles

Every card title is paired with a one-line `CardDescription`. A lone mono title with nothing under it reads as unfinished next to cards that have the pairing.

### 15. Interactive styling implies a real destination

Pills, chips, and tags that look clickable (brand color, interactive borders) are only used when something actually happens on click. Static descriptors (capabilities, connectors) use `Badge variant="neutral"`.

## Tables and lists

### 16. Full-row clickability via the stretched link

Table rows and list items that navigate are made fully clickable with exactly one real anchor per row: `relative` on the row, `relative z-10 after:absolute after:inset-0 after:content-['']` on the anchor. Never nest multiple links per row or wrap a `<tr>` in an anchor.

### 17. Severity leads the row

In any listing where rows carry a severity-class signal (risk, health), that indicator is the first column, icon-only, with its own sortable column header. Approvals leads with Risk; Agents leads with Health; Attention Queue rows lead with the severity glyph.

### 18. Inventories sort; triage feeds do not

Full inventories of one entity type (Agents, Approvals) make every column sortable through the shared `SortHeader` pattern (mono header text, ArrowUp/ArrowDown when active, dimmed ArrowUpDown otherwise; clicking an active column flips direction). Pre-ranked, mixed-type triage feeds (Attention Queue) keep a fixed urgency order and no filters: the ranking is the value the surface provides, so it is not user-reorderable.

### 19. Sorting requires real data underneath

Columns sort on true values, never on display strings. Human-readable time strings ("8 minutes ago", "Tomorrow 6:00 AM") are paired with ISO timestamp fields (`lastRunAt`, `nextRunAt`, `requestedAt`, `expiresAt`) and sorts compare the timestamps. Unscheduled/absent values sort to the end regardless of direction. If a new column has no sortable underlying value, either add the value to the data or leave the column unsortable; do not sort the label text.

### 20. No redundant restatement

The same fact does not appear twice on one screen, or on a screen and a persistent surface simultaneously. This removed: the Overview metrics row (duplicated the status bar), the Overview fleet roster (duplicated the Agents page), and Agent Detail's header health/status pills (duplicated the At-a-glance card). When two surfaces need related information, one holds the canonical rendering and the other links to it.

## Page structure

### 21. Compact identity-first page headers

`PageHeader` renders eyebrow, title, optional inline identifier chip, then description, at a uniform `gap-1` rhythm; the icon sits in its own column so eyebrow, title, and description share one left edge. Trailing meta chips (risk, state, review) render at `text-xs` to match one another.

### 22. Equivalent page types share structure

Pages serving the same role share layout: both detail pages (Agent, Approval) use the fact-panel-plus-main-content grid with a sticky aside (`sticky top-[calc(var(--statusbar-height)+var(--topbar-height)+1rem)]`). A new detail page should reuse this skeleton, not invent a third.

### 23. Shared dimensions come from CSS variables

Structural measurements referenced by more than one component are defined once as custom properties (`--sidebar-width`, `--sidebar-width-collapsed`, `--statusbar-height`, `--topbar-height`) and consumed via `var()` everywhere, including in Tailwind arbitrary values. Never restate these numbers.

### 24. Disclosure triggers look interactive

Collapsible sections (System prompt reference) style the trigger row with `bg-surface-secondary` plus `hover:bg-surface-hover` so it is visibly distinct from static headings that share the same typography. A chevron with `rotate-180` on open is the secondary cue; the background is the primary one.

### 25. Header buttons are small and sentence-cased

Action buttons inside `PageHeader` use `size="sm"` and sentence case, matching their siblings. Confirmation dialogs reuse the same labels as their triggers.
