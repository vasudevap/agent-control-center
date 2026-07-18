# WO-032 Facts-Used Evidence and Revalidation Contracts — Implementation Report

**Work Order:** [WO-032](../work-orders/032-facts-used-evidence-and-revalidation-contracts.md)
**Status:** Implemented Locally - Pending PR, CI, and Merge
**Date:** 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing ADP:** [ADP-002](../implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md)

## Summary

WO-032 binds approval evidence to exact governed knowledge fact revisions and
adds a fail-closed revalidation contract before approved work can continue.
The implementation uses the existing approval `evidence_summary` and
`decision_context_manifest` JSON fields rather than adding a new top-level
approval field or database migration.

No Gmail draft generation, LLM prompt assembly, connector execution, UI
productization, or production retention policy was added.

## Implemented Scope

- Added `atlas_api.services.approval_facts` with:
  - `facts_used` evidence items stored inside `ApprovalRequest.evidence_summary`;
  - `fact_revision_bindings` stored inside
    `ApprovalRequest.decision_context_manifest`;
  - exact revision binding by fact ID, revision ID, revision number, content
    hash, volatility flag, and confirmation timestamp;
  - revalidation that fails closed for missing, deleted, changed, integrity
    changed, prohibited, and stale volatile facts.
- Added `POST /api/v1/approvals/{approval_id}/facts-used/revalidate`.
- Added explicit external-client authorization for medium-risk approval fact
  revalidation.
- Added durable audit events for revalidation pass/fail outcomes with
  metadata-only counts and continuation status.
- Expanded observability metadata sanitization for safe revalidation summary
  fields.

## Failure Reason Codes

| Reason code | Meaning |
| --- | --- |
| `fact_missing` | The bound fact no longer exists for the approval owner. |
| `fact_deleted` | The bound fact is deleted or inactive. |
| `fact_revision_changed` | The fact's current revision no longer matches the approved evidence. |
| `fact_revision_missing` | The bound revision identity cannot be loaded. |
| `fact_integrity_changed` | The bound revision content hash no longer matches. |
| `fact_prohibited_content` | The bound revision is marked as prohibited content. |
| `fact_stale_volatile` | The bound volatile fact is stale and must be reconfirmed. |

## Validation Evidence

Focused local validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_approval_facts.py tests/test_approvals.py tests/test_authorization.py
```

Result:

```text
17 passed, 1 warning
```

Type validation:

```text
cd apps/api
./.venv/bin/python -m mypy src
```

Result:

```text
Success: no issues found in 51 source files
```

The warning is the existing FastAPI/Starlette `httpx` deprecation warning from
the local dependency stack.

## Security and Governance Notes

- `facts_used` is embedded in approval evidence and is not a parallel approval
  field.
- Evidence does not include fact `display_value` or answer text; it carries
  revision identity and integrity metadata.
- Revalidation only changes continuation readiness state. It does not execute a
  connector action or authorize work by itself.
- Changed, deleted, stale, and prohibited facts block continuation by setting
  `continuation_status` to `blocked`.

## Follow-Ups

- WO-035 should include this path in the synthetic Phase 5 closeout scenario.
- Phase 6 Gmail draft generation can consume `facts_used` only after Gmail
  scope and safety work orders are accepted.
