# Atlas Brand Identity System — Recommendation

**Work Order:** BRAND-002
**Status:** Proposed — awaiting review
**Companion documents:** [`color-palette.md`](color-palette.md), [`icon-system.md`](icon-system.md)

This document is a recommendation only. No existing screens have been modified. Nothing here is applied to the Overview Dashboard until reviewed and approved, per BOUNDARIES.md.

---

## Positioning Recap

**Atlas** — Enterprise Agent Control Center. "The unified control plane for your AI workforce." Design direction: **Modern Infrastructure**. Principles: Control, Trust, Clarity, Operational first, Enterprise quality, Accessibility first.

**New objective for this system (carried forward from the Overview Dashboard refinement):** Atlas should feel like an **operating system, not an analytics dashboard**. Every recommendation below is written to reduce visual noise and increase information clarity — color, motion, and container treatments are only ever used to communicate meaning, never decoration.

---

## 1. Status System

Atlas has **two separate state vocabularies** that must not be visually conflated:

1. **Operational Status** — the health/execution state of an agent, run, or connector (this section)
2. **Decision Status** — the outcome of an approval workflow (`pending` / `approved` / `rejected`) — narrower, already implemented, unaffected by this recommendation

### Operational Status — recommended 7-state taxonomy

| State | Meaning | Color | Icon | Change from current build |
|---|---|---|---|---|
| **Healthy** | Operating normally | Success | `CheckCircle2` | No change |
| **Running** | Actively executing | Info | `Loader2` (spinning) | No change — the only animated icon in the system |
| **Pending** | Waiting on a trigger, schedule, or input — not a problem | Warning (muted) | `CircleDashed` | No change |
| **Warning** | Degraded but still functioning | Warning | `AlertTriangle` | **Rename** — the current Fleet Health table uses the label "Degraded" for this state. Recommend standardizing on "Warning" everywhere so the label vocabulary matches the Alerts severity vocabulary exactly (Critical / Warning / Information already exist there) |
| **Critical** | Severe failure requiring immediate attention | Error | `AlertOctagon` | No change — matches existing Alert severity |
| **Offline** | Stopped / not running, unexpectedly | **Neutral** (not Error) | `XCircle` | **Recommend change.** Offline currently reuses the Error/red treatment. Recommend moving it to a neutral treatment (`bg-surface-tertiary` / `text-foreground-secondary`) so red is reserved exclusively for Critical. Today, a red "Offline" badge and a red "Critical" alert compete for the same visual alarm — that dilutes Critical's meaning, which works against "Clarity" as a stated principle |
| **Disabled** | Intentionally turned off by an operator | Neutral, reduced opacity | `CircleSlash` | **New** — not yet implemented. Visually distinct from Offline: Offline implies "should be running, isn't"; Disabled implies "someone turned this off on purpose." Recommend rendering Disabled at ~60% opacity so it visibly recedes rather than competing for attention |

**Why Offline shouldn't be red:** an operator scanning a fleet table for problems should be able to trust that "red = needs attention now." If Offline (which may simply mean "paused for maintenance") shares that treatment with Critical (which means "something is actively broken"), the operator has to read every red badge's label to know if it's actually urgent. Removing that ambiguity is a direct, concrete way to serve "reduce visual noise while increasing information clarity."

**Reconciling with Decision Status:** the existing `pending` / `approved` / `rejected` approval states already map cleanly onto this system's color logic (Pending→Warning-muted, Approved→Success, Rejected→Error) and require no change.

---

## 2. Component Personality

Codifying what the Overview Dashboard already established as house style, so future screens don't have to rediscover it:

