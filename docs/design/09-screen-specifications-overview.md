# Atlas Screen Specifications — Part 1

> **Legacy screen baseline.** Active Overview, Agents, Agent Detail, and
> Executions responsibilities are defined in
> `12-agent-visibility-mvp-experience.md`.

**Status:** Draft  
**Version:** 1.0  
**Owner:** Product Design

> This document defines production screen specifications for the core Atlas experience.
> Additional screens will be documented in Part 2.

---

# Screen Specification Standard

Each screen defines:

- Purpose
- Primary Question
- Primary Objects
- Layout
- Primary Actions
- Secondary Actions
- States
- Success Criteria

---

# 1. Overview

## Purpose

Provide an operational summary of the platform.

## Primary Question

> What requires my attention right now?

## Layout

- Global Header
- Primary Navigation
- Health Summary
- Active Alerts
- Pending Approvals
- Fleet Health
- Active Runs
- Upcoming Schedules
- Recent Activity

## Primary Actions

- Investigate
- Approve
- Run Agent

## States

- Normal
- Warning
- Critical
- Empty
- Loading

---

# 2. Agents

## Purpose

Monitor all agents and investigate their operational state.

## Primary Question

> Which agents exist and what is their operational state?

## Layout

- Search
- Status and health filters
- Agent Table
- Mobile agent summaries
- Detail Navigation

## Columns

- Name
- Status
- Health
- Owner
- Last Run
- Next Run
- Version

## Primary Actions

- Open Agent Details

Registration, bulk actions, Run, Pause, Disable, and other state-changing
operations are excluded from this frontend-only milestone.

The detailed field hierarchy, ordering, responsive behavior, screen states,
interaction requirements, and acceptance criteria are defined by
[`Work Order 006 — Agents Inventory`](../work-orders/006-agents-inventory.md).
That Work Order is authoritative for `/agents`.

---

# 3. Agent Detail

## Purpose

Inspect and operate a single agent.

## Sections

- Overview
- Workflows
- Runs
- Outputs
- Connectors
- Policies
- Health
- Configuration
- Version History

## Persistent Actions

- Run Now
- Pause
- Disable

---

# 4. Runs

## Purpose

Review execution history.

## Layout

- Filters
- Search
- Runs Table

## Columns

- Run ID
- Agent
- Status
- Trigger
- Duration
- Started
- Finished

---

# 5. Run Detail

## Purpose

Explain everything that occurred during one execution.

## Sections

- Timeline
- Events
- Logs
- Evidence
- Outputs
- Artifacts
- Retry History

## Actions

- Retry
- Export
- Open Related Agent

---

# Global Requirements

Every production screen must support:

- keyboard navigation
- responsive layouts
- loading states
- empty states
- error states
- accessible focus order
- breadcrumb navigation where applicable
- deep linking

---

# Acceptance Criteria

Every screen should:

- answer one operational question
- expose current state immediately
- surface required actions
- support investigation
- preserve user context
