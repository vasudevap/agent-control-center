# Atlas Design Tokens v1.0 — Recommendation

**Work Order:** 003 — Design Tokens v1.0
**Status:** Proposed — awaiting review
**Depends on:** [`brand-identity-system.md`](brand-identity-system.md), [`color-palette.md`](color-palette.md), [`icon-system.md`](icon-system.md) — all three are kept as-is; nothing in those documents is changed or superseded except where explicitly noted below.

This document is a recommendation only. No tokens, components, or screens have been modified. Nothing here is applied until reviewed and approved.

---

## Carried Forward Without Change

Per the work order's instruction to keep these as previously defined:

- **Component personality** — cards, borders, radius, shadows, metric-card hierarchy, table density, section-header pattern (`brand-identity-system.md` §2)
- **Icon system** — stroke width, size scale, chip containers, concept→icon mapping (`icon-system.md`)
- **Neutral palette** — 12-step slate scale (`color-palette.md` §2)
- **Semantic colors** — Success / Warning / Error / Info, both themes (`color-palette.md` §3)
- **Motion philosophy** — hover/focus/loading/status-change boundaries (`brand-identity-system.md` §4)
- **Border system** — three-tier hairline-overlay approach (`color-palette.md` §2, `brand-identity-system.md` §2)

## Explicit Corrections to Prior Recommendations

The following proposals from `brand-identity-system.md` §7 (Open Questions) are **not adopted** as of this work order:

- **"Degraded" is not renamed.** The Fleet Health table's existing "Degraded" label stands as-is.
- **"Offline" is not recolored neutral.** It keeps its current Error/red treatment.
- **The primary brand color is not permanently named.** Prior documents used "Atlas Ink" as a working name for the `#3d6690` family; this was provisional and is not adopted. This document — and everything downstream of it — refers to that color only as **Primary Accent (Temporary)** until a logo-derived identity is approved. The hex values and token architecture (`--brand` / `--brand-solid` split) are unchanged; only the name "Atlas Ink" is withdrawn.

Nothing above required editing `brand-identity-system.md` or `color-palette.md` directly — both are left intact per instruction; this section is the authoritative override.

---

## 1. Typography Scale

Two typefaces only, per KNOWLEDGE.md: **Inter** (primary) and **JetBrains Mono** (secondary — labels, metadata, timestamps, technical annotations, code). A tier is either one or the other, never mixed within itself.

| Tier | Typeface | Size | Weight | Line Height | Letter Spacing | Usage | Status |
|---|---|---|---|---|---|---|---|
| **Display** | Inter | 60px / 3.75rem | Semibold (600) | 1.1 | −0.02em (tight) | Reserved for hero-scale numerals — e.g. a single headline metric on a future summary/landing surface. Larger than any Metric Card value; not used on the Overview Dashboard | Reserved (not yet used) |
| **H1** | Inter | 24px → 30px (responsive) | Semibold (600) | 1.2 | −0.02em (tight) | Page title (`PageHeader`) | Implemented |
| **H2** | Inter | 20px / 1.25rem | Semibold (600) | 1.25 | −0.01em | Sub-page heading — a heading that groups multiple Section Titles on a screen with more than one major zone (no current screen needs this; Overview is single-zone) | Reserved (not yet used) |
| **H3** | Inter | 18px / 1.125rem | Semibold (600) | 1.3 | −0.01em | Nested heading within an H2 zone (e.g. a subsection of an Agents detail screen) | Reserved (not yet used) |
| **Section Title** | Inter | 16px / 1rem | Semibold (600) | 1.4 | normal | Groups a cluster of cards under one label on a multi-zone screen (distinct from, and one size larger than, Card Title) | Reserved (not yet used) |
| **Card Title** | Inter | 14px / 0.875rem | Semibold (600) | 1.3 | −0.01em (tight) | Card header (`CardTitle`) — "Fleet Health," "Active Runs," etc. | Implemented |
| **Table Header** | JetBrains Mono | 11px | Medium (500) | 1.2 | 0.06em (wide) | Table column headers (`TableHead`) — uppercase | Implemented |
| **Body Large** | Inter | 16px / 1rem | Regular (400) | 1.6 (relaxed) | normal | Page-level descriptive copy where more presence than default Body is warranted (not currently needed — `PageHeader` description uses Body) | Reserved (not yet used) |
| **Body** | Inter | 14px / 0.875rem | Regular (400) | 1.6 (relaxed) | normal | Page-level descriptive text (`PageHeader` description) | Implemented |
| **Metadata** | JetBrains Mono | 12px / 0.75rem | Regular (400) | 1.4 | normal | Timestamps, durations, run IDs, "requested 18 min ago" — anything machine-generated/operational | Implemented (see note below) |
| **Caption** | Inter | 12px / 0.75rem | Regular (400) | 1.5 | normal | Muted supporting prose — `CardDescription`, empty/error-state descriptions. Distinct from Metadata: Caption is human-authored sentence copy, Metadata is machine-generated data | Implemented |
| **Status Badge** | Inter | 12px / 0.75rem | Medium (500) | 1 (none — single line) | normal | The label text inside a status pill (`StatusBadge`, `Badge`) | Implemented |
| **Code** | JetBrains Mono | 14px / 0.875rem | Regular (400) | 1.5 | normal | Reserved for literal technical values in a dedicated inline/code treatment (e.g. a future policy JSON preview or connector config snippet) — distinct from Metadata by size and by having its own background treatment (a subtly tinted, monospace-only inline chip), not yet needed on any built screen | Reserved (not yet used) |

