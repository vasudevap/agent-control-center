# Atlas Design System

**Status:** Draft
**Version:** 1.0
**Owner:** Product Design

---

# Purpose

This document defines the reusable design system for Atlas.

It establishes the visual and interaction rules that ensure every interface is consistent, scalable, accessible, and implementation-ready.

The Design System translates the Brand Strategy, Design Principles, and Visual Identity into reusable building blocks.

---

# Goals

The Atlas Design System should be:

- Consistent
- Predictable
- Accessible
- Scalable
- Themeable
- Enterprise-ready

---

# Foundations

The system is built upon:

- Design Tokens
- Layout Grid
- Spacing Scale
- Typography Scale
- Color Tokens
- Elevation
- Borders
- Motion
- Accessibility

---

# Design Tokens

Every visual property should originate from a design token.

Examples:

- color.surface.default
- color.text.primary
- spacing.16
- radius.md
- shadow.sm
- duration.fast

No hard-coded visual values should exist within components.

---

# Grid System

Desktop-first.

Recommended layout:

- 12-column responsive grid
- 8px spacing system
- Consistent gutters
- Maximum readable content width

---

# Spacing

Base unit:

8px

Preferred spacing scale:

4

8

12

16

24

32

48

64

Spacing communicates hierarchy before decoration.

---

# Typography

Typography hierarchy should define:

- Display
- Heading
- Title
- Body
- Label
- Caption
- Code

Typography should support dense operational interfaces.

---

# Page Headers and Navigation Labels

Top-level product screens must use a consistent title treatment so that moving
between primary navigation destinations does not shift or duplicate the page
hierarchy.

- The page title must use the exact concise label shown for its primary left-rail
  navigation destination. For example, the `Approvals` destination uses the
  `Approvals` page title.
- Put qualifiers, audience, scope, or explanatory context in the page
  description, not in a different or expanded primary title. For example,
  describe the Approvals page as human approval work in its description.
- A top-level destination must not render a breadcrumb that only repeats its
  left-rail label. Its shared page header begins at the same vertical position
  as other top-level destinations.
- Every product route must use the shared `PageContainer`, a `flex flex-col
  gap-8` content root, and `PageHeader` for its primary title. The title,
  optional description, icon, and contextual actions must not be recreated as
  bespoke page markup.
- Every primary and detail page header must include a concise description. For
  detail pages, use the object description when it is available.
- Section cards must use the shared `CardHeader`, `CardTitle`, and
  `CardDescription` hierarchy established by Fleet Health; page-header and
  card-header typography serve different semantic levels and must not be
  mixed.
- For a one-level detail destination, use a return action in the shared page
  header actions instead of a separate breadcrumb row. Use breadcrumbs only
  when they communicate multi-level hierarchy that a return action cannot.

---

# Color System

Color is semantic.

Primary categories:

- Surface
- Text
- Border
- Action
- Success
- Warning
- Critical
- Information

Never assign color purely for decoration.

## Approved Surface Hierarchy

Atlas uses layered surfaces to create hierarchy before adding decoration.

Light mode:

- The app canvas uses a cool off-white background.
- Primary content surfaces use white cards so important content stands forward.
- Control/filter surfaces use a softer secondary surface when they should
  support, not compete with, the main content.
- Borders are visible enough to define structure without becoming outlines.

Dark mode:

- The app canvas uses the darkest neutral background.
- Primary content surfaces use the next lighter neutral surface.
- Secondary surfaces and hover states use restrained neutral elevation.

Screen hierarchy rules:

- One primary content region per screen should read as the dominant surface.
- Supporting filters, summary controls, and secondary panels should be quieter
  than the primary content.
- Page-title icon chips use a white/primary surface, subtle border, and brand
  icon color so the page identity remains legible across light and dark modes.
- Avoid pure white-on-white light-mode compositions that flatten the interface.
- Avoid adding decorative color to solve hierarchy; use surface, spacing,
  typography, borders, and restrained elevation first.

---

# Elevation

Use minimal elevation.

Hierarchy should primarily be created through:

- spacing
- typography
- borders

Reserve shadows for overlays and floating surfaces.

---

# Border Radius

Rounded corners should remain subtle and consistent.

Avoid mixing radius values unnecessarily.

---

# Icons

Icons should:

- use one style
- align to pixel grid
- scale cleanly
- communicate operational meaning

---

# Motion

Standard motion categories:

- Enter
- Exit
- Expand
- Collapse
- Loading
- Progress

Motion durations should be tokenized.

---

# States

Interactive components should support:

- Default
- Hover
- Focus
- Active
- Disabled
- Loading
- Error

State transitions should remain consistent.

---

# Forms

Forms should provide:

- inline validation
- accessible labels
- keyboard navigation
- consistent helper text
- clear error messaging

---

# Tables

Tables are first-class components.

Support:

- sorting
- filtering
- pagination
- virtualization
- bulk selection
- keyboard navigation

---

# Data Visualization

Charts should:

- prioritize clarity
- support dark mode
- use semantic color
- maintain accessibility

---

# Accessibility

Target:

WCAG 2.2 AA

Support:

- keyboard navigation
- screen readers
- reduced motion
- high contrast
- semantic markup

---

# Theme Support

Both Light and Dark themes are required.

Theme switching should be token-driven.

---

# Responsiveness

Desktop:

Primary operating environment.

Tablet:

Monitoring and investigation.

Mobile:

Operational awareness and intervention.

---

# Component Governance

All reusable components should:

- originate from this system
- use design tokens
- remain backward compatible where practical
- be documented before adoption

---

# Versioning

Changes to the Design System should follow semantic versioning.

Breaking visual changes require documented migration guidance.

---

# Success Criteria

The Design System is successful when:

- interfaces remain visually consistent
- new screens can be built without inventing patterns
- accessibility is maintained
- themes remain synchronized
- engineering implementation is predictable
