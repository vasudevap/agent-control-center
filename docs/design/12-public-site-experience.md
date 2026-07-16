# Atlas Public Site Experience

**Status:** Approved
**Version:** 1.0
**Date:** 2026-07-15
**Owner:** Product Design
**Depends on:** 00-brand.md, 01-design-principles.md, 05-visual-identity.md,
06-visual-direction-selection.md
**Product Brief:** [Atlas Public Site Discovery Brief](../specifications/atlas-public-site-discovery-brief.md)

---

## 1. Purpose

This document defines the content architecture, first-release page structure,
responsive behavior, interaction model, and low-fidelity wireframe for the
public Atlas site.

It does not redefine the Atlas application interface. The public site is a
distinct explanatory surface that inherits the approved Atlas brand and Modern
Infrastructure visual direction.

## 2. Experience Goal

The public site should feel like the front door to a serious operating platform.
It must create confidence through structure, proof, and precise language rather
than promotional spectacle.

The desired visitor reaction is:

- I understand the operational problem.
- I understand why Atlas exists.
- I can see how human control and evidence shape the product.
- I know which capabilities exist today and which remain planned.
- I can inspect the underlying architecture.

## 3. Visual Direction

The site inherits **Modern Infrastructure**.

Public-site expression:

- neutral, warm-light primary canvas;
- dark operational product stage in the hero;
- precise sans-serif typography with a restrained serif accent for selected
  editorial statements;
- fine borders and subtle grid or topology motifs;
- product UI and data as the primary visual evidence;
- semantic color used sparingly;
- no robots, glowing orbs, circuit heads, stock photography, or generic AI
  gradients;
- limited, purposeful motion that respects reduced-motion preferences.

## 4. First-Release Information Architecture

The first release is a single-page site with stable section anchors:

```text
Home
├── Product
├── Control
├── Evidence
├── Architecture
├── Status
└── About the build
```

The navigation remains intentionally small. Product documentation, source
repository links, and a live product route may be added when public destinations
are approved and available.

## 5. Page Sequence and Content Requirements

### 5.1 Header

Required content:

- Atlas wordmark;
- `Enterprise Agent Control Center` descriptor;
- Product, Architecture, and Status anchor links;
- one primary `Explore Atlas` action.

### 5.2 Hero

**Eyebrow:** Enterprise Agent Control Center

**Headline:** Keep autonomous work under control.

**Supporting copy:** Atlas brings agents, runs, approvals, connectors, and
operational evidence into one governed workspace.

**Status:** In active development · Product prototype and architecture reference

**Actions:** Explore Atlas; View the architecture.

The hero uses a composed operational control-center preview built from HTML and
CSS. It may show agent health, an active run, an approval, and connector evidence
using fictional data.

### 5.3 Operational problem

Heading: **More agents should not mean less control.**

Show the transition from disconnected agents, schedules, credentials,
approvals, logs, and outputs to one governed operational layer.

### 5.4 Product pillars

1. **Control** — Operators remain able to inspect, pause, stop, and authorize.
2. **Trust** — Every material action should leave evidence.
3. **Clarity** — The system should make state, risk, and required action obvious.

Each pillar requires one concrete product example rather than abstract brand
copy.

### 5.5 Product walkthrough

Present four operational views: Fleet awareness, Run evidence, Human approvals,
and Governed connections. Pair each outcome statement with a compact product
representation.

### 5.6 Human authority feature

Heading: **Human authority is part of the architecture.**

Explain that approval is not a decorative confirmation dialog. Atlas is designed
to bind an exact action to its evidence, decision context, reviewer provenance,
and continuation state. Label the displayed workflow as a frontend prototype.

### 5.7 Architecture

Heading: **Built as a control plane, not a collection of scripts.**

Show the Control plane, Execution plane, Agent and connector contracts, Policy
and approval boundaries, and Structured observability and audit evidence.

### 5.8 Capability status

Heading: **Clear about what exists today.**

