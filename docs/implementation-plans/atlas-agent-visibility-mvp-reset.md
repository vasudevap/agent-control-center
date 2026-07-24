# Atlas Agent Visibility MVP Reset Plan

**Status:** Accepted Direction and Planning Baseline
**Date:** 2026-07-23
**Owner:** Repository Maintainer
**Governing Decisions:** `ADR-008`, `ADR-009`, and `DDR-003`
**Implementation Authority:** None

## 1. Purpose

This plan translates the accepted Atlas direction reset into a controlled
sequence. It records what is retained, reworked, made dormant, or removed from
the active product path.

It does not authorize code, schema, production data, deployment, route, or
infrastructure changes.

## 2. Target outcome

Atlas becomes an honest, focused MVP for:

- owner-authenticated agent enrollment;
- per-agent credential lifecycle;
- heartbeat and execution ingestion;
- observed and reported health;
- operational alerts;
- agent detail and activity history;
- disconnect, reconnect, and archive.

The active product no longer depends on Atlas-owned agent execution, Gmail,
connectors, approvals, knowledge, queue workers, or synthetic smoke data.

## 3. Capability disposition

### 3.1 Retain

| Capability | Reason |
| --- | --- |
| Next.js application shell | Reusable authenticated product surface |
| FastAPI application foundation | Reusable versioned API and middleware |
| Google OIDC owner identity | Active single-owner boundary under ADR-007 |
| Owner sessions and CSRF | Active browser security controls |
| PostgreSQL and Alembic | Active system of record and migration mechanism |
| Structured errors and correlation | Required by the new API contract |
| Audit foundation and redaction | Required for credential and lifecycle evidence |
| Frontend and backend tests | Required quality baseline |
| CI and governance | Required delivery controls |
| Netlify, Render API, and Render PostgreSQL | Reusable hosted topology |
| Agents inventory visual foundation | Closest active product surface |
| Alerts visual foundation | Reusable after live condition integration |

### 3.2 Rework

| Capability | Required change |
| --- | --- |
| Agent registry | Add owner enrollment, lifecycle, environment, monitoring, references, and active mutations |
| External authentication | Replace one global product-client identity for agent ingestion with per-agent credentials |
| Agent Detail | Resolve real database agents and remove fixture-only controls |
| Runs | Replace Atlas job-intake semantics with read-only external Executions |
| Agent health | Separate observed connection health from reported health |
| Alerts | Derive from live heartbeat, check, execution, and security conditions |
| Audit page | Present material owner-facing Activity while retaining durable audit |
| Monitoring | Check database, evaluator, ingestion, and alert freshness |
| Readiness | Include persistence and required evaluator/configuration health |

### 3.3 Dismount from active navigation and API promise

- Approvals
- Connectors
- Policies
- Artifacts
- Knowledge
- Settings beyond real owner-session needs
- Manual run and cancel controls
- Schedules
- Gmail-specific operations
- External product-client interactions

Dismounting means the product no longer advertises the capability. It does not
authorize destructive deletion.

### 3.4 Leave dormant pending later decision

- PostgreSQL queue
- Interval scheduler foundation except code reused for the health evaluator
- Webhook delivery
- Connector models and services
- Approval and continuation services
- Knowledge models and services
- Gmail operational services
- Policy and artifact prototypes
- Historical external-client HMAC routes

Dormant code must not be used by the active navigation or normal MVP workflow.
Router unmounting, feature flags, source removal, and table removal require
explicit implementation scope.

### 3.5 Remove from normal production behavior

- Synthetic smoke seeding
- Synthetic agent, connector, run, and approval evidence
- Fixture fallback when a live API is expected
- Simulated pause, resume, run, cancel, approval, connector, policy, and
  settings actions
- Product copy claiming Atlas executed external work

Synthetic factories may remain test-only.

### 3.6 Preserve unchanged as history

- Completed Engineering Specifications
- Completed Work Orders
- Implementation and review reports
- Release and cutover evidence
- Existing migrations
- Original architecture and product specifications with supersession markers
- Git history and release tag evidence

## 4. Data disposition

- Do not roll back production to an older migration.
- Do not reinterpret synthetic `runs` as external executions.
- Add normalized active-MVP tables through forward migrations.
- Preserve existing rows until a later retention and cleanup decision.
- Exclude synthetic records from active production projections.
- Do not cascade-delete agent history on disconnect or archive.
- Do not store plaintext agent credentials.