| Element | Rule |
|---|---|
| **Cards** | `rounded-atlas-lg`, `border-border-default` (hairline, not outline), `shadow-atlas-sm` (barely-there). Cards separate from each other primarily through spacing (`gap-8` between major sections), not border weight |
| **Borders** | Three tiers only — `border-subtle` (table row dividers), `border-default` (card edges), `border-strong` (reserved, not yet used). All are low-alpha overlays, not solid neutral swatches, so they scale with light/dark automatically |
| **Radius** | Three tiers — `radius-atlas-sm` (4px, badges/tags), `radius-atlas-md` (8px, buttons/inputs/icon chips/cards' inner elements), `radius-atlas-lg` (12px, cards themselves). No other radius values should appear |
| **Shadows** | Two tiers only, both minimal — `shadow-atlas-sm` (default card resting state) and `shadow-atlas-md` (popovers/dropdowns/tooltips — anything that floats above the page). Never used to fake depth or elevation beyond that |
| **Metric cards** | The number is the dominant element (`text-4xl`/`5xl`, Inter not mono). Label is secondary (mono, uppercase, small). Icon is tertiary (small chip, neutral unless reporting status). This hierarchy — number > label > icon — should hold on every metric card in the product |
| **Tables** | Mono headers (uppercase, wide tracking) signal "this is operational data." Row height `py-3.5`. Dividers are the lightest border tier (`border-subtle`) — density and whitespace communicate structure, not heavy rules |
| **Section headers** | `CardTitle` (`text-sm`, semibold, tight tracking) + `CardDescription` (`text-xs`, muted) — every card-based section follows this exact two-line header pattern, no exceptions, so scanning the dashboard top-to-bottom feels uniform |

---

## 3. Data Visualization (forward-looking — none exist yet)

No charts currently exist in the Overview Dashboard (it uses metric cards, a table, and lists). This section is guidance for future screens (e.g., an Agents detail view or Runs analytics) so charts are designed consistently with everything above rather than improvised later.

**General rules:**
- No gradients, no 3D effects, no drop shadows on chart elements
- Chart color palette is exactly: neutral grays for baseline/inactive series, the four status colors for anything status-related, brand color only if a chart needs a single non-status accent series
- Never introduce a fifth categorical color — if a chart needs more than 4–5 distinct series, it's the wrong chart type for this product (prefer a table)

**Trend lines** (e.g., a sparkline showing agent throughput over time):
- Single-color line, 1.5–2px stroke, no fill/area gradient beneath it
- Use Success/Error color only if the trend line itself represents a pass/fail metric; otherwise neutral (`--foreground-secondary`)
- No data-point markers on the line itself except on hover

**Donut / ring charts** (e.g., fleet health breakdown):
- Segments colored using the Operational Status palette above (Healthy/Warning/Critical/Offline/Disabled) — never arbitrary chart-library defaults
- Center label uses the same numeral treatment as metric cards (large, Inter, semibold) — a donut chart's center number should look like it belongs to the same family as the KPI cards above it
- Track (background ring) uses `--surface-tertiary`, not a colored "remainder" segment

**Empty states for charts:**
- Reuse the existing `EmptyState` component pattern exactly (icon in a neutral circle, title, short description) rather than inventing a chart-specific empty state
- Never render a chart axis/grid with no data — show the empty state instead

---

## 4. Motion

Per CLAUDE.md, Framer Motion is used **minimally**. This section defines the boundary of "minimal."

| Interaction | Treatment |
|---|---|
| **Hover** | Color/background transition only (`transition-colors`, ~150ms). No scale, no shadow-lift, no movement |
| **Focus** | Instant 2px outline (`--focus-ring`), no transition delay — focus must never feel "lazy" for keyboard users |
| **Loading** | `Skeleton` pulse (existing Tailwind `animate-pulse`) for content still arriving; `Loader2` spin exclusively for actively-running status. No skeleton shimmer effects, no progress bars with gradient fills |
| **Status changes** | State changes (e.g., an approval resolving) should update immediately, no transition animation on the value itself. If a future screen wants to soften this, a single opacity cross-fade (~150–200ms) is the ceiling — never a slide, bounce, or scale transform |
| **Reduced motion** | Already enforced globally (`prefers-reduced-motion` collapses all durations to ~0) — any future motion must respect this same global rule, not add its own escape hatch |

**Rule of thumb:** if a motion effect would look at home in a consumer app but not in an airline cockpit display, it doesn't belong in Atlas.

---

## 5. Cross-References

- Primary brand color, neutral palette, and semantic status colors, with accessibility validation → [`color-palette.md`](color-palette.md)
- Icon stroke width, size scale, container/chip rules, and the concept-to-icon mapping table → [`icon-system.md`](icon-system.md)

---

## 6. What Changes If This Is Approved

For transparency, since no code is being written in this pass:

- **Tokens:** `tokens.css` brand values need no change (already match §1 of `color-palette.md`) — only the "temporary" framing in its header comment would be removed
- **Status labels:** `StatusBadge`'s `degraded` state would be relabeled "Warning" in its display string; `offline`'s color class would move from error to neutral; a new `disabled` state would be added
- **No layout, architecture, or component structure changes** — this system codifies and extends what's already built, it does not redesign it

---

## 7. Open Questions for Review

1. Confirm "Atlas Ink" (`#3d6690` family) as the primary brand color, or hold further pending a separate logo process
2. Confirm the Offline → neutral recolor (currently shares Error/red with Critical)
3. Confirm addition of the new `Disabled` operational state ahead of any screen that needs it
4. Confirm the "Warning" relabel of the Fleet Health table's current "Degraded" text

**Status: awaiting review. No changes will be applied to the Overview Dashboard or any other screen until approved.**
