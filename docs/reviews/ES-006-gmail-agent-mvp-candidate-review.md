# ES-006 Gmail Agent MVP Candidate Review Record

**Status:** Accepted
**Engineering Specification:** `docs/engineering-specifications/ES-006-gmail-agent-mvp-candidate.md`
**Governing Plan:** `docs/implementation-plans/phase-6-work-order-backlog.md`
**ADR Assessment:** `docs/implementation-plans/phase-6-adr-assessment.md`
**Autonomous Delivery Program:** `docs/implementation-plans/ADP-003-phase-6-gmail-agent-mvp-candidate.md`
**Work Orders:** `docs/work-orders/036-gmail-oauth-scopes-and-connector-boundary.md` through `docs/work-orders/044-controlled-account-verification-and-mvp-candidate-closeout.md`
**Review Owner:** Repository Maintainer
**Review Date:** 2026-07-18
**Review Result:** Accepted
**Implementation Authorization:** Granted for WO-036 through WO-044 under ADP-003

---

## 1. Review Scope

This review covers the accepted Phase 6 Gmail Agent MVP Candidate planning
package after Phase 5 closeout.

Reviewed artifacts:

- ES-006 Gmail Agent MVP Candidate.
- Phase 6 ADR assessment.
- Phase 6 Work Order backlog.
- ADP-003 Phase 6 Gmail Agent MVP Candidate.
- WO-036 through WO-044.
- Phase 5 closeout evidence under WO-035.
- Accepted ADR-002, ADR-003, ADR-004, and ADR-005.
- Connector, Security, Data, Agent Runtime, Observability, and Human Approvals
  architecture references.
- Engineering governance, Definition of Ready, and Definition of Done.
- Official Google Gmail and Drive OAuth scope documentation checked on
  2026-07-18.

## 2. Acceptance Basis

The ES-006 planning package satisfies the readiness requirements for a Phase 6
implementation program, under maintainer acceptance:

- The Gmail Agent objective, intended outcome, owner, target phase, and MVP
  boundary are explicit.
- Scope is limited to the first Gmail Agent MVP candidate consuming the generic
  Phase 5 contracts.
- Work Orders split the implementation into OAuth/scopes, eligibility,
  suppression, low-risk actions, ask-instead-of-guess, drafts, approval gates,
  operational reconciliation, and controlled-account closeout.
- Out-of-scope behavior is explicit, including unrestricted mailbox scans,
  automatic sends, permanent delete, production release authority, live
  external webhooks, multi-user expansion, and new orchestration frameworks.
- The exact candidate Google scopes are identified before implementation:
  `gmail.modify` for Gmail and `drive.file` for approved Drive attachment
  saving.
- `https://mail.google.com/` is explicitly rejected for MVP because it exceeds
  accepted behavior by including immediate permanent delete authority.
- Clinical and PHI suppression is a serial guardrail before knowledge,
  questions, drafts, approvals, low-risk actions, sends, or learning.
- Approval gates preserve exact action/content/source/fact binding,
  edit-then-approve supersession, revalidation, and explicit send outcomes.
- Controlled-account testing is isolated from personal or production mailbox
  use and still requires explicit authorization before live credentials are
  used.

## 3. Definition of Ready Review

| Readiness item | Result | Evidence |
| --- | --- | --- |
| Objective and intended outcome explicit | Pass | ES-006 sections 1 through 3 |
| Acceptance criteria observable and testable | Pass | ES-006 sections 10 and 11; WO-044 closeout |
| Out-of-scope behavior explicit | Pass | ES-006 section 6; ADP-003 section 7; each Work Order section 4 |
| Canonical references linked | Pass | ES-006 section 4; Work Order architecture references |
| Dependencies and sequencing identified | Pass | Phase 6 backlog and ADP-003 dependency waves |
| Security, privacy, trust, scopes, and secrets addressed | Pass | ES-006 sections 7 and 9; WO-036; WO-038; WO-044 |
| Data ownership and integration contracts addressed | Pass | ES-006 section 8; connector and run Work Orders |
| UI scope addressed where relevant | Pass | WO-043 limits dashboard work to contract compatibility unless separately accepted |
| Verification plan defined | Pass | ES-006 section 10; each Work Order section 5 |
| Review owner named | Pass | ES-006 and this review record name the Repository Maintainer |
| Unresolved decisions identified | Pass | Phase-gates unknowns and Work Order stop-and-ask triggers |

## 4. Architecture Review Findings

- **Phase 5 dependency:** Pass. WO-035 closeout records Phase 5 generic
  contracts as completed and merged. ES-006 consumes rather than reopens those
  contracts.
- **Control-plane authority:** Pass. Atlas remains authoritative for agent
  state, run state, approvals, knowledge, `facts_used`, audit, and send
  outcomes.
- **Connector boundary:** Pass. Gmail and Drive behavior must flow through the
  Connector Runtime and credential boundary. Agents do not receive raw provider
  clients or token values.
