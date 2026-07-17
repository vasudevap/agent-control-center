# Work Order 025: Observability and Audit Baseline

**Status:** Accepted - Implementation Authorized
**Work Order ID:** WO-025
**Type:** Backend operational foundation
**Implementation Authorization:** Granted
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Architecture Authority:** [Observability Architecture](../architecture/11-observability.md), [Security Architecture](../architecture/07-security-architecture.md)
**Prerequisites:** [WO-021](./021-api-contract-foundation.md), [WO-022](./022-webhook-delivery-hardening.md), [WO-023](./023-postgresql-queue-foundation.md)

## 1. Purpose

Establish consistent structured operational logging and append-oriented audit
writing across the foundations built in Phase 3.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Logging implementation | Python standard-library logging with one-line JSON formatter; no external telemetry SDK. |
| Required log fields | UTC timestamp, component, severity, event type, correlation ID, and run/job/schedule IDs only when applicable. |
| Redaction | Central allowlist-first sanitizer; secrets, tokens, cookies, signatures, URLs with credentials, full bodies, and prohibited content are removed. |
| Audit separation | Audit records are durable PostgreSQL events written through a dedicated service, never inferred from logs. |
| Audit shape | Actor/channel/action/resource/result/reason/correlation/time plus minimal typed metadata. |
| Failure policy | Audit-required material changes fail closed if the audit event cannot be committed in the same transaction or durable handoff boundary. |
| Health | Liveness is process-only; readiness reports stable dependency/configuration problem codes without secrets. |
| Metrics/tracing | Typed metric-name placeholders and correlation propagation only; OpenTelemetry, exporters, dashboards, alerts, and SLO automation are deferred. |

## 3. Approved Scope if Accepted

- JSON formatter, structured event helper, redaction/sanitization utility, and
  correlation context propagation across API, webhook, and queue, plus the
  shared contract consumed by the independently implemented scheduler.
- Append-oriented audit writer and transaction-aware integration points for
  auth, authorization, webhook, queue, and schedule material events.
- Health/readiness convention alignment and tests.
- Tests for schema, redaction, correlation, audit persistence, rollback/failure
  policy, and separation between audit and operational logs.

## 4. Explicitly Out of Scope

OpenTelemetry deployment, hosted log/metric platforms, alert routing,
dashboards, production retention configuration, log shipping, immutable WORM
storage, frontend observability views, and business analytics are excluded.

## 5. Verification and Completion

Require PostgreSQL audit integration tests, captured-log/redaction tests, full
repository checks, CI, implementation report, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before adding a vendor/SDK, logging sensitive values, weakening an
audit-required failure policy, treating logs as audit records, or changing
retention/production monitoring architecture.

## 7. Review Notes

Accepted as part of the consolidated Phase 3 planning package. Implement only
after WO-021, WO-022, and WO-023 have merged.
