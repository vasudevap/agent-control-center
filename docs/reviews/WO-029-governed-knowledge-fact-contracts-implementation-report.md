# WO-029 Governed Knowledge Fact Contracts Implementation Report

**Status:** Implemented Locally - Pending PR, CI, and Merge
**Work Order:** [WO-029: Governed Knowledge Fact Contracts](../work-orders/029-governed-knowledge-fact-contracts.md)
**Implemented Branch:** `codex/wo-029-governed-knowledge-facts`
**Implementation Date:** 2026-07-18
**Engineering Specification:** [ES-005: Agent Framework and Governance Contracts](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**ADP:** [ADP-002: Phase 5 Agent Framework and Governance Contracts](../implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md)

## Summary

Implemented governed knowledge fact CRUD contracts over the Phase 3 persistence
foundation without adding knowledge questions, approval `facts_used`, Gmail
history learning, LLM extraction, live provider data, production retention
selection, or frontend productization.

## Scope Delivered

- Added migration `0009_knowledge_fact_contracts` for fact confirmation metadata
  and generic API idempotency records.
- Added `last_confirmed_at` support for facts while preserving immutable fact
  revisions as separate records.
- Added owner resolution through the existing one external product client to one
  human owner relationship.
- Added signed external-client create, list, read, update, confirm, stale
  volatile list, and soft-delete API contracts.
- Added explicit idempotency-key validation and persisted replay protection for
  state-changing fact operations.
- Added prohibited-content rejection for synthetic secret, credential,
  clinical-source, and protected-health values before persistence.
- Added audit events for material knowledge fact API actions with metadata-only
  audit payloads.
- Added focused API/service/schema tests for idempotency, revision history,
  confirmation, volatility staleness, soft deletion, authorization, owner
  linkage, OpenAPI security, and prohibited-content rejection.

## Explicit Non-Scope Preserved

- No knowledge question or answer lifecycle was implemented.
- No approval evidence, `facts_used`, or revalidation behavior was implemented.
- No Gmail-derived facts, Gmail OAuth, Gmail API calls, LLM extraction, provider
  data, production retention policy, or frontend productization was added.
- Deleted facts remain soft-deleted; evidence-relevant history is not destroyed.

## Validation

Local validation from `apps/api`:

```text
./.venv/bin/python -m pytest
./.venv/bin/python -m ruff check .
./.venv/bin/python -m mypy src
git diff --check
```

Result:

- `58 passed`
- `ruff`: all checks passed
- `mypy`: success, no issues in 40 source files
- `git diff --check`: passed

Known local warning:

- FastAPI/Starlette test client emits the pre-existing `httpx` deprecation
  warning from the local dependency set.

## Residual Risk

- PostgreSQL migration upgrade/downgrade evidence is expected from GitHub CI's
  backend migrations step.
- Idempotency records retain operation hashes and resource references only; final
  retention duration remains deferred to a later accepted retention/security
  review.
- Human dashboard access to knowledge facts remains deferred until dashboard
  authentication and productization authority exists.
