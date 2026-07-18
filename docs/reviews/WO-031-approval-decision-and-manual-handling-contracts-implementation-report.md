# WO-031 Approval Decision and Manual-Handling Contracts Implementation Report

**Status:** Implemented Locally - Pending PR, CI, and Merge
**Work Order:** [WO-031: Approval Decision and Manual-Handling Contracts](../work-orders/031-approval-decision-and-manual-handling-contracts.md)
**Implemented Branch:** `codex/wo-031-approval-manual-handling`
**Implementation Date:** 2026-07-18
**Engineering Specification:** [ES-005: Agent Framework and Governance Contracts](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**ADP:** [ADP-002: Phase 5 Agent Framework and Governance Contracts](../implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md)

## Summary

Implemented generic approval queue, evidence read, decision submission,
edit-then-approve supersession, and manual-handling read contracts without
adding Gmail drafting, Gmail sending, connector action execution, LLM
generation, multi-reviewer behavior, delegation, frontend productization, or
live external webhook delivery.

## Scope Delivered

- Added migration `0010_approval_manual_handling` for approval requests,
  approval decisions, and manual-handling records.
- Added pending approval queue and evidence-read contracts over the signed
  external-client API boundary.
- Added approve, reject, and edit-then-approve decision submission with exact
  revision binding, expiry checks, idempotency, channel provenance, reviewer
  attribution, continuation intent status, and durable audit events.
- Implemented edit-then-approve as supersession of the original approval plus
  immediate approval of an exact replacement action hash.
- Added manual-handling records and read/list APIs that remain separate from
  approvals and cannot authorize action.
- Minimized manual-handling response metadata to suppress content-like,
  token-like, and secret-like keys.
- Added API, state-transition, idempotency, expiry, revision-conflict, audit,
  manual-handling separation, and OpenAPI security tests.

## Explicit Non-Scope Preserved

- No Gmail draft or send execution was implemented.
- No connector runtime action, LLM generation, provider SDK, live webhook
  delivery, frontend productization, reviewer delegation, roles, RBAC,
  multi-user, or multi-tenant behavior was added.
- Manual-handling records are not approvals and do not create an approval bypass.
- Continuation remains a persisted contract state only; no external action is
  dispatched.

## Validation

Local validation from `apps/api`:

```text
./.venv/bin/python -m pytest
./.venv/bin/python -m ruff check .
./.venv/bin/python -m mypy src
git diff --check
```

Result:

- `63 passed`
- `ruff`: all checks passed
- `mypy`: success, no issues in 43 source files
- `git diff --check`: passed

Known local warning:

- FastAPI/Starlette test client emits the pre-existing `httpx` deprecation
  warning from the local dependency set.

## Residual Risk

- PostgreSQL migration upgrade/downgrade evidence is expected from GitHub CI's
  backend migrations step.
- WO-033 must expand webhook event contracts before live or fake event enqueue
  coverage for approval/manual-handling notifications is considered complete.
- WO-032 must bind approval evidence to exact knowledge fact revisions before
  Gmail draft approval evidence can rely on `facts_used`.
