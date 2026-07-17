# Work Order 024: Scheduler Foundation

**Status:** Completed - Pending Merge
**Work Order ID:** WO-024
**Type:** Backend scheduling foundation
**Implementation Authorization:** Granted
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Architecture Authority:** [Agent Runtime](../architecture/09-agent-runtime.md), [Deployment Architecture](../architecture/06-deployment-architecture.md)
**Prerequisite:** [WO-023](./023-postgresql-queue-foundation.md)

## 1. Purpose

Create deterministic interval scheduling that transactionally emits queue jobs
without deploying a cron service or executing agents.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Schedule type | Fixed interval only in Phase 3; cron expressions and calendar/time-zone schedules are deferred. |
| Interval bounds | Minimum 60 seconds, maximum 30 days. |
| Time | All persisted and evaluated times are UTC; injected clock in tests. |
| Record | Schedule ID, job type/reference template, interval seconds, enabled flag, next due, last triggered, and version. |
| Trigger identity | Unique `(schedule_id, scheduled_for)` occurrence; enqueue uses the same deterministic idempotency key. |
| Atomicity | Lock due schedule, create occurrence/enqueue job, and advance `next_due_at` in one PostgreSQL transaction. |
| Catch-up | At most one overdue occurrence per schedule per sweep; next due advances from the scheduled occurrence. If more than 100 intervals behind, skip directly to the first future interval and audit the skipped count. |
| Concurrency | `FOR UPDATE SKIP LOCKED` prevents duplicate trigger across scheduler instances. |
| Runtime | Importable service plus one-shot CLI command; no daemon and no Render Cron provisioning. |

## 3. Approved Scope if Accepted

- Schedule and occurrence migration/models.
- Create/update/disable service boundaries for internal tests only, due query,
  transactional trigger, skip-ahead, and one-shot command.
- Audit envelope hook for created/changed/disabled/triggered/skipped decisions,
  compatible with the shared audit contract finalized by WO-025.
- PostgreSQL tests for boundary times, concurrent sweep, duplicate prevention,
  disabled schedules, delayed runs, catch-up, rollback, and queue integration.

## 4. Explicitly Out of Scope

Cron parsing, local time zones/DST, frontend schedule UI, public management API,
Render Cron deployment, worker execution, agent behavior, and missed-run alert
routing are excluded.

## 5. Verification and Completion

Require PostgreSQL 18 migration/integration/concurrency evidence, deterministic
clock tests, full repository validation, report, CI, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before adding cron/time-zone libraries, a hosted scheduler, automatic
agent execution, unbounded catch-up, or non-transactional enqueue behavior.

## 7. Review Notes

Accepted as part of the consolidated Phase 3 planning package. Implement only
after WO-023 has merged.

**Review Record:** [WO-024 Scheduler Foundation Implementation Report](../reviews/WO-024-scheduler-foundation-implementation-report.md)
