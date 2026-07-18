# WO-038 Clinical and PHI Suppression Guardrail Implementation Report

**Work Order:** [WO-038](../work-orders/038-clinical-and-phi-suppression-guardrail.md)
**Status:** Implemented - Pending PR Review
**Date:** 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing ADP:** [ADP-003](../implementation-plans/ADP-003-phase-6-gmail-agent-mvp-candidate.md)

## Summary

WO-038 adds the Gmail clinical and protected-health-information suppression
guardrail immediately after message retrieval/classification and before any
downstream knowledge, question, draft, approval, action, send, or learning
behavior can consume a Gmail message.

Suppressed messages create minimized manual-handling records, emit safe audit
and optional webhook events, redact persisted sender/subject/label/attachment
display values, and expose an explicit downstream-use guard that later Phase 6
work orders must call before producing side effects.

No medical advice, clinical content processing, live Gmail calls, drafts,
approvals, low-risk actions, sends, or learning behavior were introduced.

## Scope Implemented

- `gmail_message_records` suppression fields:
  `suppression_status`, `suppression_reason_code`, and `manual_handling_id`.
- Deterministic clinical and PHI suppression detector contract.
- Fail-closed detector-schema validation to manual handling.
- Minimized manual-handling record creation through the existing Phase 5
  manual-handling contract.
- Redaction for suppressed message sender, subject preview, labels, attachment
  filename, snippet-derived hash, and source-integrity hash.
- Safe audit metadata allowlist additions for bounded suppression fields:
  `reason_category`, `sensitivity_classification`, and `suppressed_count`.
- Optional Phase 5 platform webhook enqueueing for
  `message.held_for_manual_handling` when a webhook context and active
  subscription are available.
- `ensure_gmail_message_allowed_for_downstream_use` guard for knowledge,
  question, draft, approval, action, send, and learning paths.

## Files Changed

- `apps/api/alembic/versions/0014_gmail_suppression_guardrail.py`
- `apps/api/src/atlas_api/core/observability.py`
- `apps/api/src/atlas_api/models/gmail_message.py`
- `apps/api/src/atlas_api/services/gmail_messages.py`
- `apps/api/tests/test_gmail_messages.py`
- Phase 6 and WO-037/WO-038 status documentation.

## Validation Commands

Focused Gmail suppression validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_gmail_messages.py
```

Result:

```text
9 passed
```

Connector compatibility validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_gmail_messages.py tests/test_connectors.py
```

Result:

```text
13 passed, 1 warning
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
98 passed, 1 warning
All checks passed
Success: no issues found in 56 source files
```

Migration validation:

```text
cd apps/api
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas-wo038-migration-v2.db ./.venv/bin/alembic upgrade head
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas-wo038-migration-v2.db ./.venv/bin/alembic current
```

Result:

```text
0014_gmail_suppression (head)
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

- Suppressed messages persist safe references and reason codes only; clinical
  sender, subject preview, label names, attachment filenames, and snippet
  hashes are redacted or replaced before storage.
- Suppression creates manual-handling records with bounded metadata:
  connector type, connection reference, provider references, and suppression
  reason code.
- Audit and webhook payloads use existing Phase 5 minimized contracts and do
  not include Gmail body, subject, sender, or attachment content.
- Detector schema failure suppresses the message and creates a
  `ProtectedHealthInformation` manual-handling record.
- Human approval cannot override suppression because suppressed messages are
  manual-handling records and the downstream guard rejects all approved
  downstream-use categories.

## Residual Risks and Deferred Scope

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Later Gmail actions must call the downstream guard before side effects | Expected | WO-039 through WO-042 must enforce this guard. |
| Rule-based detector is intentionally deterministic and conservative | Accepted for WO-038 | Later model-backed detection must remain schema-validated and fail closed. |
| Optional webhook enqueueing requires active subscriptions and signing settings | Expected | Existing Phase 5 webhook delivery contract owns subscription delivery. |
| No live Gmail or controlled-account verification | Expected | WO-044 owns controlled-account evidence if explicitly authorized. |
| No drafting, approvals, low-risk actions, sends, or learning | Expected | WO-039 through WO-042 own those behaviors after this gate is merged. |

## Completion State

WO-038 is implemented with local validation complete and is ready for governed
pull-request review. It does not complete the ADP-003 merge gate until PR review
and required CI pass.
