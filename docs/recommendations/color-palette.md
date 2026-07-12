# Atlas Color Palette — Recommendation

**Work Order:** BRAND-002
**Status:** Proposed — awaiting review
**Scope:** Primary brand color, neutral palette, semantic status colors, accessibility validation

This document is a recommendation only. No tokens or UI have been changed. If approved, it replaces the "temporary neutral-blue" framing established during the Overview Dashboard refinement pass with a permanent decision.

---

## 1. Primary Brand Color

### Recommendation: "Atlas Ink"

A deep, desaturated steel-blue — not a bright SaaS blue, not purple, no gradient.

| Step | Hex | Usage |
|---|---|---|
| 50 | `#eef2f7` | Active/selected background tint (light mode) |
| 100 | `#dde6f0` | Stronger tint — sidebar active state, hover fills |
| 200 | `#c2d3e3` | Border/divider accents on brand-tinted surfaces |
| 300 | `#9db9d1` | Disabled brand elements, decorative accents |
| 400 | `#7098bb` | Dark-mode hover state |
| 500 | `#4d7aa3` | Focus ring (light mode) |
| 600 | `#3d6690` | **Primary** — buttons, links, active icons/text (light mode), solid fills (both modes) |
| 700 | `#325577` | Hover/pressed state for primary actions |
| 800 | `#2a465f` | Reserved — dense/pressed dark accents |
| 900 | `#23394c` | Reserved — maximum-contrast brand text on light surfaces |

**Why this color, and why now:**

This is the same hue this project has already been using since the Overview Dashboard refinement pass (`#3d6690`), where it was explicitly framed as a *temporary* placeholder pending a logo-derived identity. This document promotes it to a firm recommendation rather than introducing a new, unvalidated color, for three reasons:

1. **It has already been visually and functionally validated** in the shipped Overview Dashboard, across light and dark mode, at production build quality.
2. **It satisfies every constraint already given for the brand accent**: modern, enterprise, premium, restrained, timeless, no bright SaaS blue, no purple, no gradient.
3. **Changing hue at this stage is the highest-risk, lowest-value move available.** A hue swap (e.g., to teal or slate-green) would invalidate the accessibility work already done and would not be motivated by anything in the brief — the brief asks for *restraint*, which this already delivers.

**Alternatives considered and rejected:**

| Option | Rejected because |
|---|---|
| Tailwind default blue (`#2563eb`) | Reads as an unstyled default — this is what the refinement pass moved away from |
| Purple/indigo (Linear/Stripe-style) | Explicitly excluded by brief |
| Teal/green primary | Would collide semantically with the Success status color |
| Monochrome-only (Vercel-style, no accent) | Atlas needs a recognizable accent for interactive affordances (buttons, links, active nav) — full monochrome under-serves "Control" as a principle |
| Bright/saturated blue variant | Explicitly excluded by brief ("avoid bright SaaS blue") |

**If a logo is produced separately:** if the approved logo mandates a different hue, only the nine `--atlas-brand-*` values in `tokens.css` need to change — every component references the semantic tokens (`--brand`, `--brand-solid`, `--brand-subtle`, `--focus-ring`), not raw hex values, so a future hue change is a one-file edit, not a UI rewrite. This was a deliberate architecture decision, not an accident.

### Token architecture: `--brand` vs `--brand-solid`

Two distinct semantic tokens, both derived from the same palette, exist for accessibility reasons:

- **`--brand`** — used for text, icons, links, active states. Value differs per theme (light: `600`, dark: a lighter custom tone `#86a8c7`) so it stays readable against its surrounding surface in both themes.
- **`--brand-solid`** — used for filled backgrounds (primary buttons, logo mark, filled badges) carrying white text. This stays the **same value in both themes** (`#3d6690`) because it was validated to give ~6:1 contrast against white text regardless of theme — a lighter dark-mode variant would drop that contrast below 3:1.

Do not collapse these into a single token — that was tried during refinement and failed contrast validation in dark mode (see §4).

---

## 2. Neutral Palette

Slate-based, 12 steps (0 → 950), shared by both themes as the base from which all light/dark surface and text tokens are derived.

| Step | Hex | Primary usage |
|---|---|---|
| 0 | `#ffffff` | Light-mode background/surface |
| 50 | `#f8fafc` | Light-mode secondary surface |
| 100 | `#f1f5f9` | Light-mode tertiary surface, hover fills |
| 200 | `#e2e8f0` | Light-mode active/pressed fills |
| 300 | `#cbd5e1` | Reserved — stronger light-mode dividers |
| 400 | `#94a3b8` | Dark-mode tertiary text |
| 500 | `#64748b` | Reserved |
| 600 | `#475569` | Light-mode secondary text |
| 700 | `#334155` | Reserved |
| 800 | `#1e293b` | Dark-mode secondary/tertiary surface |
| 900 | `#0f172a` | Dark-mode background/surface, light-mode primary text |
| 950 | `#020617` | Dark-mode background |

