# ADR-002 - Human Approvals Decision Integrity and Continuation

**Status:** Accepted
**Date:** 2026-07-13
**Decision Owners:** Architecture and Security Review
**Scope:** Human Approvals

---

## Context

A Human Approval must record one authoritative decision, preserve the exact
context reviewed by the operator, make workflow continuation recoverable, and
prevent duplicate external action intent.

Decision, audit evidence, and continuation cannot be independent best-effort
writes. External providers also cannot always prove whether an action occurred
after a timeout or connection failure, so Atlas cannot promise absolute
at-most-once external side effects across every connector.

PostgreSQL is the planned runtime system of record. Existing Atlas architecture
already separates Approval Service, Policy Engine, Agent Runtime, Connector
Runtime, and Audit Writer responsibilities.

---

## Decision

Atlas adopts the following integrity model:

1. Every decision attempt supplies a monotonic approval revision or equivalent concurrency identity.
2. One authoritative transaction records the terminal approval transition, reviewer provenance, decision reason, durable audit event, and durable continuation intent.
3. Continuation uses a transactional outbox or an equivalent pattern with the same atomicity and recovery properties.
4. Continuation consumers are idempotent and revalidate the exact action.
5. Every decision binds to an immutable decision-context manifest containing action identity, evidence references, source versions, integrity identities, timestamps, and sensitivity metadata.
6. Atlas creates one authorized action intent and uses a stable dispatch idempotency identity.
7. Provider idempotency is used where available.
8. Uncertain external execution becomes `Indeterminate`; automatic retry is prohibited until reconciliation establishes that retry is safe.
9. Durable local audit failure blocks decision acceptance.
10. Downstream audit export or telemetry failure retries asynchronously and does not reverse a durable decision.

---

## Rationale

This provides one authoritative decision, recoverable continuation, durable
audit provenance, stale and duplicate decision protection, historical evidence
integrity, and honest representation of uncertain external outcomes.

The pattern fits the existing modular architecture and planned PostgreSQL
system of record without introducing a new container or orchestration
framework.

---

## Consequences

### Positive

- Decision, audit, and continuation cannot diverge through independent writes.
- Continuation publication can recover after process failure.
- Duplicate local dispatch is suppressed.
- Historical review can verify the evidence context used for a decision.
- External uncertainty is not mislabeled as success or failure.

### Trade-offs

- Data design must support approval revisions, manifests, durable audit events,
  and continuation intents.
- An outbox dispatcher and idempotent consumer are required.
- Connectors need declared idempotency and reconciliation capabilities.
- Indeterminate outcomes require investigation and reconciliation.
- Retention must distinguish integrity metadata from sensitive content.

### Risks

- Incorrect consumer idempotency could still create duplicate dispatch.
- Weak integrity identities could undermine historical verification.
- Poor reconciliation tooling could leave indeterminate outcomes unresolved.
- Outbox backlog could delay continuation and requires observability.

---

## Alternatives Considered

### Independent decision and continuation writes

Rejected because partial failure can leave approval and continuation out of sync.

### Execute the external action inside the decision transaction

Rejected because external calls cannot participate reliably in the database
transaction.

### Absolute exactly-once external execution

Rejected because many providers cannot establish that guarantee under ambiguous
network failure.

### Snapshot all evidence into the approval record

Rejected because it duplicates sensitive data and complicates retention. Atlas
uses minimum snapshots only when stable versioned references are unavailable.

---

## Implementation Constraints

The Engineering Specification must define approval concurrency, transaction
boundaries, outbox behavior, consumer idempotency, connector capability
declarations, reconciliation, manifest representation, integrity mechanisms,
retention, redaction, metrics, alerts, and recovery procedures.

This ADR does not authorize implementation.