Present Built, Designed, and Planned as visually distinct groups. Planned
capabilities must not appear equivalent to implemented behavior.

### 5.9 Reference implementation

Use the Gmail Triage Agent as evidence of how the architecture will be exercised.
Describe classification, labeling, draft preparation, attachment routing, and
human approval as planned reference behavior.

### 5.10 Closing action

Heading: **Autonomous systems should remain understandable.**

Primary action: Explore the Atlas product.
Secondary action: Review the delivery roadmap.

### 5.11 Footer

Include the Atlas identity and category, product status, current year, and a
concise statement that Atlas is in active development.

## 6. Low-Fidelity Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ ATLAS · Agent Control Center      Product Architecture Status│
├──────────────────────────────────────────────────────────────┤
│ [Category]                                                   │
│ KEEP AUTONOMOUS WORK UNDER CONTROL.   ┌─────────────────────┐│
│ Product explanation                    │ Operational preview ││
│ [Explore Atlas] [Architecture]         │ fleet/run/approval  ││
│ [In active development]                └─────────────────────┘│
├──────────────────────────────────────────────────────────────┤
│ More agents should not mean less control.                    │
│ disconnected state  ────────────────>  governed control plane│
├──────────────────────────────────────────────────────────────┤
│ CONTROL                    TRUST                    CLARITY   │
├──────────────────────────────────────────────────────────────┤
│ Product walkthrough: fleet / runs / approvals / connectors   │
├──────────────────────────────────────────────────────────────┤
│ Human authority feature         Approval evidence preview     │
├──────────────────────────────────────────────────────────────┤
│ Control plane  ───── governed boundary ─────  Execution plane │
├──────────────────────────────────────────────────────────────┤
│ BUILT                   DESIGNED                  PLANNED      │
├──────────────────────────────────────────────────────────────┤
│ Gmail reference implementation                               │
├──────────────────────────────────────────────────────────────┤
│ Autonomous systems should remain understandable. [Explore]   │
├──────────────────────────────────────────────────────────────┤
│ Atlas · status · architecture · roadmap                      │
└──────────────────────────────────────────────────────────────┘
```

## 7. Responsive Requirements

- Remain usable at 320 CSS pixels without document-level horizontal scrolling.
- Stack hero copy and operational preview on narrow screens.
- Reduce navigation links before removing the product action.
- Convert multi-column proof sections into ordered single-column narratives.
- Preserve Built, Designed, and Planned labels in every layout.
- Keep operational previews legible without requiring zoom.
- Meet accessible touch-target expectations.

## 8. Accessibility Requirements

- Target WCAG 2.2 AA.
- Use semantic landmarks and one page-level heading.
- Provide a keyboard-visible skip link.
- Maintain logical heading order and visible focus states.
- Do not rely on color alone for status, risk, or implementation maturity.
- Honor reduced-motion and contrast preferences.
- Preserve readable line lengths and text scaling at 200 percent zoom.
- Use real links for navigation and buttons only for actions.

## 9. Motion and Interaction

Allowed motion includes subtle product-evidence reveals, a restrained active-run
pulse, hover and focus transitions, and a navigation-surface transition. Motion
must stop or simplify under `prefers-reduced-motion`.

The first release does not require carousels, autoplay video, animated
backgrounds, cursor effects, or scroll-jacking.

## 10. Content Rules

- Prefer operational language over AI hype.
- Avoid anthropomorphism.
- Use `designed to` for architecture that is not implemented.
- Use `planned` for roadmap capability.
- Use `prototype` wherever displayed behavior could be mistaken for execution.
- Do not use fictional customers, metrics, quotes, or outcomes.
- Do not use `open source` until visibility and licensing support the claim.

## 11. Acceptance Criteria

- Every section has a defined visitor purpose.
- Hero, status language, and actions align with the discovery brief.
- Modern Infrastructure remains the visual direction.
- Claim maturity is explicit.
- The wireframe supports desktop and mobile ordering.
- No content requires unavailable production behavior.
