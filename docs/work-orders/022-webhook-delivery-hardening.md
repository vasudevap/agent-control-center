# Work Order 022: Webhook Delivery Hardening

**Status:** Accepted - Implementation Authorized
**Work Order ID:** WO-022
**Type:** Backend notification foundation
**Implementation Authorization:** Granted
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Decision Authority:** [ADR-003](../decisions/ADR-003-governed-external-approval-decision-channel.md), [ADR-004](../decisions/ADR-004-governed-external-product-client-contract.md), [ADR-005](../decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md)
**Prerequisites:** [WO-020](./020-authorization-and-external-client-identity-boundary.md), [WO-021](./021-api-contract-foundation.md)

## 1. Purpose

Make outbound webhooks signed, minimized, retryable, deduplicated notifications
that never authorize actions or replace authoritative API reconciliation.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Event identity | Stable opaque event ID and event type; receiver deduplicates by event ID. |
| Signature | HMAC-SHA256 over event ID, timestamp, and exact serialized body; key ID and signature use dedicated headers. |
| Headers | `X-Atlas-Event-Id`, `X-Atlas-Event-Type`, `X-Atlas-Timestamp`, `X-Atlas-Key-Id`, and lowercase-hex `X-Atlas-Signature`. |
| Secret ownership | Signing keys are environment/provider secrets with current/next key IDs; database stores metadata only. |
| Payload | Versioned minimal notification containing identifiers/status hints and API reconciliation reference; no authoritative decision or sensitive body. |
| Serialization | Deterministic UTF-8 JSON bytes are signed exactly as transmitted. |
| Delivery states | `pending`, `delivering`, `retry_wait`, `delivered`, `failed`, `indeterminate`. |
| Retry | Maximum five attempts; exponential delays of 30s, 2m, 8m, and 30m; terminal failure after the fifth attempt. |
| Attempt timeout | Five seconds per fake/real transport contract; real transport remains unimplemented. |
| Success | Any `2xx`; redirects are not followed automatically; timeouts/network ambiguity become `indeterminate` and remain retryable within the attempt limit. |
| Transport | Fake recording transport for tests; no live network delivery in this work order. |

## 3. Approved Scope if Accepted

- Event/subscription/attempt persistence refinements and state transitions.
- Signature/key-rotation service, minimized payload validator, deduplication,
  retry scheduling, and reconciliation metadata.
- Fake-transport unit/integration tests for signing, tampering, retries,
  duplicate events, timeouts, redirects, terminal failures, and redaction.
- Event-type registry placeholders only for architecturally approved future
  events; no event generation from unimplemented workflows.

## 4. Explicitly Out of Scope

Live delivery, receiver code, approval/knowledge/Gmail event creation, webhook
authorization semantics, inbound webhooks, provider provisioning, and frontend
work are excluded.

## 5. Verification and Completion

Require PostgreSQL integration tests, deterministic fake-clock/transport tests,
all repository checks, secret scan, CI, implementation report, and merge.

## 6. Stop-and-Ask Triggers

Stop before adding live endpoints/secrets, treating delivery as authorization,
including prohibited content, changing retry limits materially, or adding a
third-party delivery service.

## 7. Review Notes

Accepted as part of the consolidated Phase 3 planning package. Implement only
after WO-020 and WO-021 have merged.
