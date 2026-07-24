# Atlas Product Domain Model

> **Legacy broad domain model.** The active MVP domain is Agent, Agent
> Credential, Heartbeat, Execution, Health, Alert, Activity, Audit, and Owner
> Session as defined in the Agent Visibility MVP Experience.

**Status:** Approved  
**Version:** 1.0  
**Owner:** Product Design

---

# Purpose

This document defines the canonical domain model for Atlas.

It establishes the business concepts that make up the product. Every user interface, API, workflow, permission model, documentation artifact, and future capability should be built from these definitions.

This document defines **what exists**. It does not define **how those concepts are presented**.

---

# Domain Principles

- Every concept has one canonical name.
- Every concept has one primary responsibility.
- Objects relate through explicit relationships.
- The domain model is independent of UI implementation.
- New capabilities should extend existing objects before introducing new ones.

---

# Core Domain Hierarchy

```text
Workspace
└── Environment
    └── Agent
        ├── Workflow
        ├── Trigger
        ├── Schedule
        ├── Connector
        ├── Policy
        └── Run
            ├── Event
            ├── Log
            ├── Evidence
            ├── Output
            ├── Artifact
            └── Approval
```

---

# Domain Object Taxonomy

## Platform

- Workspace
- Environment
- User
- Team

## Operational

- Agent
- Workflow
- Run
- Trigger
- Schedule

## Integration

- Connector
- Credential
- Secret

## Governance

- Policy
- Approval
- Audit Event

## Observability

- Health
- Event
- Log
- Alert
- Incident

## Knowledge

- Output
- Artifact
- Evidence

---

# Canonical Object Definitions

## Workspace

Top-level operational boundary containing environments, users, teams, policies, and agents.

## Environment

Logical deployment boundary such as Development, Test, or Production.

## Agent

A governed autonomous capability with a defined purpose, configuration, lifecycle, permissions, and execution history.

## Workflow

A sequence of orchestrated actions performed by an agent to accomplish a capability.

## Trigger

A condition that initiates a run.

Examples include schedules, events, webhooks, and manual execution.

## Schedule

A time-based trigger definition.

## Run

A single execution instance of an agent.

A run is immutable once completed.

## Connector

A managed integration with an external system.

## Credential

A managed authentication grant used by a connector.

## Secret

Sensitive configuration that must never be exposed in plain text.

## Policy

A rule governing agent behavior or platform operation.

## Approval

A human decision required before a governed action may proceed.

## Event

A timestamped operational occurrence.

## Log

Detailed diagnostic information generated during execution.

## Health

The current operational state of an object.

## Alert

A condition requiring awareness or intervention.

## Incident

A significant operational issue affecting one or more platform objects.

## Output

A meaningful result produced by a run.

## Artifact

A persisted object produced or referenced by a run.

## Evidence

Supporting information explaining how or why an outcome occurred.

---

# Relationships

## Workspace

Contains:

- Environments
- Users
- Teams

## Environment

Contains:

- Agents
- Connectors
- Policies

## Agent

Owns:

- Workflows
- Triggers
- Runs

Uses:

- Connectors
- Policies

Produces:

- Outputs
- Artifacts

## Run

Contains:

- Events
- Logs
- Evidence

May require:

- Approval

Produces:

- Outputs
- Artifacts

---

# Lifecycle Models

## Agent

Draft

↓

Configured

↓

Validated

↓

Active

↓

Paused

↓

Disabled

↓

Archived

---

## Run

Queued

↓

Running

↓

Waiting for Approval

↓

Completed

or

↓

Failed

or

↓

Cancelled

---

# Ownership Rules

Every primary object should expose ownership.

Examples:

- Agent Owner
- Policy Owner
- Connector Owner
- Incident Owner

Objects without ownership are operational risks.

---

# Canonical Terminology

Always use:

- Agent
- Workflow
- Run
- Connector
- Policy
- Approval
- Artifact
- Output
- Environment
- Workspace

Avoid interchangeable synonyms.

---

# Future Extension Principles

Future features should extend the domain model without changing its conceptual structure.

Likely additions include:

- Organizations
- Projects
- Marketplace
- Templates
- Playbooks
- Knowledge Sources
- Model Registry
- Cost Objects

---

# Success Criteria

The domain model is successful when:

- every feature maps to existing objects
- terminology remains consistent
- relationships are explicit
- ownership is clear
- lifecycle is well defined
- future capabilities extend rather than replace the model
