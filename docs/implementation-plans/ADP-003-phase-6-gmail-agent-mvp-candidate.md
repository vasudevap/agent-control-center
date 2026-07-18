# ADP-003: Phase 6 Gmail Agent MVP Candidate

**Status:** Accepted - Phase 6 Execution Authorized
**Program ID:** ADP-003
**Type:** Autonomous Delivery Program
**Owner:** Repository Maintainer
**Created:** 2026-07-18
**Execution Window:** Active as of Repository Maintainer acceptance on 2026-07-18
**Engineering Specification:** `docs/engineering-specifications/ES-006-gmail-agent-mvp-candidate.md`
**Work Order Backlog:** `docs/implementation-plans/phase-6-work-order-backlog.md`

---

## 1. Purpose

Collect the accepted Phase 6 Gmail Agent MVP Candidate Work Orders into one
sequenced execution program.

This ADP does not replace the individual Work Orders. Each Work Order remains
the technical scope authority for its implementation, exclusions, validation
gates, rollback expectations, and stop-and-ask triggers.

## 2. Execution Authority

Execution authority is granted by Repository Maintainer acceptance on 2026-07-18.

The Repository Maintainer accepted ES-006, accepted WO-036 through WO-044,
accepted the candidate Google OAuth scopes, and explicitly authorized ADP-003
execution.

That authority includes implementing, validating,
documenting, committing, pushing, opening governed pull requests, monitoring
CI, merging after required CI passes, updating the local branch, and beginning
the next dependency-ready Work Order.

The authority remains limited to the Work Orders listed in this ADP. It
does not authorize use of a personal mailbox, production mailbox, unbounded
live Gmail data, live external webhook receivers, production deployment,
architecture changes, or scope outside ES-006.

## 3. Accepted Work Order Set

| Order | Work Order | Current State | ADP Execution Action | Completion Gate |
| ---: | --- | --- | --- | --- |
| 1 | `WO-036: Gmail OAuth, Scopes, and Connector Boundary` | Completed - Merged | Complete | PR merged with exact scopes, fake providers, credential-boundary tests, health/revoke behavior, and audit evidence |
| 2 | `WO-037: Gmail Message Eligibility, Retrieval, and Classification` | Completed - Merged | Complete | PR merged with eligibility retrieval, minimized metadata/content handling, schema validation, uncertainty behavior, and no downstream drafting |
| 3 | `WO-038: Clinical and PHI Suppression Guardrail` | Completed - Merged | Complete | PR merged with fail-closed suppression tests proving no draft, approval, question, action, or learned fact from suppressed sources |
| 4 | `WO-039: Low-Risk Mailbox Actions and Attachment Saving` | Implemented - Pending PR Review | Complete PR review and CI gate | PR merged with idempotent label/archive/Drive-save fake-provider operations and audit/retry evidence |
| 5 | `WO-040: Ask-Instead-of-Guess and Governed Fact Use` | Accepted | Begin after WO-038 completion gate | PR merged with missing/stale fact question behavior, answer validation, fact revisions, and prohibited-source exclusion |
| 6 | `WO-041: Draft Generation and Facts-Used Evidence` | Accepted | Begin after WO-040 completion gate | PR merged with draft generation gates, Gmail draft fake-provider creation, exact `facts_used`, and no automatic send |
| 7 | `WO-042: Approval Gates, Edit-Then-Approve, and Send Continuation` | Accepted | Begin after WO-041 completion gate | PR merged with approval creation, revalidation, edit supersession, send continuation, and explicit send outcomes |
| 8 | `WO-043: Gmail Agent Operational Reconciliation` | Accepted | Begin after WO-039, WO-040, and WO-042 completion gates | PR merged with Gmail agent registration, run status, webhook/audit events, and dashboard/external-client contract compatibility |
| 9 | `WO-044: Controlled-Account Verification and MVP Candidate Closeout` | Accepted | Begin after WO-036 through WO-043 completion gates | PR merged with fake-provider E2E evidence, authorized controlled-account evidence if allowed, residual risks, and MVP candidate checklist |

## 4. Dependency Sequence

