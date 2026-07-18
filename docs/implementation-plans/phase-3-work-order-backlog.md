# Phase 3 Work Order Backlog

**Status:** Accepted - Implementation Sequenced
**Owner:** Repository Maintainer
**Date:** 2026-07-17
**Implementation Authorization:** Granted for accepted WO-019 through WO-026 in dependency order

---

## 1. Purpose

Define the planned Work Order sequence for the rest of Phase 3.

This is a backlog, not authorization. Each Work Order must still be drafted,
reviewed, accepted, implemented, validated, and merged independently.

## 2. Work Order Map

| Work Order | Name | Depends On | Parallelizable | Status |
| --- | --- | --- | --- | --- |
| WO-015 | Platform Foundation | ES-004 | Complete | Completed |
| WO-016 | Infrastructure Provisioning and Environment Strategy | WO-015 | Complete | Completed |
| WO-017 | Backend Runtime and Dependency Hardening | WO-016 | No | Completed |
| WO-018 | PostgreSQL Environment and Migration Hardening | WO-017 | No | Completed |
| WO-019 | Owner Authentication and Session Foundation | WO-018 | No | Completed |
| WO-020 | Authorization and External-Client Identity Boundary | WO-019 | No | Completed |
| WO-021 | API Contract Foundation | WO-020 | Limited | Completed |
| WO-022 | Webhook Delivery Hardening | WO-020, WO-021 | Yes, after dependencies | Completed |
| WO-023 | Queue Foundation | WO-018, WO-021 | Yes, after dependencies | Completed |
| WO-024 | Scheduler Foundation | WO-023 | No | Completed |
| WO-025 | Observability and Audit Baseline | WO-021, WO-022, WO-023 | Yes, after dependencies | Completed |
| WO-026 | Phase 3 Integration Verification and Closeout | WO-016-WO-025 | No | Completed |

## 3. Planned Work Orders

### WO-016 - Infrastructure Provisioning and Environment Strategy

Work Order:

- [`docs/work-orders/016-infrastructure-provisioning-and-environment-strategy.md`](../work-orders/016-infrastructure-provisioning-and-environment-strategy.md)

Objective:

- Document the infrastructure provisioning approach and environment strategy
  before additional backend implementation or live resource creation.

Likely scope:

- confirm Netlify dashboard hosting, Render backend hosting, and Render
  PostgreSQL as the initial hosted database target;
- decide the provisioning mechanism, such as manual provider runbook, Render
  Blueprint, Terraform, Pulumi, or another approved approach;
- define local, development, test, and production environment boundaries;
- define where PostgreSQL is installed or provisioned for local/test and hosted
  development/production use;
- define secret, environment variable, backup, restore, migration, rollback,
  region, tier, and access-control expectations;
- define whether an `infrastructure/` repository area is introduced now or
  deferred;
- create an ADR if the decision changes accepted hosting, deployment,
  persistence, or repository-structure architecture.

Out of scope:

- creating live Netlify or Render resources;
- provisioning production infrastructure;
- changing backend runtime code;
- implementing authentication, authorization, queue, scheduler, or webhook
  behavior.

### WO-017 - Backend Runtime and Dependency Hardening

Work Order:

- [`docs/work-orders/017-backend-runtime-and-dependency-hardening.md`](../work-orders/017-backend-runtime-and-dependency-hardening.md)

Objective:

- Make backend dependency installation, local commands, runtime settings, and
  CI behavior deterministic.

Likely scope:

- Python constraints or lock strategy decision and implementation.
- Backend command documentation.
- Runtime settings validation improvements.
- Local dev startup command standardization.
- CI cache and install refinement.

Out of scope:

- production deployment;
- authentication behavior;
- new operational endpoints;
- queue or scheduler.

Completion:

- Committed `apps/api/constraints.txt` defines the resolved backend dependency
  input used by both local setup and CI.
- Runtime settings accept only the documented environment names and have
  regression coverage for readiness requirements and secret redaction.
- No provider, migration, authentication, API-contract, queue, or scheduler
  scope was introduced.
- Evidence is recorded in [WO-017 Runtime Hardening Implementation Report](../reviews/WO-017-runtime-hardening-implementation-report.md).

### WO-018 - PostgreSQL Environment and Migration Hardening

Work Order:

- [`docs/work-orders/018-postgresql-environment-and-migration-hardening.md`](../work-orders/018-postgresql-environment-and-migration-hardening.md)

Objective:

- Move migration validation beyond SQLite substitute and define the approved
  local/test PostgreSQL path.

Likely scope:

- local PostgreSQL strategy;
- test database strategy;
- migration upgrade/downgrade commands;
- database engine/session dependency;
- migration smoke tests;
- documented handling for unavailable local PostgreSQL.

Out of scope:

- production database provisioning;
- data seeding for business workflows;
- Phase 5 knowledge contracts.

### WO-019 - Owner Authentication and Session Foundation

Work Order:

- [`docs/work-orders/019-owner-authentication-and-session-foundation.md`](../work-orders/019-owner-authentication-and-session-foundation.md)

Objective:

- Add owner-only dashboard authentication and secure session foundations.

Likely scope:

