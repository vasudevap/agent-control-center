# Atlas User Experience

**Status:** Approved  
**Version:** 1.0  
**Owner:** Product Design  
**Depends on:** 00-brand.md, 01-design-principles.md, 02-product-domain-model.md, 03-information-architecture.md

---

# Purpose

This document defines how operators accomplish work in Atlas.

It specifies user journeys, interaction patterns, workflow standards, and UX conventions independently of visual design.

---

# UX Goals

Atlas should enable operators to:

- understand platform state immediately
- investigate issues efficiently
- govern autonomous systems confidently
- intervene safely
- complete common tasks with minimal cognitive load

---

# Primary User Goals

- Monitor platform health
- Operate an agent fleet
- Investigate executions
- Resolve failures
- Review approvals
- Manage integrations
- Govern agent behavior

---

# Primary User Journeys

## 1. Monitor Platform

Entry: Overview

Flow:

Overview → Alert → Agent → Run → Resolution

Success:

Issue identified within seconds.

---

## 2. Investigate Failure

Overview or Alert

↓

Run Detail

↓

Evidence

↓

Logs

↓

Connector / Policy

↓

Resolution

---

## 3. Review Approval

Approval Queue

↓

Approval Detail

↓

Evidence

↓

Approve / Reject

↓

Audit Recorded

---

## 4. Operate Agent

Agents

↓

Agent Detail

↓

Run / Pause / Configure

↓

Observe Status

---

## 5. Configure Connector

Connectors

↓

Connector Detail

↓

Authenticate

↓

Validate

↓

Available to Agents

---

# Interaction Patterns

Atlas uses a small number of consistent interaction patterns.

## Collection → Detail

Lists always navigate to object detail pages.

## Summary → Investigation

Dashboards summarize.

Detail pages explain.

## Inspect → Act

Users understand before acting.

## Configure → Validate

Configuration should always support validation before activation.

---

# Operational Workflows

Every workflow should follow:

Observe

↓

Understand

↓

Decide

↓

Act

↓

Verify

Users should never be forced to act without sufficient context.

---

# UX Standards

## Visibility

Current state is always visible.

## Feedback

Every action produces immediate feedback.

## Recovery

Failures provide clear recovery paths.

## Safety

High-risk actions require deliberate confirmation.

## Consistency

Equivalent objects behave identically.

---

# Navigation Behavior

- Preserve user context.
- Minimize page transitions.
- Prefer in-context inspection where practical.
- Support browser history naturally.
- Support keyboard navigation.

---

# Tables

Operational tables should support:

- sorting
- filtering
- search
- bulk actions
- column visibility
- saved views

---

# Detail Pages

Every object detail page should expose:

- Overview
- Current State
- Relationships
- Activity
- History
- Configuration

Structure should remain consistent across object types.

---

# Notifications

Differentiate between:

- Success
- Information
- Warning
- Critical Alert
- Approval Request

Notifications inform.

Alerts require action.

---

# Confirmation

Require confirmation for:

- deletion
- disabling
- credential changes
- policy changes
- destructive actions

Dialogs should explain consequences.

---

# Error Experience

Errors should state:

- what happened
- why it happened
- impact
- next step

Never use generic error messages.

---

# Loading Experience

Prefer:

- skeleton loading
- optimistic layout stability
- background refresh

Avoid blocking the interface unnecessarily.

---

# Empty States

Explain:

- expected content
- reason for absence
- recommended action

---

# Keyboard Experience

Support:

- global search shortcut
- command palette
- table navigation
- quick actions
- escape to close transient UI

---

# Responsive Experience

Desktop

Primary operational environment.

Tablet

Monitoring and investigation.

Mobile

Health, alerts, approvals, and intervention.

---

# UX Success Metrics

Operators should be able to:

- identify issues rapidly
- locate any agent quickly
- investigate failures efficiently
- complete approvals confidently
- recover from errors without assistance

Atlas should consistently feel calm, predictable, and in control.
