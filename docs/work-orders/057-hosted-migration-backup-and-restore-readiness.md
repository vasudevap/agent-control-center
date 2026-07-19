# Work Order 057: Hosted Migration, Backup, and Restore Readiness

**Status:** Proposed - Pending Acceptance
**Work Order ID:** WO-057
**Type:** Hosted data cutover
**Implementation Authorization:** Not granted
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-055 Render PostgreSQL ready
**Review Record:** TBD

## 1. Purpose

Execute or rehearse hosted database migration with backup, restore, and
rollback evidence before production use.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Migration tool | Alembic |
| Target head | Current repository migration head |
| Backup posture | Confirm backup/restore path before migration |
| Rollback posture | Prefer corrective forward or restore with explicit evidence |

## 3. Approved Scope if Accepted

- Confirm Render PostgreSQL backup or export path.
- Run hosted migration only after explicit migration authority.
- Verify Alembic current head and application compatibility.
- Document restore procedure, migration failure handling, and corrective
  forward path.

## 4. Explicitly Out of Scope

Unreviewed destructive database commands, provider changes, business logic in
SQL, production data imports beyond migration, and release tagging are
excluded.

## 5. Verification and Completion

Require local migration validation, hosted migration evidence if authorized,
backup/restore evidence, migration-head evidence, rollback notes, and an
implementation report under `docs/reviews/`.

## 6. Rollback Expectations

Application rollback is not database rollback. Restore or corrective-forward
steps must be explicit, reviewed, and documented before closing the Work Order.

## 7. Stop-and-Ask Triggers

Stop before running hosted migrations without backup evidence, performing
destructive data changes, skipping restore expectations, or proceeding when
migration state is ambiguous.
