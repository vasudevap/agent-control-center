# Atlas Component Library

**Status:** Draft
**Version:** 1.0
**Owner:** Product Design

---

# Purpose

This document defines every reusable UI component used throughout Atlas.

Components are implementation-independent specifications that promote consistency, accessibility, and reuse.

No production screen should introduce a new component without first extending this library.

---

# Component Principles

Every component should be:

- Reusable
- Accessible
- Composable
- Predictable
- Responsive
- Theme-aware

---

# Component Classification

## Foundations

- Color Tokens
- Typography
- Icons
- Spacing
- Elevation

## Inputs

- Button
- Icon Button
- Text Field
- Search Field
- Text Area
- Checkbox
- Radio Button
- Toggle
- Select
- Combobox
- Date Picker
- Time Picker

## Navigation

- Sidebar
- Top Navigation
- Breadcrumb
- Tabs
- Pagination
- Command Palette

## Feedback

- Toast
- Alert Banner
- Progress Indicator
- Skeleton Loader
- Empty State
- Error State
- Confirmation Dialog

## Data Display

- Card
- Table
- Badge
- Status Indicator
- Avatar
- Tooltip
- Timeline
- Activity Feed
- Key Value List
- Metric Card

## Operational

- Health Indicator
- Agent Card
- Run Timeline
- Approval Card
- Connector Status
- Policy Summary
- Audit Event Row
- Alert Card

## Overlays

- Dialog
- Drawer
- Popover
- Context Menu

---

# Component Specification Template

Every component should document:

- Purpose
- Usage
- Anatomy
- Variants
- States
- Behaviors
- Accessibility
- Responsive Rules
- Design Tokens
- Related Components

---

# Component States

Interactive components should support where applicable:

- Default
- Hover
- Focus
- Active
- Disabled
- Loading
- Error
- Success

---

# Button

Primary action component.

Variants:

- Primary
- Secondary
- Tertiary
- Destructive
- Icon Only

---

# Table

Primary operational component.

Capabilities:

- Sorting
- Filtering
- Search
- Pagination
- Bulk Selection
- Column Visibility
- Sticky Header
- Keyboard Navigation

---

# Status Indicator

Communicates operational state.

Semantic states:

- Healthy
- Running
- Scheduled
- Pending
- Warning
- Failed
- Disabled

Status should never rely on color alone.

---

# Timeline

Chronological presentation of events.

Used for:

- Runs
- Audit
- Activity
- Incidents

---

# Dialog

Reserved for:

- Confirmation
- Short Forms
- Critical Decisions

Avoid using dialogs for complex workflows.

---

# Drawer

Preferred for contextual inspection while preserving navigation context.

---

# Command Palette

Supports:

- Navigation
- Search
- Quick Actions
- Recently Used Items

Keyboard-first interaction.

---

# Accessibility

Every component must document:

- Keyboard behavior
- Focus management
- Screen reader support
- ARIA requirements
- Contrast requirements

---

# Responsive Behavior

Each component should specify:

Desktop

Tablet

Mobile

Behavioral differences where applicable.

---

# Versioning

Components follow semantic versioning.

Breaking changes require migration documentation.

---

# Governance

A new component should only be introduced if:

- Existing components cannot satisfy the requirement.
- The new pattern will be reused.
- Accessibility is documented.
- Design tokens are used.
- Engineering implementation has been reviewed.

---

# Success Criteria

The library is successful when:

- every screen is composed from documented components
- duplicate patterns do not exist
- accessibility is consistent
- implementation effort decreases over time
- the product maintains a cohesive visual language