**Implementation note (informational, not a change request):** Metadata currently appears at two sizes in the shipped build — 12px in some places (e.g. `AlertCard` timestamp) and 11px in others (e.g. `ActiveRunsSection` duration, `PendingApprovalsSection` "Requested X ago"). This scale recommends standardizing all Metadata usage at **12px**, with **11px reserved exclusively for the Table Header tier's uppercase micro-label context** (where the wide tracking and all-caps treatment need the smaller size to avoid feeling oversized). This is a note for a future consolidation pass — no UI is being changed by this document.

---

## 2. Spacing Scale

Closed set — **4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96** (pixels). Nothing outside this list should be introduced. Base unit is 4px; 8px is the primary rhythm (per KNOWLEDGE.md), with 4px available as a fine half-step and the upper steps (64–96) reserved for page-level, not component-level, spacing.

This scale maps 1:1 onto Tailwind's default spacing scale, which is what the codebase already uses — no new spacing utility is required to adopt it:

| Value | Tailwind step | Usage guidance |
|---|---|---|
| **4px** | `1` | Finest increment — icon-to-text gap in the densest inline contexts (badge internals), never used for padding |
| **8px** | `2` | Primary micro-rhythm — gap between an icon and its label, gap between tightly related inline elements, sidebar item internal padding |
| **12px** | `3` | Secondary micro-rhythm — used where 8px reads too tight and 16px too loose (e.g. gap between a label and the value directly beneath it in a Metric Card) |
| **16px** | `4` | Standard internal padding for compact containers; gap between rows within a list-style section (Active Runs, Upcoming Schedule) |
| **24px** | `6` | Default card padding at narrow viewports; gap between grouped elements within a card's content area |
| **32px** | `8` | Card padding at desktop width (Metric Cards); the current inter-card gap within a column (`gap-8`) |
| **40px** | `10` | Reserved — larger internal breathing room for a card that needs more presence than standard (not currently used) |
| **48px** | `12` | Reserved — gap between major page sections on a denser, multi-zone future screen |
| **64px** | `16` | Page-level vertical rhythm — top-level margin/padding at wide viewports on a future multi-zone screen |
| **80px** | `20` | Reserved — generous top-level spacing, landing/marketing-adjacent surfaces only, not dashboard density |
| **96px** | `24` | Reserved — maximum spacing tier, hero sections only |

---

## 3. Elevation Scale

Four tiers. Shadows remain deliberately minimal per `ui-standards.md` — elevation communicates stacking order (what floats above what), never decorative depth.

| Tier | Shadow value (light) | Shadow value (dark) | Usage |
|---|---|---|---|
| **None** | `none` | `none` | Elements resting flush on their surface — table rows, sidebar nav items, inline badges, tooltip triggers |
| **Low** | `0 1px 2px 0 rgb(15 23 42 / 0.04)` | `0 1px 2px 0 rgb(0 0 0 / 0.24)` | Default card resting state — the only elevation most of the UI ever needs. Matches existing `--shadow-sm` | Implemented (as `--shadow-sm` / `shadow-atlas-sm`) |
| **Medium** | `0 1px 3px 0 rgb(15 23 42 / 0.08), 0 1px 2px -1px rgb(15 23 42 / 0.06)` | `0 1px 3px 0 rgb(0 0 0 / 0.36), 0 1px 2px -1px rgb(0 0 0 / 0.3)` | Anything that floats above adjacent page content — dropdown menus, tooltips, popovers. Matches existing `--shadow-md` | Implemented (as `--shadow-md` / `shadow-atlas-md`) |
| **Overlay** | `0 8px 24px -4px rgb(15 23 42 / 0.18), 0 4px 8px -4px rgb(15 23 42 / 0.12)` | `0 8px 24px -4px rgb(0 0 0 / 0.48), 0 4px 8px -4px rgb(0 0 0 / 0.36)` | Full modal dialogs and the mobile navigation drawer — content that needs to visually separate from the *entire* page, not just an adjacent sibling. Not yet a distinct token; the current mobile drawer relies on its scrim + border rather than a dedicated overlay shadow | Reserved (not yet implemented) |

