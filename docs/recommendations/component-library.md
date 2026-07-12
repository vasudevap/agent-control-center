# Atlas Core Component Library — Recommendation

**Work Order:** COMPONENT-004
**Status:** Proposed — awaiting review
**Depends on:** [`brand-identity-system.md`](brand-identity-system.md), [`color-palette.md`](color-palette.md), [`icon-system.md`](icon-system.md), [`design-tokens.md`](design-tokens.md) — all four are unchanged by this document.

This document is a specification only. No application code has been written. These become, on approval, the only approved building blocks for future screens — no new component should be introduced outside this set without a corresponding update here first.

---

## How to Read This Document

Each component is marked **Implemented** (already shipped in the Overview Dashboard — this section formalizes its existing spec) or **Proposed** (named in Work Order 004 but not yet built — this section is a full design spec for the upcoming implementation pass). Nothing marked Proposed exists in code yet.

| # | Component | Category | Status |
|---|---|---|---|
| 1 | Sidebar | Navigation | Implemented |
| 2 | Top Navigation | Navigation | Implemented |
| 3 | Breadcrumb | Navigation | Proposed |
| 4 | Page Header | Content | Implemented |
| 5 | Section Header | Content | Proposed |
| 6 | Metric Card | Content | Implemented |
| 7 | Status Badge | Content | Implemented |
| 8 | Alert Card | Content | Implemented |
| 9 | Empty State | Content | Implemented |
| 10 | Loading Skeleton | Content | Implemented |
| 11 | Data Table | Data | Partially implemented (primitives exist; wrapper is proposed) |
| 12 | Table Toolbar | Data | Proposed |
| 13 | Table Pagination | Data | Proposed |
| 14 | Button | Inputs | Implemented |
| 15 | Icon Button | Inputs | Formalized usage pattern of Button (not a new component — see §15) |
| 16 | Search Field | Inputs | Proposed |
| 17 | Filter Chip | Inputs | Proposed |

