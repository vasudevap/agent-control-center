# Refinement Plan 002: Overview Dashboard Polish

**Date:** 2026-07-10
**Baseline:** Approved (Phase 1 Overview Dashboard implementation)
**Status:** Awaiting approval — no code changes made yet
**Objective:** Increase perceived product quality from ~9.3/10 to 9.7+/10 through refinement only. No redesign, no new widgets, no new functionality.

---

## Scope Guardrails

**Keep unchanged:**
- Overall layout
- Information hierarchy
- Card placement
- Dashboard structure
- Sidebar structure
- Component architecture

**Do not:**
- Redesign layouts
- Add new widgets or charts
- Add new functionality
- Introduce visual effects, gradients, glassmorphism, or decorative animation

All changes below are token- and class-level refinements to existing components.

---

## Visual References

- **Linear** — restrained accent color used sparingly, tight typographic hierarchy, near-invisible borders
- **Stripe Dashboard** — table density/typography, generous card whitespace, numbers that dominate over chrome
- **Vercel Dashboard / Geist** — monochrome-first surfaces with a single disciplined accent, mono used deliberately for technical metadata only
- **GitHub Primer** — desaturated, deep accent blue (`#0969DA`), far less saturated than Tailwind's default `blue-600`

---

## 1. Typography (Highest Priority)

| Element | Current | Proposed |
|---|---|---|
| Page H1 | `text-xl sm:text-2xl` semibold | `text-2xl sm:text-3xl` semibold, tighter `tracking-tight` |
| Title→subtitle gap | `gap-1` | `gap-2`, subtitle drops to `text-sm` muted with slightly more line-height |
| Metric value | `text-2xl`, font-mono | `text-4xl sm:text-5xl`, **switch to Inter (sans)**, tabular-nums, tighter tracking |
| Metric label | `text-xs uppercase` sans | `text-xs uppercase` **JetBrains Mono**, wider tracking |
| Table header row | `text-xs uppercase` sans | **JetBrains Mono** |
| Table timestamps/meta | already mono | keep, tighten size/color consistency |
| Sidebar nav labels | `text-sm font-medium` | keep size, refine line-height/vertical centering, tighten tracking slightly |
| Sidebar badges/counts | mono | keep — already correct |

**Why:** Mono is currently used almost decoratively (on the big metric number, where it competes with the number's size) and not used where it would signal "this is machine-generated, operational data" — labels, timestamps, table headers. Swapping the big metric number to Inter makes it read bigger and bolder (mono digits are wider and look smaller at the same font-size). Pushing mono down to labels/metadata/timestamps is the split Vercel and Linear use: humanist sans for anything meant to be read, mono for anything meant to be scanned as data.

---

## 2. Atlas Accent Color

**Current:** Tailwind default `blue-600` (`#2563eb`) — instantly recognizable as unstyled default.

**Proposed:** A desaturated, deep ink-blue — same hue family (no pivot to purple/teal), pulled down in saturation and lightness so it reads as considered rather than default.

- Light mode brand: `#2C4A6E` ("Atlas Ink") — deep steel blue, ~215° hue, ~45% saturation, ~30% lightness
- Dark mode brand: `#6C93BE` — same hue family, lifted lightness for contrast on dark surfaces, still desaturated
- Subtle/tint backgrounds derived from the same hue at low saturation/opacity — no separate accent color introduced

**Why:** Keeps a blue (matches "Control/Trust" positioning, no risky hue pivot) but removes the "generic SaaS" signal from high-saturation Tailwind defaults. Same move GitHub made with `#0969DA` vs a raw Bootstrap blue — same family, deliberately less saturated, reads as engineered rather than picked from a palette generator.

---

## 3. Sidebar Polish

- Tighten and regularize spacing rhythm: logo row, nav items, and settings footer all snap to the same 8px vertical rhythm (currently slightly inconsistent between `p-3` container and `py-2` items)
- Active state: keep the subtle tinted background, add a thin **left accent rule** (2px, brand color) instead of relying on background tint alone — reads as more intentional than a flat highlight (Linear, Notion pattern)
- Icon consistency: standardize all Lucide icons to the same `strokeWidth` (currently default, inconsistent visual weight) — pin to `1.75`
- Section hierarchy: add slightly more breathing room between the top nav cluster and the Connectors/Policies/Artifacts/Audit cluster (spacing only — no dividers, no relabeling, no reordering)

---

## 4. KPI Cards

- Number becomes the dominant element: `text-4xl`/`5xl`, tighter tracking, sits closer to the top label with more separation from the icon
- Icon treatment de-emphasized: shrink chip from `size-9` to `size-8`, reduce icon opacity/weight so it reads as secondary, not competing with the number
- Increase internal card padding slightly for more whitespace around the number
- Trend indicator shrinks slightly; delta value moves to mono

---

## 5. Tables

- Row height: `py-3` → `py-3.5`
- Header row switches to JetBrains Mono (see Typography)
- Divider weight reduced (see Borders) — row separators become nearly invisible, relying on whitespace + hover state (Stripe pattern)
- Cell typography: agent name stays Inter/medium; secondary columns (status text, timestamps) tighten to a consistent muted color weight

---

## 6. Borders

- Card borders: reduce contrast substantially — `border-default` token pulled closer to the surface color itself (light mode: `#e2e8f0` → ~`#edf1f5`; dark mode: moves closer to the dark surface tone) so it reads as a hairline, not an outline
- Increase gap between major cards (`gap-6` → `gap-8` in the two-column section grid) so spacing — not strokes — does the separating
- Table row dividers get the same contrast reduction, even lighter than card borders since they repeat many times per section

---

## 7. Overall Polish

- Audit every spacing value against the 8px grid; correct any off-grid values introduced during Phase 1
- Standardize icon stroke-width globally (not just sidebar) so Lucide icons read as one consistent set
- Align card header padding/vertical rhythm across all six sections so they line up edge-to-edge
- Unify focus-ring and radius treatment across buttons/cards/badges

---

## Scope Confirmation

All changes above are token- and class-level refinements to existing components — no new components, no layout changes, no structural sidebar/card changes, nothing added.

**Status: Awaiting approval to implement.**
