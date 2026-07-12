# Atlas Icon System — Recommendation

**Work Order:** BRAND-002
**Status:** Proposed — awaiting review
**Library:** Lucide (per KNOWLEDGE.md / CLAUDE.md — no other icon set is in scope)

This document is a recommendation only. No components have been changed.

---

## 1. Stroke Width

**Standard: `1.75`** (Lucide's default is `2`).

Applied once, globally, rather than per-icon-instance:

```css
svg { stroke-width: 1.75; }
```

This is already live in `globals.css` from the refinement pass — this document formalizes it as system policy rather than a one-off tweak.

**Rationale:** Lucide's default `2` reads slightly heavy at the small sizes used throughout an operational dashboard (14–20px). `1.75` is lighter without approaching the fragility of `1.5`, and — critically — applying it as a single global rule guarantees every icon in the product carries identical visual weight, regardless of which engineer drops in a new Lucide icon later. This is what makes the icon set read as "one system" rather than "whatever the default was."

**Exception:** none. If a future icon needs emphasis (e.g., a destructive-action icon), express that through color or size — not a heavier stroke. Mixing stroke weights is one of the fastest ways to make an icon set look unintentional.

---

## 2. Size Scale

Five sizes, each tied to a specific usage context. No other sizes should appear in the product.

| Token | Pixels | Context |
|---|---|---|
| `size-3.5` | 14px | Inline with small text — trend indicators, badge icons, status-badge icons |
| `size-4` | 16px | Default — nav items, table cells, button icons, card icons inside a chip |
| `size-4.5`* | 18px | *Avoid — not on Tailwind's default scale; do not introduce as a one-off arbitrary value* |
| `size-5` | 20px | Empty-state / error-state icon (inside its circular container), top-bar icon buttons |
| `size-8`–`size-9` | 32–36px | Icon **containers** (chips), not the icon itself — see §3 |

**Rule:** an icon's own size is almost always `size-4` (16px). The only two exceptions are `size-3.5` for inline/badge contexts and `size-5` for the single icon inside an empty/error-state circle. Resist the temptation to size icons to "fill" their container — the whitespace inside a chip is deliberate (see Metric Card guidance in `brand-identity-system.md`).

---

## 3. Containers ("chips")

Icons that represent a concept (not an inline action) sit inside a square, rounded container — the "chip" pattern already used for metric-card icons, alert-card severity icons, and the sidebar logo mark.

| Chip size | Icon size | Radius | Usage |
|---|---|---|---|
| `size-8` (32px) | `size-4` (16px) | `rounded-atlas-md` | Metric card icon, alert-card severity icon, sidebar logo mark |
| `size-9` (36px) | `size-4`/`size-5` | `rounded-atlas-md` | Reserved for a single, more prominent placement per screen (not currently used — avoid introducing without reason) |
| `size-10` (40px) | `size-5` | `rounded-full` | Empty-state / error-state icon |

**Fill rule:** a chip's background communicates the icon's *role*, not decoration:

- **Neutral** (`bg-surface-tertiary` / `text-foreground-secondary`) — default for any icon that isn't reporting a status (e.g., "Total Agents," "Running Agents" counts — these are just counts, not health signals)
- **Status-tinted** (`bg-success-bg` / `bg-warning-bg` / `bg-error-bg` / `bg-info-bg`) — reserved for icons that *are* reporting a status (Healthy-agents count, Pending-approvals count, alert severity, empty/error states)
- **Brand-solid** (`bg-brand-solid`) — reserved for exactly one element per screen: the product's own mark (sidebar logo). Never used for a generic content icon.

This is the same principle color-palette.md establishes for color generally: a visual treatment must mean something, or it's noise. A dashboard where every icon chip is a different pastel color is what this system is explicitly designed to avoid — see "operating system, not analytics dashboard" in `brand-identity-system.md`.

---

## 4. Usage Rules

1. **One icon per concept, everywhere.** Build (and maintain) a fixed mapping from domain concept → Lucide icon, and reuse it across every screen. Table below is the current mapping; extend it, don't fork it, when new screens are built.
2. **`aria-hidden="true"` on every decorative/status icon.** Icons are always paired with visible text (a label, a badge string) — they are never the sole conveyor of information. This is already the pattern in `StatusBadge`, `AlertCard`, and nav items; keep it that way on new screens.
3. **Motion is reserved for exactly one state: active execution.** Only `Loader2` (or equivalent) spins, and only for `running`/`loading` states. No other icon should animate — see Motion section of `brand-identity-system.md`.
4. **Never recolor an icon independently of its chip.** Icon color is always inherited from the chip's semantic class (`text-success`, `text-foreground-secondary`, etc.), never set as a one-off override.

### Current concept → icon mapping

| Concept | Icon | Notes |
|---|---|---|
| Overview / dashboard | `LayoutDashboard` | Sidebar nav |
| Agents | `Bot` | Sidebar nav |
| Runs | `Workflow` | Sidebar nav |
| Approvals | `CheckSquare` | Sidebar nav + approval actions (`Check` for approve) |
| Alerts | `Bell` | Sidebar nav + top-bar notification |
| Connectors | `Plug` | Sidebar nav |
| Policies | `ShieldCheck` | Sidebar nav |
| Artifacts | `Package` | Sidebar nav |
| Audit | `ScrollText` | Sidebar nav |
| Settings | `Settings` | Sidebar footer |
| Total Agents | `Bot` | Metric card (neutral chip) |
| Running Agents | `PlayCircle` | Metric card (neutral chip) |
| Healthy Agents | `HeartPulse` | Metric card (success chip) |
| Pending Approvals | `CheckSquare` | Metric card (warning chip) |
| Healthy (status) | `CheckCircle2` | Success |
| Running (status) | `Loader2` (spinning) | Info — the only animated icon |
| Queued (status) | `CircleDashed` | Neutral |
| Pending (status) | `CircleDashed` | Warning |
| Degraded/Warning (status) | `AlertTriangle` | Warning |
| Offline (status) | `XCircle` | *Recommend moving to neutral — see brand-identity-system.md §Status System* |
| Critical alert | `AlertOctagon` | Error |
| Warning alert | `AlertTriangle` | Warning |
| Informational alert | `Info` | Info |
| Refresh action | `RefreshCw` | Button |
| Approve action | `Check` | Button |
| Reject action | `X` | Button |
| Theme toggle | `Sun` / `Moon` | Top bar |
| Mobile nav open/close | `Menu` / `X` | Top bar / drawer |
| Empty state (generic) | `Inbox` | Default fallback |
| Empty state (fleet) | `ServerCog` | Fleet Health |
| Empty state (runs) | `Activity` | Active Runs |
| Empty state (approvals) | `CheckSquare` | Pending Approvals |
| Empty state (alerts) | `BellOff` | Alerts |
| Empty state (schedule) | `CalendarX2` | Upcoming Schedule |
| Error state (generic) | `AlertCircle` | |
| Scheduled item | `CalendarClock` | Upcoming Schedule |

**New concepts not yet built** (Agents, Runs, Connectors, Policies, Artifacts, Audit screens) should extend this table before implementation begins on those screens, so icon choices are made once, deliberately, rather than improvised per-screen.

---

## 5. Do / Don't

**Do:**
- Apply the global `stroke-width: 1.75` — never override per-instance
- Keep icon size at `size-4` unless it's an inline/badge (`size-3.5`) or a state-circle (`size-5`)
- Reuse the concept → icon table; extend it centrally when new concepts appear

**Don't:**
- Mix icon libraries — Lucide only
- Introduce arbitrary sizes (e.g., `size-[17px]`)
- Use a filled/solid icon style alongside Lucide's stroked style — visual inconsistency
- Animate any icon other than the running/loading spinner