```text
ES-006 accepted + WO-036 through WO-044 accepted
  -> Wave 1: WO-036 OAuth and connector boundary
    -> Wave 2: WO-037 eligibility/classification
      -> Wave 3: WO-038 suppression guardrail
        -> Wave 4 parallel lanes: WO-039 low-risk actions, WO-040 ask-instead-of-guess
          -> Wave 5: WO-041 draft generation and facts-used evidence
            -> Wave 6: WO-042 approval gates and send continuation
              -> Wave 7: WO-043 operational reconciliation
                -> Wave 8: WO-044 verification and closeout
```

## 5. Parallel Execution Notes

| Lane | Work Orders | Parallel-safe conditions |
| --- | --- | --- |
| Connector lane | WO-036, then provider fake refinements needed by WO-039 and WO-042 | Safe if it owns connector interfaces, OAuth lifecycle, credential references, and fake clients without implementing agent behavior early |
| Message safety lane | WO-037, then WO-038 | Mostly serial because suppression must become a hard gate before downstream behavior |
| Action lane | WO-039 | Safe after WO-038 if it only performs low-risk side effects and does not add send behavior |
| Knowledge lane | WO-040 | Safe after WO-038 if it consumes existing Phase 5 knowledge contracts and avoids draft creation |
| Draft/approval lane | WO-041, then WO-042 | Serial because approval evidence and send continuation depend on exact draft and `facts_used` identities |
| Operations lane | WO-043 | Safe after action/approval events stabilize and it avoids broad dashboard productization |
| Verification lane | WO-044 | Serial closeout |

Parallel agents must not modify the same migration head, route module, connector
interface, provider fake, or event schema without rebasing and reconciling
before PR review.

## 6. Stop-and-Ask Triggers

Stop and request Repository Maintainer direction before proceeding if any of
the following occurs:

- ES-006 or a required Work Order is not accepted;
- exact Google OAuth scopes are not accepted;
- required CI fails and the failure is not a narrow, in-scope defect fix;
- a reviewer requests a scope, product, security, or architecture decision;
- implementation requires live infrastructure, a personal mailbox, a production
  mailbox, live external webhooks, or real credentials outside the accepted
  controlled-account boundary;
- provider API behavior requires broader scopes or changed Gmail behavior;
- implementation would store full message bodies, OAuth token values, secrets,
  clinical content, PHI, or unrestricted attachment copies;
- implementation would draft, ask, approve, learn from, act on, or send from a
  suppressed clinical or PHI source;
- the work would weaken authentication, authorization, audit, redaction,
  approval evidence, webhook minimization, or fail-closed behavior;
- a new ADR, Engineering Specification, Work Order, or architecture authority
  is required.

## 7. Explicit Exclusions

This ADP does not authorize:

- use of the owner's personal Gmail mailbox;
- production release or hosted infrastructure provisioning;
- unrestricted mailbox scans or full mailbox replication;
- permanent delete, automatic send, automatic forward, automatic unsubscribe,
  or external sharing without approval;
- live external webhook delivery or receiver implementation;
- multi-user, RBAC, multi-tenant, delegation, quorum, multiple reviewers, or
  multiple external product clients;
- adding LangChain, LangGraph, Temporal, or another framework;
- broad dashboard productization beyond explicit contract compatibility;
- Gmail-specific changes to generic Phase 5 contracts unless a later accepted
  Work Order and ADR permit them.

## 8. Evidence and Reporting

Each Work Order completed under ADP-003 must leave evidence in the repository:

- implementation or closeout report under `docs/reviews/`;
- Work Order status and review-record links kept current;
- local validation command results summarized in the PR;
- GitHub CI result available from the merged PR;
- OAuth scope, credential, redaction, suppression, approval, and audit evidence
  where relevant;
- residual risk or deferred scope recorded when relevant.

## 9. Completion Definition

ADP-003 is complete when:

- WO-036 through WO-044 are implemented, validated, reviewed, and merged;
- Gmail behavior consumes the generic Phase 5 contracts without bypassing them;
- controlled data evidence proves the MVP candidate end to end;
- no unresolved credential, privacy, safety, approval, audit, provider, or CI
  blocker remains;
- the MVP candidate closeout report explicitly states whether the Gmail Agent
  is ready for a release decision.