- owner identity configuration;
- login callback scaffold or identity-token validation boundary;
- opaque secure session cookie backed by a hashed server-side session;
- logout/session invalidation;
- auth tests;
- no frontend integration unless explicitly authorized.

Out of scope:

- enterprise SSO;
- multiple users;
- full RBAC UI;
- Gmail OAuth.

### WO-020 - Authorization and External-Client Identity Boundary

Work Order:

- [`docs/work-orders/020-authorization-and-external-client-identity-boundary.md`](../work-orders/020-authorization-and-external-client-identity-boundary.md)

Objective:

- Add deny-by-default authorization service and harden external-client identity
  separation from human attribution.

Likely scope:

- authorization context model;
- actor/channel/resource/action model;
- external-client credential metadata lifecycle;
- request signing or keyed authentication hardening;
- audit provenance for denied/accepted auth decisions;
- tests for fail-closed behavior.

Out of scope:

- multi-client behavior;
- approval decisions;
- operational knowledge writes.

### WO-021 - API Contract Foundation

Work Order:

- [`docs/work-orders/021-api-contract-foundation.md`](../work-orders/021-api-contract-foundation.md)

Objective:

- Standardize route, schema, error, pagination, idempotency, and OpenAPI
  conventions before broad API implementation.

Likely scope:

- response envelope conventions;
- pagination/filtering utilities;
- idempotency key validation helpers;
- rate-limit response shape;
- OpenAPI tags and examples;
- contract tests for placeholder and health routes.

Out of scope:

- full agent, run, approval, or knowledge CRUD;
- frontend integration.

### WO-022 - Webhook Delivery Hardening

Work Order:

- [`docs/work-orders/022-webhook-delivery-hardening.md`](../work-orders/022-webhook-delivery-hardening.md)

Objective:

- Prepare outbound webhook delivery for future approval, send outcome, manual
  handling, and knowledge notification events.

Likely scope:

- webhook signing;
- event identity and deduplication;
- retry scheduling;
- delivery status transitions;
- minimized payload validator;
- fake transport plus local integration tests.

Out of scope:

- live external delivery;
- event creation from Gmail or approval workflows;
- receiver implementation.

### WO-023 - Queue Foundation

Work Order:

- [`docs/work-orders/023-postgresql-queue-foundation.md`](../work-orders/023-postgresql-queue-foundation.md)

Objective:

- Add a PostgreSQL-backed job queue foundation.

Likely scope:

- job table migration;
- job status lifecycle;
- enqueue helper;
- claim/lease helper;
- retry and dead-letter fields;
- idempotency key handling;
- tests for duplicate prevention and no-sensitive-payload guardrails.

Out of scope:

- Redis;
- worker execution;
- Gmail jobs;
- agent business logic.

### WO-024 - Scheduler Foundation

Work Order:

- [`docs/work-orders/024-scheduler-foundation.md`](../work-orders/024-scheduler-foundation.md)

Objective:

- Add schedule records and due-trigger logic that can enqueue jobs without
  executing agents.

Likely scope:

- schedule table migration;
- due schedule query;
- duplicate trigger prevention;
- scheduler command or service function;
- audit event for trigger decisions;
- tests for interval/cron-like due calculations if selected.

Out of scope:

- Render Cron deployment;
- real agent execution;
- frontend schedule management.

### WO-025 - Observability and Audit Baseline

Work Order:

- [`docs/work-orders/025-observability-and-audit-baseline.md`](../work-orders/025-observability-and-audit-baseline.md)

Objective:

- Establish backend structured logging, audit helper, and health conventions
  across API, queue, scheduler, and webhook flows.

Likely scope:

- JSON log formatter;
- shared audit event writer;
- redaction helper;
- correlation propagation tests;
- health/readiness conventions;
- implementation report evidence.

Out of scope:

- full OpenTelemetry deployment;
- external monitoring platform;
- alert routing.

### WO-026 - Phase 3 Integration Verification and Closeout

Work Order:

- [`docs/work-orders/026-phase-3-integration-verification-and-closeout.md`](../work-orders/026-phase-3-integration-verification-and-closeout.md)

Objective:

- Verify Phase 3 foundations as one coherent platform baseline and prepare
  Phase 5 handoff.

Likely scope:

- end-to-end local smoke path across API, auth scaffold, DB, queue, scheduler,
  webhook fake transport, audit, and logs;
- residual risk review;
- Phase 5 prerequisites;
- status/index updates;
- closeout report.

Out of scope:

- new platform capabilities beyond fixing closeout findings;
- Phase 5 behavior.

## 4. Agent Assignment Guidance

Recommended agent shape:

- one agent per Work Order;
- no agent receives multiple unaccepted Work Orders;
- no agent starts from stale branch state;
- each agent begins from latest `main`;
- each agent opens one draft PR;
- each agent records implementation evidence.

Recommended model settings when assigning future work:

- `5.5 · High · Standard` for architecture-heavy Work Orders.
- `5.6 Terra · Medium · Standard` for well-scoped backend implementation.
- `5.6 Luna · Medium · Standard` for tests, cleanup, and mechanical docs.

## 5. Backlog Review Rule

Before starting each planned Work Order, review whether the previous merged
increment changed dependencies or scope. Update this backlog if the execution
path changes.
