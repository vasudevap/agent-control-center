# Atlas Information Architecture

**Status:** Approved  
**Version:** 1.0  
**Owner:** Product Design  
**Depends on:** 00-brand.md, 01-design-principles.md, 02-product-domain-model.md

---

# Purpose

This document defines how Atlas organizes information for operators.

It translates the Product Domain Model into a coherent navigation, information hierarchy, and screen structure.

---

# Information Architecture Principles

- Organize around domain objects, never implementation.
- Operational awareness precedes configuration.
- Every destination has one primary purpose.
- Navigation reflects stable concepts.
- Relationships should be discoverable without searching documentation.
- Users should move from summary to detail naturally.

---

# Mental Model

Atlas is a control plane.

Operators move between operational domains rather than individual tasks.

```text
Overview
    ↓
Agents
    ↓
Runs
    ↓
Evidence
    ↓
Action
```

---

# Primary Navigation

```text
Overview
Agents
Runs
Approvals
Alerts
Connectors
Policies
Artifacts
Audit
Settings
```

Future additions:

```text
Organizations
Environments
Users
Costs
Marketplace
Administration
```

---

# Navigation Hierarchy

```text
Overview

Agents
└── Agent Detail
    ├── Overview
    ├── Workflows
    ├── Runs
    ├── Outputs
    ├── Connectors
    ├── Policies
    ├── Health
    ├── Versions
    └── Configuration

Runs
└── Run Detail

Approvals

Alerts

Connectors
└── Connector Detail

Policies
└── Policy Detail

Artifacts

Audit

Settings
```

---

# Screen Responsibilities

## Overview

Answers:

> What requires my attention right now?

Primary information:

- Fleet Health
- Active Runs
- Pending Approvals
- Active Alerts
- Connector Health
- Recent Failures
- Upcoming Schedules

---

## Agents

Answers:

> Which agents exist and what is their current operational state?

Primary information:

- Identity
- Status
- Health
- Owner
- Last Run
- Next Run
- Version

---

## Agent Detail

Answers:

> How is this agent operating?

Primary sections:

- Overview
- Workflows
- Runs
- Outputs
- Connectors
- Policies
- Health
- Configuration
- Version History

---

## Runs

Answers:

> What executions have occurred?

Primary information:

- Status
- Trigger
- Duration
- Outcome
- Environment

---

## Run Detail

Answers:

> What happened during this execution?

Primary sections:

- Timeline
- Events
- Logs
- Evidence
- Outputs
- Artifacts
- Retry History

---

## Approvals

Answers:

> Which actions require authorization?

---

## Alerts

Answers:

> What requires investigation?

---

## Connectors

Answers:

> Can agents access external systems?

---

## Policies

Answers:

> Which governance rules are active?

---

## Artifacts

Answers:

> What durable outputs exist?

---

## Audit

Answers:

> Who changed what and when?

---

## Settings

Answers:

> How is this workspace configured?

---

# Information Hierarchy

Every operational view should present information in this order:

1. Identity
2. Status
3. Severity
4. Required Action
5. Activity
6. Relationships
7. History
8. Configuration

---

# Cross-Object Navigation

Primary objects should link directly to related objects.

Examples:

- Agent → Runs
- Run → Agent
- Run → Connector
- Run → Artifact
- Alert → Agent
- Policy → Affected Agents
- Connector → Dependent Agents

No relationship should require manual lookup.

---

# Search

Global search should index:

- Agents
- Runs
- Alerts
- Policies
- Connectors
- Artifacts
- Audit Events

Support:

- keyboard shortcut
- filters
- recent searches
- direct navigation

---

# Navigation Standards

- Persistent primary navigation
- Breadcrumbs on detail pages
- Consistent object detail layouts
- Maximum two navigation levels
- No critical workflow hidden behind modal dialogs

---

# Empty States

Every empty state explains:

- what belongs here
- why it is empty
- recommended next action

---

# Success Criteria

Operators should answer within five seconds:

- Is the platform healthy?
- Which agents need attention?
- What failed?
- What requires approval?
- Which connector has an issue?
- What changed?
- Where should I investigate next?

If these questions cannot be answered quickly, the information architecture should be revised before UI design proceeds.
