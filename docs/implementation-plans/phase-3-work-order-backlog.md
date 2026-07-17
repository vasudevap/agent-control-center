# Phase 3 Work Order Backlog

**Status:** Draft - Planning Review Required
**Owner:** Repository Maintainer
**Date:** 2026-07-17
**Implementation Authorization:** Not Granted

---

## 1. Purpose

Define the planned Work Order sequence for the rest of Phase 3.

This is a backlog, not authorization. Each Work Order must still be drafted,
reviewed, accepted, implemented, validated, and merged independently.

## 2. Work Order Map

| Work Order | Name | Depends On | Parallelizable | Status |
| --- | --- | --- | --- | --- |
| WO-015 | Platform Foundation | ES-004 | Complete | Completed |
| WO-016 | Backend Runtime and Dependency Hardening | WO-015 | No | Planned |
| WO-017 | PostgreSQL Environment and Migration Hardening | WO-016 | No | Planned |
| WO-018 | Owner Authentication and Session Foundation | WO-017 | No | Planned |
| WO-019 | Authorization and External-Client Identity Boundary | WO-018 | No | Planned |
| WO-020 | API Contract Foundation | WO-019 | Limited | Planned |
| WO-021 | Webhook Delivery Hardening | WO-019, WO-020 | Yes, after dependencies | Planned |
| WO-022 | Queue Foundation | WO-017, WO-020 | Yes, after dependencies | Planned |
| WO-023 | Scheduler Foundation | WO-022 | No | Planned |
| WO-024 | Observability and Audit Baseline | WO-020, WO-022 | Yes, after dependencies | Planned |
| WO-025 | Phase 3 Integration Verification and Closeout | WO-016-WO-024 | No | Planned |

## 3. Planned Work Orders

### WO-016 - Backend Runtime and Dependency Hardening

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

### WO-017 - PostgreSQL Environment and Migration Hardening

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

### WO-018 - Owner Authentication and Session Foundation

Objective:

- Add owner-only dashboard authentication and secure session foundations.

Likely scope:

- owner identity configuration;
- login callback scaffold or identity-token validation boundary;
- signed secure session cookie foundation;
- logout/session invalidation;
- auth tests;
- no frontend integration unless explicitly authorized.

Out of scope:

- enterprise SSO;
- multiple users;
- full RBAC UI;
- Gmail OAuth.

### WO-019 - Authorization and External-Client Identity Boundary

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

### WO-020 - API Contract Foundation

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

### WO-021 - Webhook Delivery Hardening

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

### WO-022 - Queue Foundation

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

### WO-023 - Scheduler Foundation

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

### WO-024 - Observability and Audit Baseline

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

### WO-025 - Phase 3 Integration Verification and Closeout

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
