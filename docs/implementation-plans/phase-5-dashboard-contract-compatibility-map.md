# Phase 5 Dashboard Contract Compatibility Map

**Status:** Implemented Locally under WO-034 - Pending PR, CI, and Merge
**Date:** 2026-07-18
**Governing Work Order:** [WO-034](../work-orders/034-phase-5-dashboard-contract-compatibility-pass.md)
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)

## Purpose

This map records how the current fixture-driven dashboard can align with the
stable Phase 5 backend contracts without claiming full Phase 4 dashboard
productization complete.

The compatibility pass adds typed frontend contract adapters and tests only.
It does not add live API calls, signed external-client authentication in the
browser, production deployment, Gmail-specific UI, or new operator workflows.

## Surface Map

| Dashboard surface | Backend contract | Compatibility state | Notes |
| --- | --- | --- | --- |
| Agents | `/api/v1/agents` | Mapped | Agent inventory/detail concepts map to descriptors; health can be combined from the separate status/health contract later. |
| Runs | `/api/v1/runs` | Mapped | Run list/detail concepts map to Phase 5 run lifecycle fields and correlation IDs. |
| Approvals | `/api/v1/approvals` | Mapped | Queue/detail concepts map to summaries and evidence payloads without executing actions. |
| Manual handling | `/api/v1/manual-handling` | Deferred | Backend contract exists, but no first-class dashboard route exists yet. |
| Audit | `audit_events` durable records | Mapped | The fixture audit surface aligns with durable audit identity and result fields; no read API exists yet. |
| Knowledge facts | `/api/v1/knowledge/facts` | Deferred | Backend contract exists, but no first-class dashboard route exists yet. |
| Knowledge questions | `/api/v1/knowledge/questions` | Deferred | Backend contract exists, but no first-class dashboard route exists yet. |

## Frontend Contract Seam

`apps/web/src/lib/phase5-contracts.ts` defines:

- Phase 5 envelope and pagination metadata shapes;
- agent, run, approval, manual-handling, knowledge, and audit contract types;
- dashboard compatibility mappings for agents, runs, and approvals;
- a surface compatibility registry that labels unmapped routes as deferred
  rather than silently inventing UI.

## Deferred Phase 4 Productization Gaps

- Real browser/API integration and authentication strategy.
- Loading, empty, error, retry, and session-expiry states backed by live data.
- First-class manual-handling and knowledge dashboard routes.
- A read API for durable audit records if the operator dashboard needs live
  audit browsing.
- Fixture removal or synthetic/live data switching.
- Operator acceptance testing against a deployed preview.