## 5. Active API disposition

The accepted target is defined in
`docs/specifications/agent-integration-api.md`.

Implementation planning must explicitly map every current route to:

- retained;
- replaced;
- temporarily compatible but hidden;
- unmounted;
- test-only;
- removed in a later cleanup.

No current route is removed by this plan.

## 6. Delivery sequence

### Stage 0 - Direction reset

Deliver and accept:

- ADR-008
- ADR-009
- active MVP PRD
- agent integration API specification
- target architecture
- DDR-003 and active experience
- this disposition plan
- roadmap and repository orientation updates

Exit: the repository has one unambiguous active target.

### Stage 1 - Engineering specification

ES-009 is accepted. The Work Order and ADP package now carries the remaining
engineering-readiness gate:

- current-to-target component and route mapping;
- normalized schema and migration design;
- credential cryptography and lifecycle detail;
- telemetry validation and rate controls;
- health evaluator algorithm and leases;
- alert state machine;
- UI route plan;
- fixture and synthetic-data quarantine;
- deployment and rollback;
- verification and security plan.
- proposed Work Orders `WO-064` through `WO-071`;
- proposed ADP-006 execution package.

Exit: the Work Orders and ADP meet the Definition of Ready and are explicitly
accepted before implementation begins.

### Stage 2 - Active surface reduction

- Reduce navigation to five destinations.
- Remove simulated operational actions from active routes.
- Add honest pending and not-implemented states where backend work is not yet
  available.
- Keep dormant routes inaccessible from normal navigation.

Exit: the visible product no longer overclaims current capability.

### Stage 3 - Enrollment and credentials

- Add agent registration and credential persistence.
- Implement owner enrollment, rotation, disconnect, reconnect, and archive.
- Add one-time credential display and redaction tests.

Exit: the owner can establish and end an individual agent trust relationship.

### Stage 4 - Telemetry and health

- Implement heartbeat and execution contracts.
- Implement identity binding, idempotency, payload bounds, and negative tests.
- Implement health evaluator and alert lifecycle.

Exit: external agents produce live, derived operational state.

### Stage 5 - Live product integration

- Integrate Overview, Agents, Agent Detail, Executions, Alerts, and Activity.
- Remove normal production fixture fallback.
- Prove loading, empty, error, stale, disconnected, archived, and partial
  states.

Exit: the active product is fully service-backed.

### Stage 6 - Hosted migration and acceptance

- Apply forward migrations.
- quarantine synthetic hosted data;
- deploy source and evaluator;
- enroll three independent reference agents;
- execute lifecycle, health, alert, failure, rotation, disconnect, and archive
  acceptance tests;
- update runbooks and release evidence.

Exit: the accepted MVP success criteria are demonstrated.

## 7. Proposed Work Order sequence

The ES-009 Work Order package is created for review under ADP-006:

1. `WO-064` - Active navigation and synthetic fixture quarantine
2. `WO-065` - Agent Visibility schema and migration foundation
3. `WO-066` - Owner enrollment and agent credentials
4. `WO-067` - Heartbeat and execution ingestion
5. `WO-068` - Health evaluator and alert lifecycle
6. `WO-069` - Live dashboard integration
7. `WO-070` - Disconnect, reconnect, archive, and credential closeout
8. `WO-071` - Hosted reference-agent verification and ADP closeout

Implementation requires maintainer acceptance of the Work Orders and ADP-006
plus an explicit autonomous delivery execution window.

## 8. Stop-and-ask triggers

Stop and request direction if implementation would:

- delete existing production tables or historical records;
- expose or migrate a current secret;
- reuse the global external-client secret for enrolled agents;
- require Atlas to call or control an external agent;
- introduce a queue, worker, streaming platform, or SDK not accepted by
  ES-009;
- change the owner identity provider;
- use live third-party agent credentials or business data;
- require external deployment mutation beyond accepted authority;
- weaken CI, authentication, CSRF, audit, or redaction controls;
- reactivate a deferred capability.

## 9. Documentation closeout

Each implementation increment updates:

- active architecture and API contract if behavior changes;
- README current implementation;
- roadmap status;
- ES-009 and Work Order state;
- implementation evidence and residual risks;
- hosted runbooks when production behavior changes.
