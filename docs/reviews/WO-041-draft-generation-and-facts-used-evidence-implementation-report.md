# WO-041 Draft Generation and Facts-Used Evidence Implementation Report

**Work Order:** [WO-041](../work-orders/041-draft-generation-and-facts-used-evidence.md)
**Status:** Implemented - Pending PR Review
**Date:** 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing ADP:** [ADP-003](../implementation-plans/ADP-003-phase-6-gmail-agent-mvp-candidate.md)

## Summary

WO-041 adds Gmail draft creation after eligibility, suppression, connector,
policy, generated-output validation, and governed-knowledge checks pass. Drafts
are created through a fake Gmail draft provider only and are never sent.

Draft records persist provider references, subject preview, body hash,
`facts_used` evidence, and decision-context bindings without storing full draft
or source message bodies.

## Scope Implemented

- `gmail_draft_records` persistence for draft references, hashes, evidence,
  and decision-context manifests.
- Fake draft generator boundary with strict output schema validation.
- Fake Gmail draft provider with explicit no-send test state.
- Missing/stale governed fact denial through WO-040 knowledge context.
- Suppressed-source denial through the WO-038 downstream guard.
- Prohibited generated-output rejection before provider draft creation.
- Connector authorization for `gmail.create_draft`.
- Idempotent draft creation using existing API idempotency records.
- Exact `facts_used` revision capture and `fact_revision_bindings`.
- Minimized audit events for denied, failed, and created draft attempts.

## Files Changed

- `apps/api/alembic/versions/0016_gmail_draft_records.py`
- `apps/api/src/atlas_api/models/gmail_message.py`
- `apps/api/src/atlas_api/models/__init__.py`
- `apps/api/src/atlas_api/services/gmail_drafts.py`
- `apps/api/tests/test_gmail_drafts.py`
- Phase 6 and WO-040/WO-041 status documentation.

## Validation Commands

Focused Gmail draft validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_gmail_drafts.py
```

Result:

```text
6 passed
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
Success: no issues found in 59 source files
```

Full backend validation:

```text
cd apps/api
./.venv/bin/python -m pytest
```

Result:

```text
116 passed, 1 warning
```

Migration validation:

```text
cd apps/api
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas-wo041-migration.db ./.venv/bin/alembic upgrade head
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas-wo041-migration.db ./.venv/bin/alembic current
```

Result:

```text
0016_gmail_drafts (head)
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

- Draft creation never calls send and the fake provider tracks no sent
  messages.
- Draft body is not persisted; only a SHA-256 body hash is stored.
- `facts_used` evidence references exact fact revisions without fact display
  values.
- Prohibited generated output is rejected before Gmail draft creation.
- Suppressed Gmail sources are rejected before generation or provider calls.
- No live Gmail credentials, provider SDKs, LLM framework, approval decision,
  or send continuation behavior was introduced.

## Residual Risks and Deferred Scope

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Draft generator is fake and deterministic | Accepted for WO-041 | Later model-backed generation must remain schema-validated and fail closed. |
| Approval creation and send continuation are not implemented | Expected | WO-042 owns approval gates and continuation. |
| No dashboard productization | Expected | WO-043 owns operational reconciliation. |
| No controlled-account evidence | Expected | WO-044 owns controlled-account verification if explicitly authorized. |

## Completion State

WO-041 is implemented with local validation complete and is ready for governed
pull-request review. It does not complete the ADP-003 merge gate until PR review
and required CI pass.
