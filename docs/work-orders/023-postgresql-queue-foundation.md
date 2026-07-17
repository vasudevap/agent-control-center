# Work Order 023: PostgreSQL Queue Foundation

**Status:** Completed - Pending Merge
**Work Order ID:** WO-023
**Type:** Backend execution foundation
**Implementation Authorization:** Granted
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Architecture Authority:** [Agent Runtime](../architecture/09-agent-runtime.md), [Security Architecture](../architecture/07-security-architecture.md), [Data Architecture](../architecture/08-data-architecture.md)
**Prerequisites:** [WO-018](./018-postgresql-environment-and-migration-hardening.md), [WO-021](./021-api-contract-foundation.md)
**Review Record:** [WO-023 Queue Foundation Implementation Report](../reviews/WO-023-queue-foundation-implementation-report.md)

## 1. Purpose

Add a durable PostgreSQL-backed job queue without executing agents or adding a
separate broker.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Backend | PostgreSQL tables and transactions; no Redis or broker. |
| States | `queued`, `leased`, `retry_wait`, `succeeded`, `dead_letter`, `cancelled`. |
| Claiming | `SELECT ... FOR UPDATE SKIP LOCKED`, ordered by availability/priority/creation, in a short transaction. |
| Lease | Random lease token, owner ID, expiry timestamp; completion/retry requires matching unexpired token. |
| Lease bounds | Default 60 seconds; caller-selectable from 15 seconds to 15 minutes; explicit extension only. |
| Recovery | Expired leases return to claimable state and increment recovery evidence without duplicating terminal jobs. |
| Retry | Default five attempts, hard maximum ten; exponential policy metadata, next-available timestamp, and terminal dead-letter state. |
| Priority | Integer `0`–`100`, default `50`; lower values are claimed first. |
| Idempotency | Unique `(job_type, idempotency_key)` when a key exists; duplicate enqueue returns the existing job. |
| Payload | Typed job type plus minimal JSON metadata and resource references; no credentials, full email bodies, prompts, or attachments. |
| Time | UTC timestamps through an injected clock for deterministic tests. |

## 3. Approved Scope if Accepted

- Job migration/model, enqueue, claim, extend lease, succeed, retry, cancel, and
  dead-letter service functions.
- Validation limits for job type, priority, attempts, lease duration, and
  payload-reference schema.
- PostgreSQL concurrency tests for duplicate enqueue, competing claimers,
  expired lease recovery, stale token rejection, retry, and terminal state.
- Audit envelope hooks without implementing the full audit writer owned by
  WO-025.

## 4. Explicitly Out of Scope

Workers, agent execution, Gmail jobs, schedules, Redis, external queues, job
payload encryption, UI/API management endpoints, and production deployment are
excluded.

## 5. Verification and Completion

Require real PostgreSQL 18 integration/concurrency tests in CI, migration
upgrade/downgrade, full repository checks, secret/payload scans, report, and
governed merge.

## 6. Stop-and-Ask Triggers

Stop before adding a broker, worker loop, business job type, sensitive payload,
unbounded retries/leases, or a schema incompatible with PostgreSQL locking.

## 7. Review Notes

Accepted as part of the consolidated Phase 3 planning package. Implement only
after WO-021 has merged.
