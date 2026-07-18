# WO-037 Gmail Message Eligibility, Retrieval, and Classification Implementation Report

**Work Order:** [WO-037](../work-orders/037-gmail-message-eligibility-retrieval-and-classification.md)
**Status:** Completed - Merged
**Date:** 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing ADP:** [ADP-003](../implementation-plans/ADP-003-phase-6-gmail-agent-mvp-candidate.md)
**Pull Request:** [#55](https://github.com/vasudevap/agent-control-center/pull/55)
**Merge Commit:** `3041ac64d10eeeef6b4d8d10d1bc323e3c1cb040`
**Merged At:** 2026-07-18T19:00:37Z

## Summary

WO-037 adds the Gmail message eligibility, fake-provider retrieval, minimized
message normalization, and classification foundation consumed by later Phase 6
Work Orders. It persists selected message metadata, provider references,
attachment metadata, classification output, confidence, review reason, and
integrity hashes without storing full Gmail message bodies.

No live Gmail calls, unrestricted mailbox scans, drafts, sends, approvals,
knowledge questions, low-risk actions, attachment saving, or learning behavior
were introduced.

## Scope Implemented

- `gmail_message_records` persistence for minimized Gmail message records.
- Fake Gmail provider contract for deterministic message listing and retrieval.
- Eligibility policy with query and maximum-message bounds.
- Gmail connection validation requiring an active Gmail connector and accepted
  `gmail.modify` scope.
- Rule-based classifier for the MVP categories needed at this layer, including
  safety classifications for `Clinical` and `Protected Health Information`.
- Fail-closed behavior to `Review Required` when classification confidence is
  below the accepted threshold.
- Idempotent upsert by owner, Gmail connection, and provider message reference.
- Audit event for retrieval/classification batches with minimized metadata.

## Files Changed

- `apps/api/alembic/versions/0013_gmail_message_classification.py`
- `apps/api/src/atlas_api/models/gmail_message.py`
- `apps/api/src/atlas_api/services/gmail_messages.py`
- `apps/api/src/atlas_api/models/__init__.py`
- `apps/api/tests/test_gmail_messages.py`
- Phase 6 and WO-036/WO-037 status documentation.

## Validation Commands

Focused Gmail message validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_gmail_messages.py
```

Result:

```text
4 passed
```

Full backend validation:

```text
cd apps/api
./.venv/bin/python -m pytest
./.venv/bin/python -m ruff check .
./.venv/bin/python -m mypy src
```

Result:

```text
93 passed, 1 warning
All checks passed
Success: no issues found in 56 source files
```

Migration validation:

```text
cd apps/api
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas_wo037_migration.db ./.venv/bin/alembic upgrade head
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas_wo037_migration.db ./.venv/bin/alembic current
```

Result:

```text
0013_gmail_messages (head)
```

Whitespace validation:

```text
git diff --check
```

Result:

```text
Passed
```

Scoped material scan:

```text
rg -n "full_body|raw_content|access_token|refresh_token|oauth_token|fake-provider-code|fake-health-code" apps/api/src apps/api/tests docs/reviews docs/work-orders/037-gmail-message-eligibility-retrieval-and-classification.md
```

Result:

```text
Matches are limited to negative test assertions, fake authorization-code test
fixtures from WO-036 tests, and prior documentation scan examples. No full
Gmail body storage or provider credential material was introduced.
```

## Security and Privacy Evidence

- `gmail_message_records` has no `body`, `full_body`, or `raw_content` column.
- Message snippets are stored only as SHA-256 hashes.
- Subject is stored as a bounded preview.
- Attachment metadata stores provider attachment references, filename, MIME
  type, and size only.
- Retrieval requires a connected Gmail connector with the accepted
  `gmail.modify` scope.
- Classification uncertainty fails closed to `Review Required`.
- Clinical and PHI are classified as safety categories but not yet suppressed;
  WO-038 owns the hard suppression gate before downstream behavior.

## Residual Risks and Deferred Scope

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Clinical and PHI are classified but not yet blocked from downstream flows | Expected | WO-038 implements the hard suppression guardrail. |
| Fake Gmail provider only | Expected | Controlled-account verification remains WO-044 or separate maintainer authorization. |
| Rule-based classifier is intentionally simple | Accepted for WO-037 | Later model-backed classification must remain schema-validated and fail closed. |
| No operational run wiring | Expected | WO-043 owns Gmail agent run reconciliation. |
| No Gmail actions, drafts, or sends | Expected | WO-039, WO-041, and WO-042 own those behaviors. |

## Completion State

WO-037 completed its governed pull-request review, required CI passed, and PR
[#55](https://github.com/vasudevap/agent-control-center/pull/55) was merged on
2026-07-18.
