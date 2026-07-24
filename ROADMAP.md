# Atlas Roadmap

## Purpose

This roadmap defines the active delivery sequence for the Atlas agent
visibility and lifecycle MVP.

The original execution-platform roadmap is preserved through Git history,
completed specifications, Work Orders, reviews, and the historical MVP release
boundary document.

## Product destination

Atlas gives one owner reliable visibility into independently operated agents
through:

- enrollment and stable identity;
- per-agent credentials;
- heartbeats and execution reporting;
- observed and reported health;
- alerts and material activity;
- credential rotation;
- disconnect, reconnect, and archive.

## Stage 0 - Direction reset

**Status:** Completed

Deliverables:

- ADR-008 product boundary
- ADR-009 enrollment and telemetry contract
- Agent Visibility MVP Product Requirements
- Agent Integration API
- Active target architecture
- DDR-003 and active product experience
- Capability disposition and reset plan
- Updated project, README, roadmap, and handoff

Exit criterion:

- One unambiguous active product and architecture direction exists.

## Stage 1 - Engineering readiness

**Status:** Completed

Deliverables:

- ES-009 Agent Visibility and Lifecycle MVP
- Current-to-target route map
- Schema and forward-migration design
- Credential cryptography and rotation design
- Telemetry validation and rate-control design
- Health evaluator algorithm and lease model
- Alert state machine
- Active UI implementation map
- Synthetic-data quarantine plan
- Deployment, validation, and rollback plan
- ADP-006 package
- Work Order sequence `WO-064` through `WO-071`

Exit criterion:

- Work Orders and ADP-006 meet the Definition of Ready, are accepted, and have
  explicit execution-window authorization before implementation begins.

## Stage 2 - Honest active surface

**Status:** Completed

Deliverables:

- Navigation reduced to Overview, Agents, Executions, Alerts, and Activity
- Dormant pages removed from normal navigation
- Simulated operational controls removed from active routes
- Clear current-capability and empty-state language
- Synthetic production seed path disabled from normal operation

Exit criterion:

- The visible product does not claim capabilities that are not operational.

## Stage 3 - Enrollment and trust lifecycle

**Status:** Completed

Deliverables:

- Owner-created registration
- Stable agent identity
- One-time per-agent credential
- Non-reversible credential persistence
- Credential rotation and expiry
- Disconnect, reconnect, and archive
- Lifecycle and credential audit evidence

Exit criterion:

- The owner can establish, rotate, end, and restore an individual agent's
  Atlas trust relationship.

## Stage 4 - Telemetry ingestion

**Status:** Completed

Deliverables:

- Heartbeat API
- Execution API
- Agent/path identity binding
- Contract version validation
- Idempotency and replay conflict handling
- Payload and rate bounds
- Redaction and prohibited-content rejection
- Python, TypeScript, and curl examples

Exit criterion:

- Independent agents can safely report through the same public contract.

## Stage 5 - Health and alerts

**Status:** Completed

Deliverables:

- Observed connection-health model
- Reported-health model
- Activity-only monitoring mode
- Scheduled health evaluator
- Missed-heartbeat alerts
- Reported-check alerts
- Repeated-execution-failure alerts
- Deduplication, acknowledgment, and recovery
- Evaluator freshness monitoring

Exit criterion:

- Atlas detects and explains operational attention conditions without calling
  an agent.

## Stage 6 - Live product integration

**Status:** Completed

Deliverables:

- Live Overview
- Live Agents inventory
- Live Agent Detail for database-backed agents
- Live Executions and detail
- Live Alerts
- Live Activity
- Loading, empty, error, stale, disconnected, archived, and partial states
- No normal production fixture fallback

Exit criterion:

- Every active product surface is backed by the accepted runtime contract.

## Stage 7 - Hosted MVP verification

**Status:** Blocked

Deliverables:

- Forward production migration
- Hosted evaluator deployment
- Synthetic-data quarantine
- Three independent reference agents
- Enrollment and first-connection evidence
- Failure, recovery, rotation, disconnect, reconnect, and archive evidence
- Security and privacy verification
- Updated runbooks and rollback evidence
- MVP acceptance report

Current blocker:

- The production Render API environment needs
  `ATLAS_API_AGENT_CREDENTIAL_PEPPER` and
  `ATLAS_API_AGENT_CREDENTIAL_PEPPER_KEY_ID` provisioned outside the
  repository before hosted reference-agent verification can complete.

Exit criterion:

- All active PRD success criteria pass against the hosted environment.

## Future capability shelves

The following are intentionally unsequenced:

- Atlas-directed commands
- Agent deployment and runtime management
- Scheduling and orchestration
- Connectors and provider credentials
- Human approvals
- Policies
- Knowledge
- Artifacts
- Webhooks
- Cost and trace observability
- Multi-user and multi-tenant operation

Reactivation requires a product requirement, architecture decision where
applicable, accepted Engineering Specification, and bounded Work Orders.

## Delivery rule

Completed historical work remains evidence. It is not counted as completion of
the new stages unless it directly satisfies the new acceptance criteria and is
explicitly adopted by ES-009.