**Naming reconciliation:** current tokens (`--shadow-sm`, `--shadow-md`) map onto this vocabulary as Low and Medium respectively. Adopting this scale means introducing `--shadow-none` (an explicit no-op, for clarity in component code) and `--shadow-overlay`, without changing the values already in use.

---

## 4. Radius Scale

Three tiers, unchanged in value from the existing implementation — this section formalizes usage mapping only.

| Tier | Value | Token | Maps to |
|---|---|---|---|
| **Small** | 4px | `--radius-atlas-sm` | Tooltips (`TooltipContent`); reserved for small rectangular controls not yet built (checkboxes, switches). **Not** status pills — those are fully rounded by design (see note) |
| **Medium** | 8px | `--radius-atlas-md` | Buttons, inputs, icon chips, card-internal elements, dropdown menus, nav items — the most common radius in the product |
| **Large** | 12px | `--radius-atlas-lg` | Cards themselves; reserved for future modal/dialog surfaces |

**Note on pill-shaped elements:** `Badge` and `StatusBadge` currently use `rounded-full`, not the Small tier — this is intentional (a pill communicates "status/tag," a slightly-rounded rectangle communicates "container"), not an inconsistency. This scale does not recommend changing that.

---

## 5. Token Naming Conventions

A single naming grammar across all five token categories: **`--{category}-{role}`**, where `role` is semantic (what it's *for*), never referencing a raw value (never `--blue-600`, always `--brand`).

| Category | Pattern | Examples | Notes |
|---|---|---|---|
| **Color** | `--color-{role}` at the Tailwind-theme layer, `--{role}` at the token layer | `--brand`, `--brand-solid`, `--success`, `--border-default`, `--surface-secondary` | The primary accent's token names (`--brand`, `--brand-solid`) are unchanged and already role-based, not name-based — only the *documentation label* changes to **Primary Accent (Temporary)**; no variable rename is implied |
| **Typography** | `--type-{tier}-{property}` | `--type-h1-size`, `--type-h1-weight`, `--type-h1-leading`, `--type-h1-tracking`, `--type-metadata-size` | One set of four properties (size/weight/leading/tracking) per tier in §1; `font-family` is set once globally (`--font-sans`, `--font-mono`), not per tier |
| **Spacing** | `--space-{px-value}` | `--space-4`, `--space-8`, `--space-24`, `--space-64` | Name is the literal pixel value from the closed scale in §2 — never a semantic alias like `--space-card-padding`, so the scale stays a shared, finite vocabulary rather than growing per-component names |
| **Radius** | `--radius-atlas-{tier}` | `--radius-atlas-sm`, `--radius-atlas-md`, `--radius-atlas-lg` | Already implemented exactly this way |
| **Elevation** | `--shadow-{tier}` | `--shadow-none`, `--shadow-low`, `--shadow-medium`, `--shadow-overlay` | Recommend this as the semantic name going forward; existing `--shadow-sm`/`--shadow-md` are the same values under the old name (see §3) |
| **Motion** | `--motion-{property}-{tier}` | `--motion-duration-fast` (~150ms, hover/color transitions), `--motion-duration-base` (~150–200ms, the opacity cross-fade ceiling from `brand-identity-system.md` §4), `--motion-ease-standard` (a single shared easing curve, not yet named) | No motion tokens exist as CSS variables yet — durations are currently inline Tailwind (`transition-colors` default). This formalizes them as named tokens without changing any current transition's actual timing |

---

## 6. What This Document Does Not Do

- Does not reopen the Offline/Degraded/Atlas-Ink questions from `brand-identity-system.md` §7 — those are explicitly closed per this work order (see "Explicit Corrections" above)
- Does not modify `brand-identity-system.md`, `color-palette.md`, or `icon-system.md`
- Does not change any token value currently in `tokens.css` — every "Implemented" row above matches shipped values; every "Reserved" row is net-new and inert until adopted
- Does not touch any component or screen

**Status: awaiting review. No implementation will begin until approved.**
