# ADP-002: Phase 5 Agent Framework and Governance Contracts

**Status:** Accepted - Active for Autonomous Phase 5 Execution
**Program ID:** ADP-002
**Type:** Autonomous Delivery Program
**Owner:** Repository Maintainer
**Created:** 2026-07-18
**Execution Window:** Active as of Repository Maintainer acceptance on 2026-07-18
**Engineering Specification:** `docs/engineering-specifications/ES-005-agent-framework-and-governance-contracts.md`
**Work Order Backlog:** `docs/implementation-plans/phase-5-work-order-backlog.md`

---

## 1. Purpose

Collect the proposed Phase 5 Work Orders into one uninterrupted execution
program after they are accepted.

This ADP does not replace the individual Work Orders. Each Work Order remains
the technical scope authority for its implementation, exclusions, validation
gates, rollback expectations, and stop-and-ask triggers.

## 2. Execution Authority

Execution authority is granted by Repository Maintainer acceptance on
2026-07-18.

The Repository Maintainer accepted ES-005, accepted WO-027 through WO-035, and
explicitly authorized ADP-002 execution. The assistant may proceed without
voluntary pauses through dependency-ready Phase 5 Work Orders.

That future authority would include implementing, validating, documenting,
committing, pushing, opening governed pull requests, monitoring CI, merging
after required CI passes, updating the local branch, and beginning the next
dependency-ready Work Order.

The authority would remain limited to the Work Orders listed in this ADP. It
would not authorize Gmail provider behavior, live credentials, live external
webhooks, production deployment, architecture changes, or scope outside ES-005.

## 3. Proposed Work Order Set

| Order | Work Order | Current State | ADP Execution Action | Completion Gate |
| ---: | --- | --- | --- | --- |
| 1 | `WO-027: Agent Registry and Runtime Contracts` | Implemented Locally - Pending PR/CI/Merge | Complete governed PR, CI, and merge evidence before closeout | PR merged with registry/runtime contract tests and implementation report |
| 2 | `WO-029: Governed Knowledge Fact Contracts` | Accepted | Can run in parallel with WO-027 and WO-031 after acceptance | PR merged with fact CRUD, revision, confirmation, volatility, authorization, audit, and prohibited-content tests |
| 3 | `WO-031: Approval Decision and Manual-Handling Contracts` | Accepted | Can run in parallel with WO-027 and WO-029 after acceptance | PR merged with approval queue, evidence, decision, edit-then-approve, manual-handling, authorization, and audit tests |
| 4 | `WO-028: Run Lifecycle and Job Intake Contracts` | Accepted | Start after WO-027 schema/API contracts stabilize | PR merged with run lifecycle, queue handoff, idempotency, cancellation, timeout, and audit tests |
| 5 | `WO-030: Knowledge Question and Answer Lifecycle` | Accepted | Start after WO-029 | PR merged with question, answer, validation, fact-update, webhook enqueue, and audit tests |
| 6 | `WO-033: Webhook and Audit Event Contract Expansion` | Accepted | Start after event producers from WO-029 through WO-031 exist | PR merged with event schemas, minimized payloads, fake webhook delivery, and audit contract tests |
| 7 | `WO-034: Phase 5 Dashboard Contract Compatibility Pass` | Accepted | Can run after stable API schemas from WO-027, WO-028, WO-029, and WO-031 | PR merged with dashboard contract alignment evidence and no full Phase 4 release claim |
| 8 | `WO-032: Facts-Used Evidence and Revalidation Contracts` | Accepted | Start after WO-029 and WO-031 | PR merged with exact fact revision binding, manifest compatibility, fail-closed revalidation, and audit tests |
| 9 | `WO-035: Phase 5 Contract Integration Verification and Closeout` | Accepted | Final serial closeout | PR merged with synthetic integration smoke, security/privacy negatives, closeout report, and Phase 6 entry criteria |

## 4. Dependency Sequence

```text
ES-005 accepted + WO-027 through WO-035 accepted
  -> Wave 1 parallel lanes: WO-027, WO-029, WO-031
    -> Wave 2 dependent lanes: WO-028, WO-030, WO-033, WO-034
      -> Wave 3: WO-032
        -> Wave 4: WO-035 closeout
```

## 5. Parallel Execution Notes

| Lane | Work Orders | Parallel-safe conditions |
| --- | --- | --- |
| Agent runtime lane | WO-027, then WO-028 | Safe if it owns agent/run modules, migrations, and tests without changing knowledge or approval semantics |
| Knowledge lane | WO-029, then WO-030 | Safe if it owns knowledge services/routes/models and coordinates shared schema helpers before merging |
| Approval lane | WO-031, then WO-032 | Safe if it owns approval/manual-handling contracts and waits for WO-029 before facts-used binding |
| Webhook/audit lane | WO-033 | Safe after event producers exist and it only uses the existing fake delivery foundation |
| Dashboard compatibility lane | WO-034 | Safe after API schemas stabilize and it avoids claiming Phase 4 productization complete |

Parallel agents must not modify the same migration head, route module, or
contract helper without rebasing and reconciling before PR review.

## 6. Stop-and-Ask Triggers

Stop and request Repository Maintainer direction before proceeding if any of
the following occurs:

- ES-005 or a required Work Order is not accepted;
- required CI fails and the failure is not a narrow, in-scope defect fix;
- a reviewer requests a scope, product, security, or architecture decision;
- implementation requires live infrastructure, live provider calls, live
  external webhooks, or real credentials;
- a new ADR, Engineering Specification, Work Order, or architecture authority
  is required;
- the work would add Gmail-specific behavior instead of generic Phase 5
  contracts;
- the work would weaken authentication, authorization, audit, redaction,
  approval evidence, or fail-closed behavior;
- a listed Work Order's own stop-and-ask trigger applies.

## 7. Explicit Exclusions

This ADP does not authorize:

- Phase 6 Gmail agent implementation;
- Gmail OAuth, Gmail API calls, Gmail drafting, Gmail sending, or Gmail history
  learning;
- live webhook delivery or receiver implementation;
- production deployment or hosted resource provisioning;
- multi-user, RBAC, multi-tenant, delegation, quorum, multiple reviewers, or
  multiple external product clients;
- adding LangChain, LangGraph, Temporal, or another framework;
- broad refactoring unrelated to Phase 5 Work Orders.

## 8. Evidence and Reporting

Each Work Order completed under ADP-002 must leave evidence in the repository:

- implementation or closeout report under `docs/reviews/`;
- Work Order status and review-record links kept current;
- local validation command results summarized in the PR;
- GitHub CI result available from the merged PR;
- residual risk or deferred scope recorded when relevant.

## 9. Completion Definition

ADP-002 is complete when:

- WO-027 through WO-035 are implemented, validated, reviewed, and merged;
- Phase 5 closeout evidence is complete;
- the generic contracts remain Gmail-neutral;
- no unresolved ADP stop-and-ask condition remains;
- Phase 6 entry criteria are explicit.

After completion, Gmail-specific MVP candidate work must proceed under ES-006,
accepted Gmail Work Orders, and a successor ADP.
