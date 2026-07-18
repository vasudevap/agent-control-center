# WO-039 Low-Risk Mailbox Actions and Attachment Saving Implementation Report

**Work Order:** [WO-039](../work-orders/039-low-risk-mailbox-actions-and-attachment-saving.md)
**Status:** Completed - Merged
**Date:** 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing ADP:** [ADP-003](../implementation-plans/ADP-003-phase-6-gmail-agent-mvp-candidate.md)
**Pull Request:** [#57](https://github.com/vasudevap/agent-control-center/pull/57)
**Merge Commit:** `da766ccbc98e2c7dc20d9dd7769264545feac132`
**Merged At:** 2026-07-18T19:23:52Z

## Summary

WO-039 adds idempotent low-risk Gmail and Drive side-effect behavior after
message eligibility, classification, connector authorization, and WO-038
suppression checks pass.

The implementation supports fake-provider Gmail label application, Gmail
archive, Gmail attachment retrieval, and Drive attachment save using the
accepted `gmail.modify` and `drive.file` scopes only. It records each
side-effecting operation as a durable Gmail action operation and binds every
operation to an API idempotency record.

No send, delete, forward, unsubscribe, external sharing, live provider call,
drafting, approval creation, knowledge behavior, or dashboard productization
was introduced.

## Scope Implemented

- `gmail_action_operations` persistence for low-risk action outcomes.
- Fake Gmail action provider for label, archive, and attachment retrieval.
- Fake Drive provider for attachment saves under `drive.file`.
- Low-risk policy contract for category labels, archive categories, attachment
  save categories, and target Drive folder reference.
- Idempotency records for:
  - `gmail.apply_label`
  - `gmail.archive_message`
  - `gmail.get_attachment`
  - `drive.save_attachment`
- Suppression and review-required denial through the WO-038 downstream guard.
- Policy denial records when no low-risk action is approved for a category.
- Connector authorization checks for Gmail and Drive operations.
- Normalized provider-failure operation records with replayable outcomes.
- Minimized audit events for low-risk action outcomes.

## Files Changed

- `apps/api/alembic/versions/0015_gmail_low_risk_actions.py`
- `apps/api/src/atlas_api/models/gmail_message.py`
- `apps/api/src/atlas_api/models/__init__.py`
- `apps/api/src/atlas_api/services/gmail_actions.py`
- `apps/api/tests/test_gmail_actions.py`
- Phase 6 and WO-038/WO-039 status documentation.

## Validation Commands

Focused Gmail action validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_gmail_actions.py
```

Result:

```text
5 passed
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
Success: no issues found in 57 source files
```

Full backend validation:

```text
cd apps/api
./.venv/bin/python -m pytest
```

Result:

```text
103 passed, 1 warning
```

Migration validation:

```text
cd apps/api
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas-wo039-migration.db ./.venv/bin/alembic upgrade head
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas-wo039-migration.db ./.venv/bin/alembic current
```

Result:

```text
0015_gmail_actions (head)
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

- Provider fakes are deterministic and local-only; no live Gmail, Drive,
  credential, or external network path is introduced.
- Drive behavior uses the existing accepted `drive.file` connector scope.
- Suppressed Gmail message records are denied before action execution and
  create a denied action-operation record.
- Attachment content is not persisted; only safe attachment metadata, provider
  references, and hashes are retained.
- Audit metadata stores operation ids, resource ids, resource type, outcome,
  and reason codes only.

## Residual Risks and Deferred Scope

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Service is not yet wired into an agent run loop | Expected | WO-043 owns operational reconciliation. |
| No API endpoint or dashboard productization | Expected | WO-043 owns dashboard/external-client compatibility. |
| Low-risk policy is service-level, not user-configurable UI | Accepted for WO-039 | Later productization requires separate authority. |
| Fake Gmail and Drive providers only | Expected | WO-044 owns controlled-account evidence if explicitly authorized. |
| No high-risk actions or sends | Expected | WO-041 and WO-042 own draft/approval/send behavior. |

## Completion State

WO-039 completed its governed pull-request review, required CI passed, and PR
[#57](https://github.com/vasudevap/agent-control-center/pull/57) was merged on
2026-07-18.
