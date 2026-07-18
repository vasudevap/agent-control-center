# WO-042 Approval Gates, Edit-Then-Approve, and Send Continuation Implementation Report

**Work Order:** [WO-042](../work-orders/042-approval-gates-edit-then-approve-and-send-continuation.md)
**Status:** Completed - Merged
**Date:** 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing ADP:** [ADP-003](../implementation-plans/ADP-003-phase-6-gmail-agent-mvp-candidate.md)
**Pull Request:** [#60](https://github.com/vasudevap/agent-control-center/pull/60)
**Merge Commit:** `8f009146332d03b74b49837ec4abfb9bc27be0d2`
**Merged At:** 2026-07-18T19:50:20Z

## Summary

WO-042 adds governed Gmail send approval creation and approved-send
continuation. Send continuation revalidates approval status, draft identity,
draft body hash, source eligibility/suppression, connector authorization, and
`facts_used` bindings before calling a fake Gmail send provider.

No automatic send, live Gmail call, provider SDK, delete, forward,
unsubscribe, external sharing, multiple reviewer, delegated approval, quorum,
or dashboard productization behavior was introduced.

## Scope Implemented

- `gmail_send_outcome_records` persistence for `sent`, `failed`, and
  `indeterminate` outcomes.
- Gmail send approval creation from WO-041 draft records.
- Evidence payloads that include draft references, body hash, minimized draft
  metadata, and `facts_used`.
- Decision-context manifests that bind draft identity, source message,
  draft hash, and fact revision bindings.
- Compatibility with existing Phase 5 edit-then-approve supersession.
- Rejected approval stop before continuation.
- Approved continuation after fact, draft, source, and connector revalidation.
- Idempotent send continuation replay.
- Fake Gmail send provider with explicit sent, failed, and indeterminate
  outcomes.
- Minimized audit events for approval pending and send outcome events.

## Files Changed

- `apps/api/alembic/versions/0017_gmail_send_outcomes.py`
- `apps/api/src/atlas_api/models/gmail_message.py`
- `apps/api/src/atlas_api/models/__init__.py`
- `apps/api/src/atlas_api/services/gmail_approvals.py`
- `apps/api/tests/test_gmail_approvals.py`
- Phase 6 and WO-041/WO-042 status documentation.

## Validation Commands

Focused Gmail approval validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_gmail_approvals.py
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
Success: no issues found in 60 source files
```

Full backend validation:

```text
cd apps/api
./.venv/bin/python -m pytest
```

Result:

```text
123 passed, 1 warning
```

Migration validation:

```text
cd apps/api
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas-wo042-migration.db ./.venv/bin/alembic upgrade head
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas-wo042-migration.db ./.venv/bin/alembic current
```

Result:

```text
0017_gmail_send_outcomes (head)
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

- Send continuation requires an approved approval and never runs from pending
  or rejected approvals.
- Revalidation fails closed when fact revision bindings change.
- Draft provider reference and draft body hash must match the approved
  decision-context manifest.
- Suppressed sources are blocked before approval creation and send
  continuation.
- Send outcomes are explicit: `sent`, `failed`, or `indeterminate`.
- Indeterminate sends are recorded and not blindly retried with a new
  idempotency key.

## Residual Risks and Deferred Scope

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Fake send provider only | Expected | WO-044 owns controlled-account evidence if explicitly authorized. |
| No external-client API expansion | Expected | Existing Phase 5 approval APIs remain the external decision channel. |
| No dashboard productization | Expected | WO-043 owns operational reconciliation. |
| No live Gmail send | Expected | Live credentials require explicit maintainer authorization. |

## Completion State

WO-042 completed its governed pull-request review, required CI passed, and PR
[#60](https://github.com/vasudevap/agent-control-center/pull/60) was merged on
2026-07-18.
