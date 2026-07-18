# WO-040 Ask-Instead-of-Guess and Governed Fact Use Implementation Report

**Work Order:** [WO-040](../work-orders/040-ask-instead-of-guess-and-governed-fact-use.md)
**Status:** Implemented - Pending PR Review
**Date:** 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing ADP:** [ADP-003](../implementation-plans/ADP-003-phase-6-gmail-agent-mvp-candidate.md)

## Summary

WO-040 connects Gmail draft prerequisites to the existing Phase 5 governed
knowledge contracts. It creates knowledge questions when required Gmail facts
are missing or stale, returns fresh governed fact revision ids when facts are
usable, validates answers through existing fact creation/update paths, and
blocks suppressed Gmail sources before question or learning behavior.

No draft generation, Gmail draft creation, approvals, send continuation,
history learning, live provider calls, clinical/PHI retention, or dashboard
productization was introduced.

## Scope Implemented

- Gmail draft-scenario required-fact mapping.
- Governed fact retrieval for active facts and current revisions.
- Stale volatile fact detection using the Phase 5 volatility window.
- Knowledge question creation for missing or stale required facts.
- Pending-question reuse for the same Gmail source and fact key.
- Answer submission through the existing Phase 5 question/answer path.
- Safe Gmail source references on answer-derived fact revisions.
- Suppressed-source exclusion before question creation or learning.
- Optional Phase 5 webhook enqueueing for question pending/answered events.
- Minimized audit events for knowledge-context preparation and question
  lifecycle events.

## Files Changed

- `apps/api/src/atlas_api/services/gmail_knowledge.py`
- `apps/api/tests/test_gmail_knowledge.py`
- Phase 6 and WO-039/WO-040 status documentation.

## Validation Commands

Focused Gmail knowledge validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_gmail_knowledge.py
```

Result:

```text
7 passed
```

Static validation:

```text
cd apps/api
./.venv/bin/python -m ruff check .
./.venv/bin/python -m mypy src
```

Result:

```text
All checks passed
Success: no issues found in 58 source files
```

Full backend validation:

```text
cd apps/api
./.venv/bin/python -m pytest
```

Result:

```text
110 passed, 1 warning
```

Whitespace validation:

```text
git diff --check
```

Result:

```text
Passed
```

## Security and Privacy Evidence

- Suppressed Gmail sources are rejected by the WO-038 downstream guard before
  creating questions, answers, facts, or learned candidates.
- Knowledge question source references use bounded Gmail provider references
  and do not include sender, subject, snippet, body, or attachment content.
- Answer text is validated by the existing Phase 5 prohibited-content checks
  before creating or updating facts.
- Questions remain separate from approvals; no approval request is created by
  the ask-instead-of-guess path.
- Webhook and audit payloads use existing minimized Phase 5 event contracts.

## Residual Risks and Deferred Scope

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Required-fact mapping is service-level and intentionally narrow | Accepted for WO-040 | Later productization can expand scenario configuration. |
| Draft generation is not implemented | Expected | WO-041 owns draft generation and facts-used evidence. |
| No approval or send behavior | Expected | WO-042 owns approval gates and send continuation. |
| No live Gmail provider calls | Expected | WO-044 owns controlled-account evidence if explicitly authorized. |

## Completion State

WO-040 is implemented with local validation complete and is ready for governed
pull-request review. It does not complete the ADP-003 merge gate until PR review
and required CI pass.
