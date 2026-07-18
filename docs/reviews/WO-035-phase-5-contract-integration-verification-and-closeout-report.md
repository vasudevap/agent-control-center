# WO-035 Phase 5 Contract Integration Verification and Closeout Report

**Work Order:** [WO-035](../work-orders/035-phase-5-contract-integration-verification-and-closeout.md)
**Status:** Completed - Merged
**Date:** 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing ADP:** [ADP-002](../implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md)

## Summary

Phase 5 now has a coherent generic agent framework and governance contract
layer. The closeout package adds a deterministic synthetic integration smoke
test across registry, run intake, governed knowledge, approval evidence,
`facts_used`, fail-closed revalidation, webhook notification, audit, and
authorization contracts.

No Gmail OAuth, Gmail provider calls, live credentials, live webhooks,
production deployment, frontend productization, or new product capability was
introduced.

## Closeout Evidence

The new closeout smoke test is:

```text
apps/api/tests/test_phase5_integration_closeout.py
```

It verifies:

- signed external-client access to the agent registry;
- manual run intake and reference-only run payloads;
- governed knowledge fact creation and prohibited-content rejection;
- approval evidence containing typed `facts_used` without fact display values;
- approval decision and pending continuation state;
- fact revalidation passing for unchanged facts;
- fact revalidation failing closed after a bound fact revision changes;
- fake webhook delivery for a Phase 5 run state event;
- durable metadata-only audit events;
- secret and sensitive-content exclusion from webhook/audit evidence.

## Validation Commands

Focused integration validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_phase5_integration_closeout.py tests/test_approval_facts.py tests/test_platform_events.py tests/test_runs.py tests/test_agent_registry.py
```

Result:

```text
23 passed, 1 warning
```

Full backend validation, lint, and typecheck:

```text
cd apps/api
./.venv/bin/python -m pytest
./.venv/bin/python -m ruff check .
./.venv/bin/python -m mypy src
```

Result:

```text
85 passed, 1 warning
All checks passed
Success: no issues found in 51 source files
```

Frontend validation because WO-034 added the dashboard compatibility seam:

```text
npm --workspace @atlas/web run test
npm --workspace @atlas/web run typecheck
npm --workspace @atlas/web run lint
npm --workspace @atlas/web run build
```

Result:

```text
18 test files passed, 84 tests passed
typecheck passed
lint passed
production build compiled successfully and generated 13 static pages
```

The production build may require network permission in the local sandbox for
approved Google Font fetches through `next/font`.

Migration validation:

```text
cd apps/api
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas_phase5_closeout_migration_3.db ./.venv/bin/alembic upgrade head
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas_phase5_closeout_migration_3.db ./.venv/bin/alembic current
```

Result:

```text
0011_run_lifecycle (head)
```

The migration check found two pre-existing SQLite migration mechanics defects
in `0006_webhook_delivery_hardening` and `0007_observability_audit_baseline`.
Both were fixed with Alembic batch operations. The schema intent is unchanged.

Secret-pattern scan:

```text
rg -n "(sk-[A-Za-z0-9]{12,}|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_[A-Za-z0-9]|BEGIN PRIVATE KEY|refresh_token|access_token|ghp_[A-Za-z0-9]|github_pat_[A-Za-z0-9])" --glob '!apps/web/.next/**' --glob '!apps/api/.venv/**' --glob '!node_modules/**' --glob '!.git/**' .
```

Result:

```text
No live secrets found. Matches were limited to prohibited-content detector
patterns and historical documentation examples of the scan command itself.
```

## Phase 5 Work Order Completion

| Work Order | Completion state |
| --- | --- |
| WO-027 Agent Registry and Runtime Contracts | Completed and merged |
| WO-028 Run Lifecycle and Job Intake Contracts | Completed and merged |
| WO-029 Governed Knowledge Fact Contracts | Completed and merged |
| WO-030 Knowledge Question and Answer Lifecycle | Completed and merged |
| WO-031 Approval Decision and Manual-Handling Contracts | Completed and merged |
| WO-032 Facts-Used Evidence and Revalidation Contracts | Completed and merged |
| WO-033 Webhook and Audit Event Contract Expansion | Completed and merged |
| WO-034 Dashboard Contract Compatibility Pass | Completed and merged |
| WO-035 Integration Verification and Closeout | Completed and merged |

## Residual Risks

| Risk | Status | Mitigation / next authority |
| --- | --- | --- |
| Dashboard remains fixture-driven | Accepted residual risk | Phase 4 productization or a dashboard integration ADP must authorize live API calls, auth/session behavior, loading/error states, and fixture removal. |
| No live Gmail provider behavior exists | Expected | Phase 6 must define Gmail OAuth, scopes, provider data handling, and safe action boundaries before implementation. |
| No live webhook delivery exists | Expected | A future work order must authorize live HTTP transport, receiver contracts, retries in deployed environments, and operational monitoring. |
| Audit browsing is not backed by a read API | Accepted residual risk | Add an audit read API only under accepted dashboard/productization scope. |
| Knowledge/manual-handling dashboard routes are absent | Accepted residual risk | Add product/design authority before implementing those operator surfaces. |
| `facts_used` is JSON-backed | Accepted for Phase 5 | If querying/reporting requirements emerge, propose a migration-backed index under a later work order. |

## Phase 6 Entry Criteria

Phase 6 Gmail Agent MVP Candidate may begin only after:

1. this WO-035 closeout PR is merged with CI passing;
2. ES-006 or equivalent Gmail-specific engineering specification is accepted;
3. Gmail OAuth/scopes, credential handling, and provider data boundaries are
   explicitly accepted;
4. Gmail work orders define message eligibility, clinical/PHI suppression,
   ask-instead-of-guess behavior, draft generation, approval gates, audit, and
   rollback expectations;
5. any live credentials or controlled account access are explicitly authorized
   by the Repository Maintainer.

## Out-of-Scope Confirmation

The closeout introduced no Gmail-specific behavior, no live provider calls, no
production resources, no broad frontend redesign, no framework adoption, and no
architecture change outside ES-005.