**Global compliance:** every component below uses tokens exclusively (no raw hex, no arbitrary spacing outside the closed scale in `design-tokens.md` §2), is built with flex/grid (no absolute-positioning layout hacks except where explicitly noted — e.g. the Sidebar's active-state accent bar), supports both themes via the existing semantic tokens, and targets WCAG 2.2 AA. Naming decisions from `design-tokens.md` (including **Primary Accent (Temporary)** in place of any permanent brand-color name, "Degraded" unchanged, "Offline" unchanged) are carried forward unmodified here.

---

## Navigation

### 1. Sidebar

**Purpose:** Primary, persistent wayfinding for the entire product — the fixed left rail on desktop, a slide-in drawer on smaller viewports.

**Anatomy:** Container (`aside`, fixed, `w-(--sidebar-width)`) → logo mark (brand-solid chip + wordmark) → nav item list (icon + label + optional count badge) → separator → Settings item (visually identical to a nav item, pinned below the separator).

**Variants:**
- **Desktop rail** — always visible ≥1024px, `position: fixed`
- **Mobile drawer** (`MobileNavDrawer`) — overlay + scrim, <1024px, reuses the identical `SidebarNav` content

**States:** Default · Hover (`hover:bg-surface-hover`) · Focus-visible (2px ring) · Active/current-route (`bg-brand-subtle` + `text-brand` + 2px left accent bar) · Disabled (reserved — not currently exercised by any nav item, but the pattern should follow Button's disabled treatment: reduced opacity, `pointer-events-none`, no href)

**Props:**
| Component | Props |
|---|---|
| `Sidebar` | none (self-contained) |
| `SidebarNav` | `onNavigate?: () => void` — called on link click, used by the drawer to close itself |
| `MobileNavDrawer` | `open: boolean`, `onClose: () => void` |

**Accessibility:** `aside[aria-label="Sidebar"]` and `nav[aria-label="Primary"]` landmarks; `aria-current="page"` on the active link; drawer is `role="dialog" aria-modal="true"`, closes on Escape and scrim click. **Known gap:** the drawer does not currently trap focus (Tab can escape to the dimmed background content) — flagged here as a defect to fix in the same pass this component library is implemented, not a new requirement.

**Responsive behavior:** Rail hidden entirely <1024px; drawer is the only access to navigation below that breakpoint, triggered from Top Navigation's menu button.

**Usage guidance:** Exactly one Sidebar per app shell. The nav item list is centrally defined (`nav-items.ts`) and must stay in sync with `icon-system.md`'s concept→icon table — never hardcode a nav item inline in a screen.

**Do:** Extend the shared nav item list when new sections are added. Keep the flat, single-level structure.
**Don't:** Don't add a second navigation rail. Don't recolor individual nav icons. Don't nest nav items (no expandable sub-menus) — that would be a structural change requiring its own work order.

---

### 2. Top Navigation

**Purpose:** Persistent utility bar for global, non-page-specific actions.

**Anatomy:** Sticky header → mobile nav toggle (hidden ≥1024px) → flexible spacer → theme toggle → alert bell (with unread-count dot) → user menu (avatar + name + dropdown).

**Variants:** Single variant — no alternate layouts.

**States:** Default · Hover (per control) · Focus-visible · Active/open (user-menu dropdown expanded, via Radix `DropdownMenu` state)

**Props:** None currently — the component is self-contained with hardcoded user identity ("Operator" / "operator@atlas.dev") and a hardcoded unread count (2). **Recommendation for the implementation pass:** parameterize `unreadAlertCount: number` and `user: { name: string; email: string; initials: string }` so this stops being mock-data-in-the-component and becomes mock-data-passed-as-props — a small but real improvement to reusability. This is a recommendation, not a requirement.

**Accessibility:** Every icon-only control has an explicit `aria-label` (`"Open navigation"`, `"Alerts, 2 unread"`, `"User menu"`). The dropdown is built on Radix primitives, which supplies keyboard navigation, roving focus, and Escape-to-close for free.

**Responsive behavior:** Menu toggle appears only <1024px. User name label hides <640px, leaving just the avatar.

**Usage guidance:** One per app shell, always paired with Sidebar — Top Navigation's mobile menu button is the only trigger for the Sidebar's drawer variant.

**Do:** Keep every icon-only button labeled. Keep the header's backdrop-blur subtle (`bg-surface/95`, not a heavier glass effect — no glassmorphism per `ui-standards.md`).
**Don't:** Don't add more utility clusters beyond nav-toggle / theme+alerts / user-menu without revisiting information density first.

---

### 3. Breadcrumb — *Proposed*

**Purpose:** Communicates location within a nested hierarchy on screens deeper than one level (e.g., a future Agents → Agent Detail → Run screen). Not needed on the single-level Overview Dashboard, which is why it doesn't exist yet.

**Anatomy:** `<nav><ol>` of crumb items joined by a `ChevronRight` (size-3.5, `text-foreground-tertiary`) separator. All crumbs except the last are links; the last is plain text representing the current page.

**Variants:** Single variant, with an automatic **Truncated** state (see States) — no separate variant prop needed.

**States:** Default · Hover/Focus (linked crumbs only — underline on hover, focus ring) · Truncated (when the path exceeds ~4 levels or available width, middle crumbs collapse into a `…` trigger that opens a `DropdownMenu` listing the hidden crumbs — reusing the existing Dropdown Menu primitive rather than inventing a new disclosure pattern)

**Props (proposed):**
```
items: { label: string; href?: string }[]
```
The final item's `href`, if present, is ignored — the current page is never a link.

**Accessibility:** `nav[aria-label="Breadcrumb"]` wrapping a semantic `<ol>`; current page carries `aria-current="page"`; the truncation trigger is a real button, keyboard-operable via the existing Dropdown Menu primitive.

**Responsive behavior:** Below `sm`, collapses to a single "back" affordance (`← {previous crumb label}`) rather than showing the full trail — avoids horizontal crowding on narrow screens without needing horizontal scroll.

**Usage guidance:** Place directly above `PageHeader`, never inside a card. Only appears on screens with real hierarchy — a screen reachable directly from the Sidebar with no further nesting should not have a single-item breadcrumb (that's a redundant "You are here: X" — just use Page Header alone).

**Do:** Keep crumb labels short (route names, not full entity titles). Truncate deep paths via the dropdown pattern.
**Don't:** Don't make the current page a link. Don't use this for in-page tab navigation — that's a different, out-of-scope pattern.

---

## Content

### 4. Page Header

**Purpose:** The single, page-level title block — one per screen.

**Anatomy:** Title (`<h1>`) + optional description paragraph, stacked; optional trailing `actions` slot (buttons), right-aligned at desktop width.

**Variants:** With/without `description`; with/without `actions`.

**States:** Static — no interactive states of its own; any interactivity lives in the `actions` slot's own components (e.g., a `Button`).

**Props:**
```
title: string
description?: string
actions?: ReactNode
className?: string
```

**Accessibility:** Renders the page's one and only `<h1>`. If a screen ever includes a `Section Header` (below), that must render as `<h2>`, never a second `<h1>`.

**Responsive behavior:** Stacks title/description above actions on mobile (`flex-col`); moves to a row with actions right-aligned ≥640px.

**Usage guidance:** Exactly one per screen, at the top of the content area, above everything else (or below a `Breadcrumb`, if the screen has one).

**Do:** Keep the title short — this is a page name, not a sentence.
**Don't:** Don't add a second `Page Header` lower on the same screen — use `Section Header` for in-page groupings instead.

---

### 5. Section Header — *Proposed*

**Purpose:** Introduces a cluster of cards within a screen that has more than one logical zone. The current Overview Dashboard is single-zone (one `Page Header`, then all cards belong to one implicit "overview" zone), so this hasn't been needed yet — a future Agents or Runs screen with, say, a "Fleet" zone and a "History" zone on the same page would use one `Section Header` per zone.

**Anatomy:** Identical shape to `Page Header` — title + optional description + optional trailing actions — one type-scale tier down (`Section Title`, per `design-tokens.md` §1, not `H1`).

**Variants:** With/without description; with/without actions — mirrors Page Header exactly.

**States:** Static, same as Page Header.

**Props (proposed):**
```
title: string
description?: string
actions?: ReactNode
className?: string
```
Deliberately the same shape as `PageHeader` so the two components are structurally interchangeable — only the rendered heading level and type scale differ.

**Accessibility:** Renders `<h2>`. A screen may have multiple `Section Header`s (multiple `<h2>`s) beneath its single `Page Header` `<h1>`.

**Responsive behavior:** Same stacking rule as Page Header.

**Usage guidance:** Use only when a screen has ≥2 distinct zones needing their own label. Do not use on a single-zone screen — Page Header alone is sufficient there, exactly as today's Overview Dashboard demonstrates.

**Do:** Reuse Page Header's prop shape exactly, to keep the two predictable and swappable.
**Don't:** Don't use Section Header in place of a Card's own `CardTitle` — Card Title labels one card; Section Header labels a zone containing several cards.

---

### 6. Metric Card

**Purpose:** Displays a single quantified KPI, with the number as the dominant visual element (per `brand-identity-system.md` §2).

**Anatomy:** Card → label (mono, uppercase, small, top) → value (large, Inter, semibold) → optional trend indicator (arrow + mono delta) → icon chip (top-right, secondary in visual weight).

**Variants (`tone` prop):** `default` (neutral chip — used when the number itself isn't a status, e.g. "Total Agents") · `success` · `warning` · `error` — chip tint only; typography treatment is identical across all tones.

**States (`state` prop):** `success` (default/populated) · `loading` (skeleton label + skeleton value + skeleton chip, `aria-busy="true"`) · `error` (compact error layout: error-tinted chip + label + short error message, no value shown).

**Props:**
```
label: string
value: string | number
icon: LucideIcon
trend?: { direction: "up" | "down"; value: string; tone?: "positive" | "negative" | "neutral" }
tone?: "default" | "success" | "warning" | "error"
state?: "success" | "loading" | "error"
errorMessage?: string
className?: string
```

**Accessibility:** Icon is `aria-hidden="true"` (the label text already conveys meaning); loading state sets `aria-busy="true"` on the card.

**Responsive behavior:** Value text scales from `text-4xl` to `text-5xl` at `sm` and above; grid placement (1/2/4 columns) is the parent `MetricsRow`'s responsibility, not the card's own.

**Usage guidance:** Reserve `success`/`warning`/`error` tones for numbers that genuinely represent a status (e.g., "Healthy Agents," "Pending Approvals"); use `default` (neutral) for plain counts (e.g., "Total Agents," "Running Agents") — this is the concrete rule that keeps the dashboard from reading as "every icon is a different color for no reason."

**Do:** Keep the number the largest, boldest element on the card, always.
**Don't:** Don't color the icon chip decoratively. Don't shrink the value's type size to make room for a longer label — wrap or truncate the label instead.

---

### 7. Status Badge

**Purpose:** Compact, reusable indicator of Operational or Decision status (see `brand-identity-system.md` §1 for the full state taxonomy — unchanged by this document, including "Degraded" and red "Offline").

**Anatomy:** Pill (`rounded-full`) → icon (size-3.5) → label text.

**Variants (`status` prop):** `healthy` · `degraded` · `offline` · `running` (spinning icon) · `queued` · `pending` · `approved` · `rejected` — each maps to one fixed icon + color pairing per the existing `STATUS_CONFIG` table; no ad hoc combinations are permitted.

**States:** The badge itself has no interactive states (it's not clickable) — its only "state" axis is which `status` value is passed in. `running` is the sole variant with a motion state (icon spin).

**Props:**
```
status: AtlasStatus
className?: string
```

**Accessibility:** Icon is `aria-hidden="true"`; the label text is the accessible name — status is never conveyed by color/icon alone.

**Responsive behavior:** None needed — fixed-size inline element.

**Usage guidance:** Always pair with the label text (never render an icon-only status indicator). Use directly in table cells and list rows exactly as Fleet Health and Active Runs already do.

**Do:** Use the existing status vocabulary as-is.
**Don't:** Don't introduce a new status value without updating `brand-identity-system.md` first — this component's variant list must stay a closed, centrally-defined set.

---

### 8. Alert Card

**Purpose:** Displays a single alert/notification with severity, title, description, timestamp, and source.

**Anatomy:** Row → severity icon chip (left) → title + timestamp (top row, space-between) → description → optional source label.

**Variants (`severity` prop):** `critical` (`AlertOctagon`, error tint) · `warning` (`AlertTriangle`, warning tint) · `information` (`Info`, info tint).

**States:** Static display component — no hover/focus/active states of its own (it is not currently clickable; if a future screen makes alerts clickable/dismissible, that's a scope addition requiring its own spec update, not an implicit extension of this one).

**Props:**
```
severity: "critical" | "warning" | "information"
title: string
description: string
timestamp: string
source?: string
className?: string
```

**Accessibility:** Severity icon `aria-hidden="true"`; title and description are plain text, fully readable by assistive tech in document order.

**Responsive behavior:** Fixed layout — title truncates with `truncate` rather than wrapping, to keep the timestamp always visible on the same line.

**Usage guidance:** One `Alert Card` per alert, stacked in a list (as in the Overview Dashboard's Alerts section) — never grid-laid-out.

**Do:** Keep title short enough to avoid truncation in the common case.
**Don't:** Don't use a severity color anywhere else in the same card (e.g., don't also tint the description text) — the icon chip alone carries the severity signal.

---

### 9. Empty State

**Purpose:** Placeholder shown when a section has no data to display.

**Anatomy:** Centered column → icon in a neutral circular chip (size-10 container, `rounded-full`) → title → optional description → optional trailing `action` slot.

**Variants:** Determined entirely by the `icon` prop — each section supplies its own contextual icon (e.g., `ServerCog` for Fleet Health, `BellOff` for Alerts) per `icon-system.md`'s mapping table; there is no separate "variant" axis beyond that.

**States:** Static — this *is* a state (the empty state of some other component), not a component with its own further states.

**Props:**
```
icon?: LucideIcon  // defaults to Inbox
title: string
description?: string
action?: ReactNode
className?: string
```

**Accessibility:** Icon `aria-hidden="true"`; title/description are plain readable text.

**Responsive behavior:** None required — content reflows naturally in its centered column.

**Usage guidance:** Used inside any section (card, table, list) that can legitimately have zero items — not a page-level 404/error pattern (that's out of scope for this component).

**Do:** Always pair with a specific, contextual icon and a short, actionable title.
**Don't:** Don't use the generic `Inbox` default when a more specific icon exists in the concept→icon mapping — the default exists only as a fallback for genuinely generic cases.

---

### 10. Loading Skeleton

**Purpose:** Placeholder shown while a section's real content is still arriving.

**Anatomy:** A single rounded block (`bg-surface-tertiary`, `animate-pulse`) — width/height are set per call site via `className` to approximate the shape of the content it stands in for (a text line, a table row, an icon chip).

**Variants:** None as a prop — shape is entirely composed via `className` at each call site (this is intentional; see Do/Don't).

**States:** Only one — pulsing. There is no static/paused variant.

**Props:**
```
className?: string  // extends standard div attributes
```

**Accessibility:** The `Skeleton` element itself carries no ARIA; the **containing region** must set `aria-busy="true"` while skeletons are shown (this is already the pattern in `MetricCard`'s loading state and should be treated as a hard requirement for every future use, not an optional nicety).

**Responsive behavior:** None intrinsic — inherits whatever width/height classes are applied per instance.

**Usage guidance:** Compose multiple `Skeleton` blocks to approximate a section's real layout (e.g., Fleet Health's loading state renders five full-width skeleton rows; Metric Card's loading state renders a label-shaped and a value-shaped block plus a chip-shaped block).

**Do:** Always set `aria-busy="true"` on the parent region while skeletons are visible.
**Don't:** Don't add shimmer/gradient sweep animation — the plain `animate-pulse` treatment is the ceiling for loading motion, per `brand-identity-system.md` §4.

---

## Data

### 11. Data Table

**Purpose:** Structured, scannable display of operational, row-based data (agents, runs, approvals, etc.). The underlying primitives (`Table`, `TableHeader`, `TableRow`, `TableHead`, `TableBody`, `TableCell`) already exist and are in production use (Fleet Health). This section formalizes those primitives and specifies a **proposed** higher-level `DataTable` composition that wires them together with sorting affordance, and optional Table Toolbar/Table Pagination — the composition itself is not yet built.

**Anatomy:** Scroll container (`overflow-x-auto`) → `<table>` → header row (mono, uppercase, `h-11`) → body rows (`py-3.5`, hover fill, `border-subtle` divider) → optional footer (Table Pagination, see §13).

**Variants:** Single density — "comfortable-compact" as already shipped (`py-3.5` row height). No alternate density is recommended; a denser or looser variant would fragment the system for no stated need.

**States:** Default · Row hover (`hover:bg-surface-hover`) · Loading (skeleton rows, as Fleet Health already implements) · Empty (`EmptyState` rendered in place of the table body) · Error (proposed — reuse `ErrorState` in place of the table body, mirroring how Metric Card handles its own error state; not yet implemented at the table level).

**Props (proposed, for the not-yet-built `DataTable` wrapper — the existing primitives' props are unchanged):**
```
columns: { key: string; header: string; sortable?: boolean }[]
rows: T[]
state?: "default" | "loading" | "empty" | "error"
sortColumn?: string
sortDirection?: "asc" | "desc"
onSort?: (column: string) => void
```
Sorting/filtering *logic* belongs to the screen that owns the data (per BOUNDARIES.md — Claude does not own data/API concerns); this component only owns the **visual affordance** of a sortable header (a small `Chevron` indicator on the active sort column) and the callback contract.

**Accessibility:** Already-semantic `<table>` markup is preserved; a sortable `TableHead` gets `aria-sort="ascending" | "descending" | "none"`.

**Responsive behavior:** Existing horizontal-scroll container is kept as the baseline. A card-per-row fallback for narrow viewports is worth considering for a future, denser table but is **not required now** — Overview's Fleet Health table already scrolls acceptably within the mobile scope defined for this dashboard (monitoring + approvals).

**Usage guidance:** Use the raw primitives directly for simple, non-sortable tables (as Fleet Health does today). Reach for the proposed `DataTable` wrapper only when a screen needs sorting, a toolbar, or pagination — don't wrap simple tables in it unnecessarily.

**Do:** Keep mono/uppercase headers and `border-subtle` dividers on every table, wrapper or not.
**Don't:** Don't add zebra-striping — row hover is the only row-level visual treatment this system uses.

---

### 12. Table Toolbar — *Proposed*

**Purpose:** The control row above a Data Table — search, filters, and table-level actions.

**Anatomy:** Single flex row → left cluster (Search Field, one or more Filter Chips) → right cluster (primary/secondary action buttons).

**Variants:** Composed per-use from its children — no toolbar-level variant prop. A toolbar with just a Search Field, just Filter Chips, or both is equally valid.

**States:** The toolbar container itself is static; all state lives in its children (Search Field's focus state, Filter Chip's active state, etc.).

**Props (proposed):** Slot-based rather than a rigid data prop:
```
children: ReactNode  // composed from Search Field / Filter Chip / Button
className?: string
```

**Accessibility:** No additional semantics beyond what its children already provide individually.

**Responsive behavior:** Wraps to two stacked rows below `sm` (search+filters row, then actions row) rather than compressing controls horizontally.

**Usage guidance:** Sits directly above the Data Table it controls, inside the same Card.

**Do:** Keep to one row of controls at desktop width.
**Don't:** Don't stack more than two rows of controls — a table needing more belongs under its own `Section Header` with a dedicated controls area instead.

---

### 13. Table Pagination — *Proposed*

**Purpose:** Page-through control for a Data Table whose row count exceeds one screen.

**Anatomy:** Single row, space-between → left: "Showing X–Y of Z" (Metadata tier, mono) → right: Previous Icon Button, current-page indicator, Next Icon Button.

**Variants:** Simple Prev/Next (the only variant currently justified by any screen's data volume). A numbered-page variant is not recommended until a specific screen's row count actually demands it — speculative complexity otherwise.

**States:** Default · Previous disabled (on page 1) · Next disabled (on the last page).

**Props (proposed):**
```
page: number
pageSize: number
total: number
onPageChange: (page: number) => void
```

**Accessibility:** `nav[aria-label="Pagination"]`; Previous/Next are real, labeled buttons (`aria-label="Previous page"` / `"Next page"`), never bare unlabeled icons.

**Responsive behavior:** Hides the "Showing X–Y of Z" text below `sm`; Previous/Next controls remain.

**Usage guidance:** Sits directly below the Data Table it controls, inside the same Card, as a natural footer.

**Do:** Build Previous/Next from the Icon Button pattern (§15).
**Don't:** Don't substitute infinite scroll for this — pagination is the specified pattern; infinite scroll has different accessibility and state-management implications and is out of scope here.

---

## Inputs

### 14. Button

**Purpose:** The single interactive-action primitive used everywhere in the product — every other clickable control (Icon Button, Filter Chip's remove control, Table Pagination's Prev/Next) is built from this, not a parallel implementation.

**Anatomy:** Single element, `asChild`-capable (via Radix `Slot`) for polymorphic rendering (e.g., rendering as a `Link`).

**Variants (`variant` prop):** `primary` (`bg-brand-solid`, filled) · `secondary` (bordered, neutral fill) · `ghost` (no border/fill until hover) · `destructive` (error-filled) · `link` (text-only, brand-colored, underline on hover).

**Sizes (`size` prop):** `sm` (h-8) · `md` (h-9, default) · `lg` (h-10) · `icon` (size-9, square — the basis for Icon Button, §15).

**States:** Default · Hover (`transition-colors`) · Focus-visible (2px ring) · Active/pressed (browser default — no custom pressed treatment currently defined; recommend none, to avoid adding a scale/transform effect the Motion philosophy explicitly discourages) · Disabled (`disabled:opacity-50 disabled:pointer-events-none`) · Loading (not currently implemented — recommend a future addition: `isLoading` prop swaps the label for a small inline `Loader2` spinner and sets `aria-busy`, without changing the button's size).

**Props:**
```
variant?: "primary" | "secondary" | "ghost" | "destructive" | "link"
size?: "sm" | "md" | "lg" | "icon"
asChild?: boolean
// + all standard <button> attributes
```

**Accessibility:** Real `<button>` semantics preserved (or the polymorphic target's own semantics, via `asChild`); disabled state uses the native `disabled` attribute, not just a visual style.

**Responsive behavior:** None intrinsic — sizing is fixed regardless of viewport; layout context (e.g., full-width on mobile) is the parent's responsibility.

**Usage guidance:** `primary` is reserved for the single most important action in a given context (e.g., "Approve"); a screen with multiple `primary` buttons visible at once should be reconsidered.

**Do:** Reuse this component for every clickable action in the product, including icon-only ones.
**Don't:** Don't create a parallel button-like element (e.g., a styled `<div onClick>`) anywhere — this is the one and only interactive-action primitive.

---

### 15. Icon Button — *Formalized usage pattern, not a new component*

**Recommendation:** Work Order 004 lists "Icon Button" as something to build. This spec recommends **not** creating a second component. `Button` with `size="icon"` already is the icon button (see the existing Top Navigation's theme toggle, alert bell, and mobile-menu trigger — all three are exactly this pattern today). Introducing a parallel `IconButton` component would directly violate `component-guidelines.md`'s "never duplicate components" rule and CLAUDE.md's "reuse components" instruction.

**What this section formalizes instead:** the *rules* for using `Button size="icon"` as an icon-only control, since those rules weren't written down anywhere before:

- **Anatomy:** `Button size="icon"` (36×36px) containing exactly one icon at `size-4` (16px), centered.
- **Variant choice:** `ghost` for utility actions (nav toggle, theme toggle, table pagination) — matches Top Navigation's existing usage. `secondary` only if the icon button needs to read as a more deliberate, boxed action (not currently used anywhere, but reserved).
- **Required prop:** `aria-label` is **mandatory** on every icon-only button — there is no visible text fallback. This is already enforced by convention (every current instance has one); this document makes it a hard requirement rather than an unwritten one.
- **States:** identical to Button's own state list (§14) — no separate state model.

**Do:** Always supply `aria-label`. Reuse `Button size="icon"` directly.
**Don't:** Don't build a second component. Don't omit `aria-label` because "the icon is obvious" — it isn't, to assistive technology.

---

### 16. Search Field — *Proposed*

**Purpose:** Text input for filtering/searching a Data Table or list, used inside a Table Toolbar.

**Anatomy:** Container (`h-9`, `rounded-atlas-md`, `border-border-default`) → leading `Search` icon (size-4, `text-foreground-tertiary`, non-interactive) → `<input>` → trailing clear button (`X`, size-3.5, appears only when the field has a value).

**Variants (`size` prop):** `md` (h-9, default, matches Button `md`) · `sm` (h-8, matches Button `sm`) for denser toolbars.

**States:** Default · Hover (`border-border-default` → `border-border-strong`) · Focus (`border` → brand, `focus-ring` applied to the container, not just the bare input) · Filled (clear button visible) · Disabled (reduced opacity, `pointer-events-none`).

**Props (proposed):**
```
value: string
onChange: (value: string) => void
placeholder?: string
size?: "sm" | "md"
onClear?: () => void
"aria-label"?: string  // required if no visible <label> is present
```

**Accessibility:** Real `<input type="search">`; must be paired with a visible `<label>` or an explicit `aria-label` — placeholder text alone is not an accessible label and must never be the sole means of identifying the field.

**Responsive behavior:** Full-width within a Table Toolbar on mobile; capped at a fixed max-width (~280px) at desktop so it doesn't dominate the toolbar row.

**Usage guidance:** Always paired with the icon leading the text, per the icon system's convention of never using icon-only meaning — here the icon reinforces, it doesn't replace, the field's accessible name.

**Do:** Always provide a real label (visible or `aria-label`).
**Don't:** Don't rely on placeholder-as-label. Don't animate the clear button's appearance beyond a simple opacity fade (no scale/bounce, per Motion philosophy).

---

### 17. Filter Chip — *Proposed*

**Purpose:** A toggleable or removable filter token, shown in a Table Toolbar (e.g., "Status: Healthy ✕").

**Anatomy:** Pill (`rounded-full`, matching Badge's radius choice) → label text → optional trailing remove control (`X`, size-3.5, a real button).

**Variants:**
- **Static** — read-only tag, no remove control (e.g., a non-dismissible default filter that's always applied)
- **Removable** — includes the `✕` remove control (presence of `onRemove` determines this, not a separate variant prop)

**States:** Default (neutral, `bg-surface-tertiary`) · Hover · Focus-visible (on the remove control) · **Active/applied** (`bg-brand-subtle` / `text-brand` — deliberately reusing Sidebar's active-item treatment, the one other place in the system where "this is the currently-selected thing" is communicated with the brand-tinted pattern) · Disabled.

**Props (proposed):**
```
label: string
active?: boolean
onRemove?: () => void  // presence = Removable variant, absence = Static
```

**Accessibility:** The remove control is a real `<button aria-label="Remove {label} filter">` nested inside the chip — never a bare icon glyph with a click handler on a non-button element.

**Responsive behavior:** Chips wrap to additional lines within the toolbar rather than triggering horizontal scroll.

**Usage guidance:** Filter Chips represent applied filters, not statuses — do not borrow Success/Warning/Error colors for them even if a chip happens to represent a status value (e.g., "Status: Critical") — the chip's own color stays neutral/brand; only the *label text* names the status.

**Do:** Reuse the brand-subtle "active" treatment already established by Sidebar, for consistency.
**Don't:** Don't color-code chips by the status they filter on — that would create a second, competing meaning for the status color palette.

---

## States Coverage Matrix

Per Work Order 004's requirement that components support Default/Hover/Focus/Active/Disabled/Loading/Error "where applicable":

| Component | Default | Hover | Focus | Active | Disabled | Loading | Error |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Sidebar (nav item) | ✅ | ✅ | ✅ | ✅ (current route) | Reserved | — | — |
| Top Navigation | ✅ | ✅ | ✅ | ✅ (menu open) | — | — | — |
| Breadcrumb | ✅ | ✅ | ✅ | — | — | — | — |
| Page Header | ✅ | — | — | — | — | — | — |
| Section Header | ✅ | — | — | — | — | — | — |
| Metric Card | ✅ | — | — | — | — | ✅ | ✅ |
| Status Badge | ✅ | — | — | — | — | — | — |
| Alert Card | ✅ | — | — | — | — | — | — |
| Empty State | ✅ | — | — | — | — | — | — |
| Loading Skeleton | — | — | — | — | — | ✅ (only state) | — |
| Data Table | ✅ | ✅ (row) | ✅ (sortable header) | — | — | ✅ | ✅ (proposed) |
| Table Toolbar | ✅ | — | — | — | — | — | — |
| Table Pagination | ✅ | ✅ | ✅ | — | ✅ (Prev/Next at bounds) | — | — |
| Button | ✅ | ✅ | ✅ | Native only | ✅ | Recommended addition | — |
| Icon Button | (inherits Button) | | | | | | |
| Search Field | ✅ | ✅ | ✅ | ✅ (filled) | ✅ | — | — |
| Filter Chip | ✅ | ✅ | ✅ | ✅ (applied) | ✅ | — | — |

Dashes mark states that don't meaningfully apply to that component (e.g., a static `Page Header` has no hover state because it isn't interactive).

---

## What This Document Does Not Do

- Does not modify `brand-identity-system.md`, `color-palette.md`, `icon-system.md`, or `design-tokens.md`
- Does not reopen any naming decision already settled (Degraded stays, Offline stays red/error, the primary accent remains **Primary Accent (Temporary)** — not "Atlas Ink")
- Does not build any new screen — every component here is a reusable primitive, not a page
- Does not write any application code — all props/anatomy above are specifications for the implementation pass, not implementations

**Status: awaiting review. No component will be built until approved.**
