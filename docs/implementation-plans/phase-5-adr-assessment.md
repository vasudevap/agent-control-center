# Phase 5 ADR Assessment

**Status:** Proposed - Governance Review Required
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Scope:** Determine whether Phase 5 Agent Framework and Governance Contracts
requires new ADR authority before implementation.
**Related ES:** `docs/engineering-specifications/ES-005-agent-framework-and-governance-contracts.md`

---

## 1. Assessment Result

Existing accepted ADRs appear sufficient for the proposed Phase 5 generic
contract implementation, provided Phase 5 stays inside ES-005 boundaries.

No new ADR is required before drafting or accepting the Phase 5 Work Orders.
A new ADR is required if implementation attempts to change any architecture
decision listed in Section 4.

## 2. Accepted ADR Coverage

| Area | Existing authority | Coverage |
| --- | --- | --- |
| Approval decision integrity | ADR-002 | Canonical approval lifecycle, exact action binding, continuation, evidence, expiry, audit, and fail-closed behavior |
| External approval channel | ADR-003 | Internal and external decision channels, external client acting for the one human reviewer, edit-then-approve requirement |
| External product client contract | ADR-004 | Generic external product client boundary, authenticated API, webhooks, manual-handling event, one-client and one-reviewer limits |
| Governed knowledge and ask-instead-of-guess | ADR-005 | Fact CRUD, confirmation, volatility, questions, answers, `facts_used`, revalidation, and Gmail sequencing |
| Backend foundation | ES-004 plus Phase 3 closeout | FastAPI, PostgreSQL, auth/session, external-client identity, authorization, API contracts, queue, scheduler, webhooks, audit, and observability foundations |

## 3. Phase 5 Work That Can Proceed Under Existing ADRs

The following Phase 5 areas can proceed after ES-005 and their Work Orders are
accepted:

- generic agent registry and runtime contract foundations;
- generic run lifecycle and queue-backed job-intake contracts;
- governed knowledge fact CRUD, confirmation, volatility, and revision
  contracts;
- knowledge question and answer lifecycle contracts;
- generic approval queue, evidence, approve/reject, and edit-then-approve
  contracts;
- manual-handling records and minimized manual-handling webhook events;
- `facts_used` evidence binding and revalidation contracts;
- synthetic-data contract and integration tests.

## 4. Decisions That Would Require a New ADR

A new ADR is required before implementation if Phase 5 introduces or changes:

| Trigger | Why it requires ADR review |
| --- | --- |
| More than one human reviewer, delegation, quorum, roles, or RBAC | Violates the accepted single-reviewer boundary |
| More than one external product client or client marketplace behavior | Expands ADR-004 beyond its accepted scope |
| Multi-tenant or multi-user operation | Changes identity, authorization, tenancy, data, and audit architecture |
| Gmail-specific provider behavior inside Phase 5 | Breaks the Phase 5 generic-contract and Phase 6 Gmail sequencing |
| Live credentials, live provider calls, or production effects | Requires explicit security, privacy, deployment, and release authority |
| A workflow framework such as LangGraph or Temporal | Changes runtime/framework architecture under the repository framework policy |
| A non-PostgreSQL system of record | Changes accepted persistence architecture |
| Webhooks as authorization or proof of reconciliation | Contradicts ADR-003 and ADR-004 |
| Storing secrets, credentials, full email bodies, PHI, or clinical content in knowledge | Contradicts ADR-005 and security architecture |

## 5. Open Design Details for Work Orders

The following are implementation-level design details for Work Orders, not ADR
blockers if they remain inside the accepted boundaries:

- exact route names and schema field names;
- migration names and table/index details;
- allowed filter and sort fields;
- idempotency-record table shape;
- stale volatile fact threshold defaults for synthetic testing;
- webhook event names and minimized payload fields;
- audit event action names;
- contract-test fixture names and factories.

## 6. Recommendation

Accept ES-005 first, then review and accept the Phase 5 Work Orders. ADP-002
should become executable only after the accepted Work Orders preserve the
boundaries recorded in this assessment.
