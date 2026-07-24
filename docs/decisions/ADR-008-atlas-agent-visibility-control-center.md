# ADR-008 - Atlas Agent Visibility and Lifecycle Control Center

**Status:** Accepted
**Date:** 2026-07-23
**Decision Owner:** Repository Maintainer
**Accepted:** 2026-07-23
**Accepted By:** Repository Maintainer
**Scope:** Atlas product boundary, operating model, and MVP definition
**Supersedes:** `ADR-003`, `ADR-004`, and `ADR-005` for the active Atlas product direction
**Related Decision:** `ADR-009 - Agent Enrollment, Authentication, and Telemetry Contract`

---

## Context

Atlas began as a place for its owner to see and understand independently built
AI agents: whether they are connected, healthy, producing failures, and still
trusted to report into the control center.

The first architecture expanded that purpose into an execution platform. It
assigned Atlas responsibility for schedules, queues, workers, agent execution,
connectors, provider credentials, policies, approvals, knowledge, artifacts,
and an external customer-facing product-client contract. The repository
contains substantial architecture and implementation evidence for that
direction, but the hosted product does not execute or maintain real external
agents end to end.

Continuing to describe the current product as a unified execution control plane
would overstate what it does and would keep the MVP spread across too many
unfinished responsibilities.

## Decision

Atlas will focus its active MVP on being a single-owner agent visibility and
lifecycle control center for agents that are built, deployed, scheduled, and
operated outside Atlas.

The active MVP will:

- enroll an externally operated agent and assign a stable Atlas identity;
- issue, rotate, and revoke a credential scoped to that agent;
- accept authenticated agent heartbeats and execution summaries through a
  versioned REST API;
- distinguish owner-declared metadata, agent-reported state, and Atlas-derived
  state;
- calculate connection and health state from authenticated observations;
- create and resolve operational alerts;
- show agents, executions, alerts, and material lifecycle activity;
- disconnect an agent from Atlas without claiming to terminate its external
  runtime;
- archive an agent while preserving operational history and audit evidence.

The active MVP will not:

- host agent source code or runtime processes;
- start, stop, pause, resume, schedule, or execute external agents;
- call an agent-owned health endpoint;
- hold the agent's provider credentials or business secrets;
- provide Atlas-managed connector execution;
- provide manual-run job intake, orchestration, approvals, governed knowledge,
  policies, artifacts, or tool execution;
- act as the governed backend for MushingMule or another external product
  client;
- claim that revoking Atlas access stops an agent outside Atlas.

## Product terminology

`Agent Control Center` remains the product name. For the active MVP, `control`
means control of the Atlas trust relationship and operational visibility:
enrollment, credential lifecycle, accepted telemetry, derived health, alerts,
disconnection, archival, and retained evidence.

`Control plane` may describe a later product only if Atlas gains accepted and
implemented desired-state or runtime-control capabilities. Until then, product
copy must not imply that Atlas deploys or executes agents.

The UI term `Execution` means an execution reported by an external agent.
It does not mean a job created or dispatched by Atlas.

## Ownership model

| Concern | Authority |
| --- | --- |
| Agent source, deployment, process, schedule, dependencies, tools, provider credentials, and business configuration | External agent owner and hosting environment |
| Atlas registration, credential state, accepted telemetry, derived health, alerts, lifecycle state, activity, and audit evidence | Atlas |
| Agent version, build identity, reported health, checks, and execution outcome | Agent report, stored as untrusted reported state |
| Last authenticated contact, missed-heartbeat state, and credential validity | Atlas observation |

Atlas must never collapse reported state into observed state. A connected agent
may report `healthy`, but Atlas alone determines whether a sufficiently recent,
authenticated report was received.

## Lifecycle boundary

The active lifecycle is:

```text
pending -> connected -> disconnected -> archived
             ^              |
             |--------------|
             new credential
```

- `pending`: registration exists, but no valid telemetry has been accepted.
- `connected`: at least one valid agent report has been accepted and an active
  credential exists.
- `disconnected`: Atlas credentials are revoked and telemetry is rejected.
- `archived`: the registration is hidden from normal active views while
  history remains retained.

Health is a separate derived dimension and must not be encoded into lifecycle
state.

## Existing capability disposition

Existing code and completed delivery evidence are not erased by this decision.

- Owner identity, session security, API, PostgreSQL, migrations, audit
  foundations, testing, CI, and hosting are reusable foundations.
- Agent registry, health, alerts, dashboard agent views, and runtime
  authentication require rework.
- Queue, scheduler, approvals, connectors, knowledge, Gmail behavior,
  policies, artifacts, webhooks, and related screens become dormant or future
  capabilities.
- Synthetic production seed behavior and fictional operational controls must
  be removed from the active product path under separately authorized work.
- Completed Engineering Specifications, Work Orders, implementation reports,
  reviews, migrations, and release evidence remain historical records.

## Consequences

### Positive

- Atlas has a narrow, testable MVP with an honest product promise.
- Independently built agents can integrate through one stable contract.
- Agent onboarding and disconnection become first-class product flows.
- The product can demonstrate identity, trust boundaries, observability,
  lifecycle governance, and secure API design without owning execution.
- Existing platform foundations remain useful.

### Negative

- Much of the visible prototype and API surface becomes dormant.
- The current database and source tree will temporarily contain capabilities
  outside the active product boundary.
- Atlas cannot stop an external runtime or guarantee that a disconnected agent
  is no longer running.
- Agent-reported data can be incomplete or false and must remain visibly
  distinct from Atlas observations.

## Superseded decisions

ADR-003, ADR-004, and ADR-005 remain historical evidence for the original
execution-platform and external-product-client direction. They no longer govern
active Atlas product work.

ADR-002 remains an accepted design for any future approval capability but is
outside the active MVP.

ADR-006 remains an accepted historical connector OAuth decision but its
connector capability is outside the active MVP.

ADR-007 remains active for single-owner Atlas identity.

## Implementation authority

This ADR changes product and architecture authority. It does not authorize code
changes, database deletion, router removal, production data mutation, or
deployment. Those require an accepted Engineering Specification and bounded
Work Orders.

## Revisit triggers

Revisit this decision if Atlas is asked to:

- issue desired-state commands to agents;
- deploy, start, stop, or schedule agent runtimes;
- manage provider connectors or business credentials for agents;
- provide human approval for an external agent action;
- support multiple owners or organizations;
- support bidirectional streaming or agent callbacks;
- guarantee service levels that push-only telemetry cannot establish.