- **Sequencing:** Pass. OAuth/scope acceptance precedes provider behavior;
  suppression precedes downstream use; drafting precedes approval continuation;
  controlled-account verification closes the candidate.
- **Framework posture:** Pass. No LangChain, LangGraph, Temporal, or new
  orchestration framework is introduced.
- **Single-owner boundary:** Pass. The plan preserves one owner, one reviewer,
  and one governed external product client.

## 5. Security and Privacy Review Findings

- **OAuth scope posture:** Pass for planning. `gmail.modify` is a restricted
  but candidate-minimum scope for the accepted Gmail MVP behaviors, and
  `drive.file` is the candidate Drive scope for attachment saving. WO-036 must
  receive final maintainer acceptance before implementation.
- **Credential handling:** Pass. Token values are excluded from API responses,
  logs, webhooks, audit payloads, fixtures, and committed files.
- **Clinical and PHI suppression:** Pass. WO-038 creates a hard fail-closed
  guardrail and prohibits approval override.
- **Knowledge safety:** Pass. Suppressed sources, secrets, credentials,
  clinical content, and PHI are excluded before knowledge retrieval, question
  creation, fact persistence, or learning.
- **Approval safety:** Pass. Sends require approval, exact binding, and
  pre-continuation revalidation. Indeterminate outcomes require manual
  reconciliation rather than blind retry.
- **Controlled data:** Pass. WO-044 requires deterministic fake-provider
  verification and separate authorization for any controlled live account.

## 6. Work Order Readiness

| Work Order | Readiness result | Notes |
| --- | --- | --- |
| WO-036 Gmail OAuth, Scopes, and Connector Boundary | Ready for acceptance review | Final scope acceptance is the Phase 6 gate. |
| WO-037 Gmail Message Eligibility, Retrieval, and Classification | Ready for acceptance review | Depends on WO-036; excludes downstream behavior. |
| WO-038 Clinical and PHI Suppression Guardrail | Ready for acceptance review | Must land before downstream action/draft/learning paths. |
| WO-039 Low-Risk Mailbox Actions and Attachment Saving | Ready for acceptance review | Parallel-ready after suppression gate; no high-risk actions. |
| WO-040 Ask-Instead-of-Guess and Governed Fact Use | Ready for acceptance review | Parallel-ready after suppression gate; no draft generation. |
| WO-041 Draft Generation and Facts-Used Evidence | Ready for acceptance review | Serial after WO-040. |
| WO-042 Approval Gates, Edit-Then-Approve, and Send Continuation | Ready for acceptance review | Serial after WO-041. |
| WO-043 Gmail Agent Operational Reconciliation | Ready for acceptance review | Contract compatibility only for dashboard/external client. |
| WO-044 Controlled-Account Verification and MVP Candidate Closeout | Ready for acceptance review | Live controlled-account use still requires explicit authorization. |

## 7. Accepted Risks If Maintainer Accepts

The following risks are accepted by the Repository Maintainer with ES-006 and the Work Orders:

- `gmail.modify` is a restricted scope and may require Google verification or
  security assessment before any broader/public production use.
- The MVP may defer Google Drive attachment saving if `drive.file` folder/file
  selection mechanics become disproportionate for the candidate.
- Clinical/PHI suppression thresholds may produce false positives that route
  messages to manual handling. This is preferred over false-negative drafting
  or learning.
- The dashboard remains contract-compatible rather than fully productized
  unless a separate dashboard Work Order expands scope.
- Controlled-account evidence may reveal provider behavior that requires Work
  Order revision or a new ADR before release.

## 8. Required Implementation Guardrails

Implementation under ADP-003 must preserve these guardrails:

- Do not use a personal mailbox or production mailbox.
- Do not use live credentials unless a specific Work Order or maintainer
  authorization grants a controlled-account boundary.
- Do not request `https://mail.google.com/` or any broader Google scope without
  stopping for security review.
- Do not store OAuth token values, full Gmail bodies, secrets, clinical
  content, PHI, or unrestricted attachment copies.
- Do not create drafts, approvals, knowledge questions, low-risk actions,
  sends, or learned facts from suppressed clinical or PHI sources.
- Do not allow human approval to override suppression.
- Do not send, delete, forward, unsubscribe, or share externally without the
  applicable approval gate.
- Do not weaken Phase 5 authorization, audit, webhook minimization, evidence,
  or fail-closed revalidation behavior.

## 9. Technical Review Recommendation

**Accepted.** The Repository Maintainer accepted the ES-006 planning package as the Phase 6 Gmail Agent MVP Candidate execution authority. Acceptance explicitly covers:

1. ES-006.
2. WO-036 through WO-044.
3. ADP-003.
4. Candidate OAuth scopes `gmail.modify` and `drive.file`.
5. No live Gmail or Drive credentials except through separately authorized
   controlled-account testing.

## 10. Current Decision

Repository Maintainer acceptance was recorded on 2026-07-18.

Implementation is authorized for WO-036 through WO-044 under ADP-003. Live Gmail or Drive credentials remain unauthorized except through separately authorized controlled-account testing.
