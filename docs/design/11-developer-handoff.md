# Atlas Developer Handoff

> **Legacy broad handoff.** Active route and workflow authority is defined by
> DDR-003 and `12-agent-visibility-mvp-experience.md`.

**Status:** Draft
**Version:** 1.0
**Owner:** Product Design

---

# Purpose

This document defines how approved Atlas designs are translated into production implementation.

It establishes expectations, standards, and deliverables for engineering teams without prescribing application architecture.

---

# Objectives

Ensure that implementation:

- faithfully represents approved designs
- maintains consistency
- preserves accessibility
- minimizes ambiguity
- scales as the product grows

---

# Source of Truth

Engineering should implement in the following order of precedence:

1. Screen Specifications
2. Component Library
3. Design System
4. Visual Identity
5. Design Principles

If conflicts exist, resolve them before implementation.

---

# Design Deliverables

Each feature should include:

- Screen specification
- User flow
- Component usage
- Empty states
- Loading states
- Error states
- Accessibility requirements
- Acceptance criteria

No implementation should begin without these artifacts.

---

# Component Implementation

Every UI component should:

- map directly to the Component Library
- use Design System tokens
- support light and dark themes
- expose accessibility attributes
- avoid one-off styling

---

# Accessibility

Implementation should support:

- WCAG 2.2 AA
- keyboard navigation
- screen readers
- visible focus states
- semantic HTML
- reduced motion preferences

Accessibility defects should be treated as functional defects.

---

# Responsive Behavior

Desktop is the primary operating environment.

Responsive behavior should follow documented specifications rather than introducing alternative workflows.

---

# State Handling

Every screen should implement:

- loading
- empty
- success
- warning
- error
- disabled

State behavior should remain consistent across the application.

---

# Design QA

Before release, verify:

- spacing
- typography
- color usage
- component consistency
- interaction behavior
- accessibility
- responsive layouts
- visual regressions

---

# Design Change Process

Changes affecting user experience should:

1. Update design documentation.
2. Review affected screens.
3. Review affected components.
4. Update acceptance criteria.
5. Obtain design approval before implementation.

---

# Versioning

Design documentation and implementation should evolve together.

Breaking design changes require corresponding updates to:

- Screen Specifications
- Component Library
- Design System

---

# Acceptance Checklist

Before implementation is complete:

- Design matches approved specifications.
- Components conform to the Design System.
- Accessibility requirements are satisfied.
- Responsive layouts behave correctly.
- User flows are complete.
- Error handling is implemented.
- Empty states are implemented.
- Loading states are implemented.

---

# Long-Term Goal

Atlas should maintain a predictable relationship between design and implementation.

A new engineer should be able to implement any approved screen using only the Design System, Component Library, Screen Specifications, and this handoff guide with minimal clarification.