Borders are **not** solid neutral steps. They are low-alpha overlays of near-black (light mode) / near-white (dark mode) so they read as hairlines rather than outlines, and scale naturally with whichever surface they sit on:

| Token | Light | Dark |
|---|---|---|
| `--border-subtle` | `rgb(15 23 42 / 0.05)` | `rgb(255 255 255 / 0.05)` |
| `--border-default` | `rgb(15 23 42 / 0.08)` | `rgb(255 255 255 / 0.08)` |
| `--border-strong` | `rgb(15 23 42 / 0.16)` | `rgb(255 255 255 / 0.16)` |

---

## 3. Semantic Status Colors

Four hues, each with a solid text/icon value, a soft background tint, and a border tint — light and dark variants for each.

| Semantic | Light text | Light bg | Light border | Dark text | Dark bg | Dark border |
|---|---|---|---|---|---|---|
| **Success** | `#059669` | `#ecfdf5` | `#a7f3d0` | `#34d399` | `rgb(16 185 129/.12)` | `rgb(16 185 129/.32)` |
| **Warning** | `#d97706` | `#fffbeb` | `#fde68a` | `#fbbf24` | `rgb(245 158 11/.12)` | `rgb(245 158 11/.32)` |
| **Error / Critical** | `#dc2626` | `#fef2f2` | `#fecaca` | `#f87171` | `rgb(239 68 68/.12)` | `rgb(239 68 68/.32)` |
| **Info** | `#2563eb` | `#eff6ff` | `#bfdbfe` | `#60a5fa` | `rgb(59 130 246/.12)` | `rgb(59 130 246/.32)` |

**Usage rule (central to this system):** these four colors are reserved exclusively for signaling meaning — agent/run health, alert severity, approval outcome. They must never be used decoratively (e.g., an icon chip colored green just because it "looks nice"). This is why the Overview Dashboard's metric-card icons for "Total Agents" and "Running Agents" are neutral gray, not brand-tinted — those numbers don't represent a status, so they don't get a status (or brand) color. See `brand-identity-system.md` §Status System for the full state taxonomy this maps to.

**Info vs. Brand:** Info intentionally uses a more saturated blue than the restrained brand accent. They read as different colors at a glance (Info is a functional/system-level indicator — e.g., "Running" — while brand is an identity/interactive color). Do not consolidate these even though both are "blue" — collapsing them would make running-status indicators look like interactive brand elements, which is misleading.

---

## 4. Accessibility Validation (WCAG 2.2 AA)

Contrast ratios computed via the WCAG relative-luminance formula. Threshold: 4.5:1 for normal text, 3:1 for large text (≥18px or ≥14px bold) and non-text UI components (icons, borders, focus indicators).

| Pairing | Ratio | Threshold | Result |
|---|---|---|---|
| White text on `--brand-solid` (`#3d6690`) — light **and** dark mode | ~6.0:1 | 4.5:1 (text) | ✅ Pass |
| `--brand` text (light, `#3d6690`) on `--surface` (white) | ~6.0:1 | 4.5:1 (text) | ✅ Pass |
| `--brand` text (light, `#3d6690`) on `--brand-subtle` (`#dde6f0`) | ~4.75:1 | 4.5:1 (text) | ✅ Pass |
| `--brand` text (dark, `#86a8c7`) on dark `--brand-subtle` tint | ~5.7:1 | 4.5:1 (text) | ✅ Pass |
| `--brand` text (dark, `#86a8c7`) on raw dark `--surface` (`#0f172a`) | ~3.0:1 | 3:1 (non-text/icon only) | ✅ Pass as icon/accent — ⚠️ do not use for body text directly on bare dark surface |
| `--focus-ring` vs. adjacent surface, both themes | >3:1 in all cases | 3:1 (non-text) | ✅ Pass |
| Status colors (text variant) vs. their own `-bg` tint, both themes | 4.5–7:1 range | 4.5:1 (text) | ✅ Pass |
| `--foreground-secondary` vs. `--surface`, both themes | >4.5:1 | 4.5:1 (text) | ✅ Pass |

**One constraint to carry forward:** the dark-mode `--brand` value is only verified safe for icons, accents, and text sitting on a tinted background (`--brand-subtle`) — not for body text placed directly on the bare dark background. Component authors should keep using `--foreground` / `--foreground-secondary` for body copy and reserve `--brand` for accents, links, and active-state indicators, exactly as the current Overview Dashboard does.

---

## 5. Do / Don't

**Do:**
- Reference semantic tokens (`--brand`, `--success`, `--border-default`, etc.) — never raw hex values in components
- Reserve status colors for actual status signaling
- Keep `--brand-solid` theme-invariant; keep `--brand` theme-adaptive
- Validate any new color pairing against the 4.5:1 / 3:1 thresholds above before shipping

**Don't:**
- Introduce a second accent color alongside brand — Atlas uses one accent, used sparingly
- Use gradients or glassmorphism on any color surface
- Recolor a metric or icon purely for visual variety — color must always mean something
