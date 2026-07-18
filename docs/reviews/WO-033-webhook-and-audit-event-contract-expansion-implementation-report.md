# WO-033 Webhook and Audit Event Contract Expansion — Implementation Report

**Work Order:** [WO-033](../work-orders/033-webhook-and-audit-event-contract-expansion.md)
**Status:** Implemented Locally - Pending PR, CI, and Merge
**Date:** 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing ADP:** [ADP-002](../implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md)

## Summary

WO-033 expands the existing Phase 3 webhook delivery foundation into a Phase 5
platform event contract. The implementation adds a canonical Phase 5 webhook
event registry, minimized payload schemas, producer-facing event builders, an
active-subscription enqueue helper, and tests for fake delivery, signing,
correlation, payload minimization, and durable audit records.

No live webhook delivery, receiver behavior, Gmail provider behavior, real
credentials, or production infrastructure was added.

## Implemented Scope

- Added canonical Phase 5 webhook event constants and payload schema metadata in
  `atlas_api.core.events`.
- Expanded the webhook delivery allowlist to include Phase 5 approval,
  manual-handling, knowledge, fact reconfirmation, and run state events while
  retaining legacy Phase 3 event compatibility.
- Added strict payload key validation that rejects sensitive-key fragments such
  as body, content, message, secret, text, token, credential, signature, and
  authorization.
- Added `PlatformWebhookEvent` builders for:
  - approval pending;
  - approval decided;
  - message held for manual handling;
  - knowledge question pending;
  - knowledge question answered;
  - knowledge fact reconfirmation required;
  - run state changed.
- Added `enqueue_platform_webhook_event` to enqueue notifications for active
  subscriptions that exactly match the event type.
- Preserved the existing fake-transport-only delivery model and durable webhook
  audit adapter.

## Validation Evidence

Local focused validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_platform_events.py tests/test_observability_and_audit.py tests/test_phase3_integration_closeout.py
```

Result:

```text
12 passed, 1 warning
```

Local type validation:

```text
cd apps/api
./.venv/bin/python -m mypy src
```

Result:

```text
Success: no issues found in 50 source files
```

The warning is the existing FastAPI/Starlette `httpx` deprecation warning from
the local test dependency stack.

## Security and Privacy Notes

- Webhook payloads remain notification summaries and are not authoritative
  action approvals.
- Event payloads contain only resource identity, status, reconciliation path,
  and bounded metadata needed for routing or safe reconciliation.
- Full message bodies, full user answers, OAuth material, secrets, signatures,
  and credentials are rejected from payload keys and are not present in test
  delivery bodies.
- Durable audit metadata remains sanitized through the existing observability
  allowlist.

## Out of Scope Confirmed

- No external HTTP transport was introduced.
- No provider-specific Gmail behavior was introduced.
- No webhook receiver implementation was introduced.
- No authorization semantics were delegated to webhook consumers.
- No production deployment or infrastructure behavior was introduced.

## Residual Risks and Follow-Ups

- Endpoint-level producers can call `enqueue_platform_webhook_event` once the
  application has an accepted subscription/runtime injection pattern for that
  route.
- WO-032 will add `facts_used` evidence and may use the fact reconfirmation
  event when revalidation fails closed.
- WO-035 should exercise the Phase 5 contracts as one synthetic integration
  path and confirm no sensitive content leaks across audit, logs, or webhook
  summaries.
