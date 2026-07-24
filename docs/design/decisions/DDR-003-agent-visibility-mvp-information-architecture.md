# DDR-003 - Agent Visibility MVP Information Architecture

**Status:** Accepted
**Date:** 2026-07-23
**Owner:** Product Design
**Decision Owner:** Repository Maintainer
**Related Decisions:** `ADR-008` and `ADR-009`

## Decision

The active Atlas MVP navigation is:

```text
Overview
Agents
Executions
Alerts
Activity
```

The active Agent Detail experience includes identity, lifecycle, credential
state, observed and reported health, version/build, recent executions, alerts,
activity, and owner actions for rotation, disconnect, reconnect, and archive.

`Runs` is renamed `Executions` because Atlas observes externally initiated
work; it does not dispatch jobs in the active MVP.

`Audit` is presented to the owner as `Activity`. The durable audit domain
remains distinct and retains security evidence that may be more detailed than
the owner-facing activity projection.

Approvals, Connectors, Policies, Artifacts, Knowledge, Settings, schedules, and
manual run controls are removed from active navigation. Existing routes may
remain dormant during implementation but must not be presented as active MVP
capabilities.

## Context

The original information architecture described a broad execution control
plane. ADR-008 narrows Atlas to enrollment, lifecycle trust, telemetry,
health, alerts, executions, and activity for external agents.

Leaving dormant screens in primary navigation would continue to overstate the
product and obscure the core onboarding and monitoring journeys.

## Primary journeys

1. Enroll an agent and copy its one-time configuration.
2. Confirm first connection.
3. Monitor fleet health and open alerts.
4. Investigate an agent, failed execution, or missed heartbeat.
5. Rotate a credential.
6. Disconnect an agent while understanding that the external runtime may
   continue running.
7. Reconnect or archive an agent.

## Consequences

- The shell becomes substantially smaller.
- Existing visual-system decisions remain valid.
- Current fixture-heavy screens become dormant rather than deleted by this
  decision.
- Agent Detail requires a live route for database-backed agents.
- Destructive-looking actions require explicit consequences and confirmation.
- Every health surface must distinguish observed from reported state.

## Alternatives considered

### Keep all existing navigation but label pages future

Rejected because primary navigation communicates product capability even when
individual pages contain disclaimers.

### Preserve `Runs`

Rejected for the MVP because the term implies Atlas-created work. `Execution`
accurately describes a unit of work reported by an external agent.

### Keep `Audit` as a primary user term

Rejected because the owner journey is operational history. The audit store
remains a security and governance mechanism beneath the Activity projection.

## Implementation authority

This DDR establishes design authority only. It does not authorize route
removal or UI implementation without an accepted Engineering Specification and
Work Order.
