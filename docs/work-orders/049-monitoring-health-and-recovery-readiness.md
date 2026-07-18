# Work Order 049: Monitoring, Health, and Recovery Readiness

**Status:** Proposed - Pending Acceptance
**Work Order ID:** WO-049
**Type:** Observability and recovery readiness
**Implementation Authorization:** Not granted
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)
**Governing Plan:** [Phase 7 Work Order Backlog](../implementation-plans/phase-7-work-order-backlog.md)
**Prerequisites:** WO-043 completed and WO-047 readiness path accepted
**Review Record:** TBD

## 1. Purpose

Establish MVP health, readiness, log, metric, alert, scheduler, queue, webhook,
provider-error, and manual recovery expectations for single-owner operation.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Observability posture | Use existing logs, audit, health checks, and lightweight owner alerts for MVP |
| Alert audience | Single owner |
| Recovery model | Manual recovery is acceptable for MVP if documented |
| Sensitive data | Logs and alerts must stay minimized and redacted |

## 3. Approved Scope if Accepted

- Define health and readiness checks for API, database, connector availability,
  scheduler, queue, webhook dispatch, and Gmail/Drive provider errors.
- Verify structured logs include correlation IDs and run IDs where relevant.
- Define MVP metrics and alert thresholds for failed runs, stuck runs,
  indeterminate sends, provider throttling, webhook failures, credential
  revocation, and migration/runtime failures.
- Add manual recovery procedures for known MVP failure modes.
- Document what remains deferred until a post-MVP monitoring stack.

## 4. Explicitly Out of Scope

Full OpenTelemetry deployment, paid monitoring vendor adoption, on-call
rotation, multi-user support operations, chaos testing, load testing beyond MVP
readiness, and automated remediation are excluded unless separately accepted.

## 5. Verification and Completion

Require health/readiness tests where code changes are made, log redaction
checks, audit coverage review, simulated failure/recovery evidence where
practical, documentation review, and an implementation report under
`docs/reviews/`.

## 6. Rollback Expectations

Rollback must not remove existing audit coverage or redaction controls. If a
new alert path is faulty, it may be disabled through documented configuration
while preserving audit and health evidence.

## 7. Stop-and-Ask Triggers

Stop before adopting a new monitoring vendor, exposing sensitive message or
token data in logs or alerts, weakening audit controls, adding automated
provider side effects as recovery, or claiming high-availability readiness for
the MVP.
