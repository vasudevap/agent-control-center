# WO-030 Knowledge Question and Answer Lifecycle Implementation Report

**Status:** Implemented Locally - Pending PR, CI, and Merge
**Work Order:** [WO-030: Knowledge Question and Answer Lifecycle](../work-orders/030-knowledge-question-and-answer-lifecycle.md)
**Implemented Branch:** `codex/wo-030-knowledge-questions`
**Implementation Date:** 2026-07-18
**Engineering Specification:** [ES-005: Agent Framework and Governance Contracts](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**ADP:** [ADP-002: Phase 5 Agent Framework and Governance Contracts](../implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md)

## Summary

Implemented first-class knowledge question and answer lifecycle contracts so
Atlas can ask instead of guess without treating questions or answers as
approvals.

## Scope Delivered

- Added signed external-client question create, list, read, cancel, and answer
  APIs.
- Reused the existing `knowledge_questions` and `knowledge_answers` persistence
  foundation.
- Added idempotency protection for create and answer submission.
- Added answer validation through the governed fact service, including
  prohibited-content rejection before fact or answer persistence.
- Added answer-to-fact creation and update behavior through immutable fact
  revisions.
- Added lifecycle states for pending, answered, cancelled, and expired questions.
- Added durable audit events and OpenAPI security coverage.
- Added tests for duplicate handling, answer-to-fact mutation, cancellation,
  prohibited answer rejection, authorization boundary, and OpenAPI security.

## Explicit Non-Scope Preserved

- No approval clarification, approval decisions, Gmail ask behavior, LLM
  extraction, live provider data, frontend productization, or production
  notification delivery was added.
- Questions and answers do not authorize actions.
- Webhook event expansion remains deferred to WO-033.

## Validation

Local validation from `apps/api`:

```text
./.venv/bin/python -m pytest
./.venv/bin/python -m ruff check .
./.venv/bin/python -m mypy src
git diff --check
```

Result:

- `71 passed`
- `ruff`: all checks passed
- `mypy`: success, no issues in 48 source files
- `git diff --check`: passed

Known local warning:

- FastAPI/Starlette test client emits the pre-existing `httpx` deprecation
  warning from the local dependency set.

## Residual Risk

- PostgreSQL migration evidence is not required for this work order because no
  schema migration was added, but GitHub CI still validates the full migration
  chain.
- Webhook enqueue and event schema expansion for question pending/answered
  notifications remains part of WO-033.
