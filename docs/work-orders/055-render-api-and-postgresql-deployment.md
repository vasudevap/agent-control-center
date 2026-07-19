# Work Order 055: Render API and PostgreSQL Deployment

**Status:** Accepted - Pending Implementation
**Work Order ID:** WO-055
**Type:** Backend and database hosting cutover
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-19; pending WO-053 gate
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-053 environment map accepted
**Review Record:** TBD

## 1. Purpose

Deploy the Atlas FastAPI service and PostgreSQL database to Render using the
accepted runtime and deployment posture.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Provider | Render API service and Render PostgreSQL |
| Runtime | Existing backend Python/FastAPI contract |
| Database | PostgreSQL remains runtime system of record |
| Logs | Structured, minimized, and secret-free |

## 3. Approved Scope if Accepted

- Configure Render service, runtime, build/start command, health checks, and
  provider environment variables.
- Provision or bind the accepted PostgreSQL instance.
- Verify `/health/live`, `/health/ready`, logs, and redaction behavior.
- Record service URL, database boundary, provider rollback path, and known
  limitations.

## 4. Explicitly Out of Scope

Changing backend provider, adding infrastructure-as-code, running migrations
before WO-057, production mailbox use, public launch, and release tagging are
excluded.

## 5. Verification and Completion

Require backend tests/lint/typecheck, Render health/readiness evidence, log
redaction evidence, database binding evidence with values omitted, provider
rollback notes, and an implementation report under `docs/reviews/`.

## 6. Rollback Expectations

Rollback uses Render service rollback or corrective forward deployment.
Database rollback requires WO-057 backup/restore evidence and must not be
treated as application rollback.

## 7. Stop-and-Ask Triggers

Stop before exposing database URLs, running hosted migrations, changing
provider topology, weakening readiness checks, or deploying unreviewed source.
