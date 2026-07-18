# Phase 6 ADR Assessment

**Status:** Accepted - No New ADR Required
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Related Engineering Specification:** `docs/engineering-specifications/ES-006-gmail-agent-mvp-candidate.md`
**Related Phase:** Phase 6 - Gmail Agent

---

## 1. Purpose

Assess whether Phase 6 Gmail Agent MVP Candidate planning requires a new
Architecture Decision Record before implementation Work Orders proceed.

This assessment records the accepted architecture decision coverage for ES-006.
Implementation authority is granted by ES-006, WO-036 through WO-044, and
ADP-003, not by this assessment alone.

## 2. Decision Coverage

| Concern | Existing authority | Assessment |
| --- | --- | --- |
| Human approval integrity and continuation | `ADR-002` | Covered. Gmail send continuation must bind to exact action, content, evidence, actor, and continuation state. |
| External approval decision channel | `ADR-003` | Covered. External webhooks remain notifications only and do not authorize Gmail actions. |
| External product client contract | `ADR-004` | Covered. One governed external product client may reconcile approvals, status, held items, and outcomes through Atlas APIs. |
| Governed knowledge and ask-instead-of-guess | `ADR-005` | Covered. Phase 6 consumes the Phase 5 knowledge, question, answer, `facts_used`, and revalidation contracts. |
| Connector framework | `docs/architecture/10-connector-framework.md` | Covered at architecture level. Phase 6 Work Orders must implement the Gmail and Drive connector specifics through this boundary. |
| Clinical and PHI suppression ordering | `ADR-005`, `docs/architecture/07-security-architecture.md`, `docs/specifications/product-requirements.md` | Covered. Suppression must occur before knowledge retrieval, question creation, draft generation, approval creation, or learning. |
| PostgreSQL runtime system of record | `docs/architecture/08-data-architecture.md`, `ES-004`, `ES-005` | Covered. Gmail remains provider source for mailbox objects; Atlas stores references and governed state. |
| Agent runtime and run lifecycle | `docs/architecture/09-agent-runtime.md`, `ES-005` | Covered. Phase 6 must register and execute Gmail behavior through generic runtime contracts. |
| OAuth credential boundary | `docs/architecture/10-connector-framework.md`, `ES-006` | Covered at architecture level. WO-036 must fix exact scopes and implementation details before code. |
| Controlled-account testing | `ES-006`, governance controls | Covered as a Work Order-level execution boundary. Live or controlled credentials still require explicit maintainer authorization. |

## 3. Scope Decision From Official Provider Docs

The current Gmail scope taxonomy was checked against official Google developer
documentation on 2026-07-18:

- Gmail scope guide:
  `https://developers.google.com/workspace/gmail/api/auth/scopes`
- Gmail OAuth scope index:
  `https://developers.google.com/identity/protocols/oauth2/scopes`
- Drive scope guide:
  `https://developers.google.com/workspace/drive/api/guides/api-specific-auth`

The Phase 6 candidate scope posture is:

| Scope | Provider classification | Planning posture |
| --- | --- | --- |
| `https://www.googleapis.com/auth/gmail.modify` | Restricted | Candidate Gmail MVP scope because labels, archive, selected message reads, draft creation, and approved send continuation require message read/modify behavior. It does not permit immediate permanent deletion that bypasses trash. |
| `https://www.googleapis.com/auth/drive.file` | Non-sensitive | Candidate Drive scope for approved attachment saving into app-created or user-shared Drive files/folders. |
| `https://mail.google.com/` | Restricted | Rejected for MVP because it includes immediate permanent delete authority and exceeds accepted behavior. |
| `https://www.googleapis.com/auth/gmail.readonly` | Restricted | Deferred/rejected as redundant when `gmail.modify` is accepted; insufficient for labels, archive, drafts, and send continuation. |
| `https://www.googleapis.com/auth/gmail.metadata` | Restricted | Insufficient for draft-worthy content retrieval. May inform future two-step designs, but not accepted for MVP by itself. |
| `https://www.googleapis.com/auth/gmail.compose` | Restricted | Insufficient by itself for message eligibility and label/archive behavior; redundant if `gmail.modify` is accepted. |
| `https://www.googleapis.com/auth/gmail.send` | Sensitive | Insufficient by itself for message eligibility, labels, archive, or drafts; redundant if `gmail.modify` is accepted. |
| `https://www.googleapis.com/auth/gmail.labels` | Non-sensitive | Allows label management but not message label application; insufficient by itself for MVP actions. |

Final scope acceptance belongs in WO-036 review. If implementation discovers
that a broader scope is required, Phase 6 must stop for security review before
code continues.

## 4. New ADR Requirement Assessment

No new ADR appears required before Phase 6 planning can proceed because the
major architectural decisions are already accepted:

- Atlas remains the control plane and system of record for governed agent
  state, approvals, knowledge, audit, and outcomes.
- Gmail and Drive are accessed only through connector contracts.
- Suppressed clinical or PHI messages remain manual-handling items, not
  approvable actions or learning sources.
- Drafts use governed facts and fail-closed revalidation.
- Human approvals authorize exact Gmail continuations only.
- The MVP remains single-owner, single-reviewer, and single external client.

## 5. ADR Stop Triggers

Create a new proposed ADR before implementation if any Phase 6 Work Order would:

- require a broader Google OAuth scope than WO-036 accepts;
- introduce automatic send, delete, forward, unsubscribe, or external sharing;
- store full Gmail message bodies, OAuth token values, clinical content, PHI,
  or unrestricted attachment copies in Atlas;
- make Gmail or Drive authoritative for Atlas approval, knowledge, or audit
  state;
- require multi-user, RBAC, tenancy, delegation, quorum, multiple reviewers, or
  multiple external product clients;
- introduce LangChain, LangGraph, Temporal, or another orchestration framework;
- require production deployment, live webhook receivers, or persistent hosted
  infrastructure beyond accepted boundaries;
- allow human approval to override clinical or PHI suppression.

## 6. Review Conclusion

Phase 6 can proceed to ES-006 and Work Order review without a new ADR, provided
WO-036 accepts exact Google scopes and every implementation Work Order must
preserve the accepted architecture, security, data, approval, and knowledge
boundaries.
