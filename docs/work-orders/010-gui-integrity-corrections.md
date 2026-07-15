# Work Order 010: GUI Integrity Corrections (Phase 1)

**Status:** Proposed - Pending Review
**Work Order ID:** GUI-INTEGRITY-010
**Type:** Frontend-only correction, no backend, API, persistence, or authentication changes
**Depends on:** [Work Order 006 - Agents Inventory](006-agents-inventory.md), [Work Order 007 - Agent Details](007-agent-details.md), [Work Order 009 - Human Approvals Frontend Experience](009-human-approvals-frontend-experience.md)
**Governing product baseline:** [Human Approvals Functional Specification](../specifications/human-approvals-functional-specification.md), [Atlas Design Principles](../design/01-design-principles.md), [Atlas Design System](../design/07-design-system.md)
**Requested by:** Project owner, following an independent GUI and visual-design review conducted on 2026-07-14
**Reviewer:** Not yet assigned

---

## 1. Purpose of this document

This document proposes Phase 1 of a GUI correction effort and requests review before any implementation begins. Per `AGENTS.md` ("Architecture First") and `.claude/CLAUDE.md` ("Claude must not begin implementation without an approved Work Order or Engineering Specification that meets the Definition of Ready"), no code in this repository may change until this Work Order is reviewed and approved.

This document only proposes scope. It does not authorize implementation, and no application code has been modified as part of writing it.

---

## 2. Background and context for the reviewer

On 2026-07-14 an independent enterprise GUI and visual-design review was conducted against the live Atlas application (`/`, `/agents`, `/agents/agent-invoice-reconcile`, `/approvals`, `/approvals/apr-2026-001`), the full canonical design documentation under `docs/design/`, the product and architecture specifications, and the Human Approvals work order and review history. The review found the token system, application shell, typography pairing, and dark theme to be a strong foundation, but identified several defects that undermine the product's core brand promise ("trust through evidence") because the interface currently contradicts itself across screens. The reviewer's full findings are summarized in this conversation; they have not yet been persisted as a separate `docs/reviews/` artifact.

The most load-bearing findings, in order of severity, were:

1. The Overview dashboard offers unlabeled, one-click Approve/Reject buttons on a $4,220 payment approval card, with no confirmation, no reason capture, and no prototype disclosure. This contradicts the approved Human Approvals Functional Specification (HA-FR-020, HA-FR-021) and the WO-009 truthfulness guardrails, which require every simulated decision to be deliberate, labeled, and routed through the canonical approval detail experience.
2. Overview, the Agents inventory, and the Approvals queue each currently describe a different, non-overlapping set of fictional agents. As a direct consequence, the Critical-risk approval's "Agent" link resolves to `/agents/agent-beta`, which does not exist in the real inventory and renders a raw, unstyled 404 inside the application shell. The Agent Details "Human Approvals" tab has deep-link conditions (`agent.id === "agent-beta"`, `agent.id === "agent-gamma"`) that can never be true against the real inventory, so they are dead code.
3. Approval fixtures use fixed calendar dates from July 2026. As real time has passed, two queue rows now display a red "Expired" timestamp while still carrying a `Pending` state badge with `Approve` enabled on the detail page, directly contradicting the approved state model (approval detail requirements, expired approvals must be read-only).
4. The Approvals functional specification defines exactly five approval states (`Pending`, `Approved`, `Rejected`, `Expired`, `Cancelled`) and requires facets such as review progress to remain orthogonal to state rather than forming compound labels. The current implementation renders `Blocked` and `Clarification requested` as if they were approval states, which both the specification and this review flag as a compliance gap.
5. The approval detail page header reads only "Approval detail" with no approval identifier or proposed-action title, which the specification requires (approval detail header requirements).
6. Reason capture for `Approve` is optional at every risk level in the current implementation. The approved functional specification requires explanatory free text for High and Critical risk approvals. This is a divergence between WO-009 as delivered and the specification it was supposed to implement, not a deliberate product decision.
7. Two minor visual defects: the "Simulated decision" card's tinted header bleeds past its own rounded corners in both themes, and the blue "Frontend prototype" disclosure uses a warning-triangle icon inside an informational surface.

Separately, the repository's current git state already has an in-progress, uncommitted revision under WO-009 (its review record states: "a bounded presentation revision began to improve expiry/SLA visibility and detail-page visual consistency... Its automated checks and manual evidence must be refreshed before this record can return to pull-request review"). That in-progress revision already resolves the breadcrumb-versus-return-action question referenced in the design review (it removed breadcrumbs in favor of the `PageHeader` return-action pattern and added the governing rule to `docs/design/07-design-system.md`). This Work Order treats that resolution as decided and does not revisit it. It does, however, propose finishing what that revision started (items 3 and 5 above extend it directly) and extending the change into files outside WO-009's original file-scope restriction (Overview, Agents, navigation), which is why a new Work Order rather than a further WO-009 amendment is being proposed.

---

## 3. Objective

Correct the integrity and consistency defects above before any visual refinement work begins, so that every screen in Atlas describes the same fictional operating reality and every simulated decision is deliberate, labeled, and evidence-gated in the way the approved specification already requires.

---

## 4. Proposed scope

### 4.1 Overview decision safety

Remove the one-click Approve/Reject buttons from the Overview "Pending Approvals" card. Replace them with a "Review" link that opens the canonical `/approvals/[id]` detail route, where the existing evidence gate, reason capture, and confirmation dialog already apply. Add the same "Frontend prototype" disclosure banner already used on Approvals screens to Overview and to Agent Detail, which currently have none.

### 4.2 Fixture unification

- Overview's Fleet Health and Active Runs sections would read from the same six agents already defined in `apps/web/src/app/(shell)/agents/agent-data.ts` (Invoice Reconciliation Agent, Calendar Briefing Agent, Connector Health Sentinel, Policy Digest Agent, Recruiting Triage Agent, Support Draft Agent), instead of seven different, unrelated agent names invented separately in `features/overview/data/mock-data.ts`.
- Overview's Total/Running/Healthy Agent metrics would be computed from that same six-agent array instead of a hardcoded, unsupported "42."
- Overview's Pending Approvals card would become a summarized projection of the real approval queue in `apps/web/src/app/(shell)/approvals/approval-data.ts`, rather than a separately authored, disconnected fixture list, so the two can no longer disagree.
- The approval fixtures' placeholder agent references (`agent-alpha`, `agent-beta`, `agent-gamma`) would be remapped to the real canonical agent ids their narrative descriptions already match by domain: "Alpha Support Agent" to Support Draft Agent, "Beta Policy Agent" to Policy Digest Agent, "Gamma Connector Agent" to Connector Health Sentinel. This is expected to resolve the `/agents/agent-beta` 404 and the dead deep-link conditions in Agent Detail as a direct consequence, without special-casing.
- Sidebar `Approvals` and `Alerts` navigation badges would become derived counts (queue length, alert count) instead of the currently hardcoded `3` and `2`.

### 4.3 Expiry as the authoritative signal

Approval fixture timestamps would switch from fixed calendar dates to offsets computed relative to load time, so queue urgency states (`Nearing expiry`, `Expiry imminent`, `Expired`) remain correct regardless of when the application is viewed, rather than drifting stale as real time passes. Expired records would lose their decision controls and be excluded from the actionable queue count, and the "N require expiry attention" summary would count correctly.

### 4.4 Approval detail header identity

The header would show the approval identifier and proposed-action title, in addition to the state and risk chips and return action already present, per the approved header requirements.

### 4.5 Canonical risk and state model

One shared risk-badge mapping would be used by both Overview and Approvals (they currently disagree: Overview treats "High" as red while Approvals treats "Critical" as red and "High" as amber). `Blocked` and `Clarification requested` would stop being rendered as approval states and would instead appear as a separate "review progress" facet chip alongside the underlying `Pending` state, matching the state model in the functional specification.

### 4.6 Decision safeguards

`Approve` would require a reason for High and Critical risk approvals, matching the functional specification and correcting the unintentional divergence in the WO-009 implementation. The confirmation dialog would restate target, consequence, risk, and expiry, not only the action text.

### 4.7 Visual defect fixes

Fix the Simulated Decision card's tinted header overflowing its rounded corners. Replace the warning-triangle icon in the informational "Frontend prototype" notice with an icon that matches its informational surface.

### 4.8 Explicitly out of scope for this Work Order

Queue table column rebuild, expanded filters and saved sorts, History reviewer/decision columns, mobile decision-panel reordering, metric-card and detail-header component consolidation across the whole product, replacement of Agent Detail's invented metrics, and all longer-term design-system documentation work identified in the review. These are proposed as later, separately reviewed phases and are not authorized by this Work Order.

---

## 5. Proposed file scope

No files outside this new Work Order document have been modified. If approved, implementation would touch:

**Modify:**
`apps/web/src/features/overview/components/pending-approvals-section.tsx`, `fleet-health-section.tsx`, `active-runs-section.tsx`, `metrics-row.tsx`, `overview-dashboard.tsx`; `apps/web/src/features/overview/data/mock-data.ts`; `apps/web/src/features/overview/types/overview.types.ts`; `apps/web/src/app/(shell)/approvals/approval-data.ts`, `approval-presentation.ts`, `approval-prototype-controller.ts`, `approvals-workspace.tsx`; `apps/web/src/app/(shell)/approvals/[approvalId]/approval-detail-workspace.tsx`; `apps/web/src/app/(shell)/agents/[agentId]/agent-detail-workspace.tsx`; `apps/web/src/components/layout/nav-items.ts`, `sidebar.tsx`, `mobile-nav-drawer.tsx`; `apps/web/src/components/ui/card.tsx` or a scoped instance-level fix; the existing test files covering approvals behavior (`approvals-workspace.test.tsx`, `approval-detail-workspace.test.tsx`, `approval-presentation.test.ts`).

**Add:**
One shared risk and state badge-variant module consumed by both Overview and Approvals.

**Documentation to update alongside code, if approved:**
`docs/work-orders/009-human-approvals-frontend-experience.md` (correct the approve-reason scope item; note that this Work Order amends its file-scope restriction to include Overview, Agents, and navigation files); `docs/specifications/human-approvals-functional-specification.md` decision log, if the reason-requirement correction needs an explicit record; `docs/design/07-design-system.md` (document the canonical risk and state badge rule).

No other files are proposed to be in scope without a further Work Order amendment.

---

## 6. Definition of Ready self-assessment

| Item | Status |
| --- | --- |
| Objective, intended outcome, owner, and approved scope are explicit | Addressed in Sections 3 and 4 |
| Acceptance criteria are observable and testable | Addressed in Section 7 |
| Out-of-scope behavior is explicit | Addressed in Section 4.8 |
| Canonical architecture, ADR, product, design, and DDR references are linked | Addressed via Functional Specification, Design Principles, and Design System references above |
| Dependencies, prerequisites, sequencing, and external constraints are identified | Addressed in Section 2 and the header dependency list |
| Security, privacy, trust-boundary, permission, and secret-handling considerations are addressed | Not applicable; frontend-only, no new data sources, connectors, or credentials introduced |
| Data ownership, migrations, retention, and integration contracts are addressed | Not applicable; local fixture data only, no persistence |
| UI flows, loading/empty/error/disabled states, accessibility, themes, and responsive behavior are specified where relevant | Existing states are preserved; no new states introduced by this Work Order |
| The verification plan identifies commands, tests, manual reviews, and required evidence | Addressed in Section 7 |
| A review owner is named | Not yet; awaiting assignment |
| Unresolved decisions are resolved, assigned to an ADR/DDR or follow-up, or explicitly accepted with risk and a revisit trigger | The WO-009 approve-reason divergence is resolved in favor of the approved functional specification (Section 4.6); no other unresolved decisions identified |

---

## 7. Definition of Done, if approved

- `npm run lint`, `npm run typecheck`, `npm test`, and `npm run build` all pass.
- Existing automated tests are updated to match corrected behavior; no test is deleted solely to make a failure disappear.
- Manual verification in both light and dark themes at desktop width confirms: Overview's approvals card links to detail rather than deciding; the agent link on `apr-2026-001` no longer 404s; expired queue records are read-only; both visual defects are fixed.
- Documentation listed in Section 5 is updated to match the implemented behavior.
- Work is committed directly to the current branch (`codex/wo-009-human-approvals-frontend`), per the project owner's direction; no new branch or pull request is opened for this phase.

---

## 8. Risks and controls

| Risk | Control |
| --- | --- |
| Remapping approval fixture agent ids could silently change which agent a historical or in-progress approval narrative refers to | Remap is a like-for-like domain match (support to support, policy to policy, connector to connector) documented in Section 4.2 for reviewer verification |
| Removing `Blocked` and `Clarification requested` as states could break existing test assertions or component logic that switches on those string values | All call sites identified in file scope (Section 5); tests updated as part of this Work Order rather than left failing |
| Relative-time fixture generation could make manual QA screenshots harder to reproduce exactly | Offsets will be documented in code comments (for example, "expires in 22 hours from load") so behavior is predictable even though absolute timestamps vary |
| Scope could creep into Phase 2/3 items during implementation | Section 4.8 is explicit; any item not listed in Section 4 requires a further Work Order amendment before implementation |

---

## 9. Dependencies and sequencing

This is proposed as Phase 1 of a three-phase effort. Phase 2 (near-term refinements: queue table rebuild, filters, History columns, mobile ordering, component consolidation) and Phase 3 (longer-term design-system documentation) are not proposed here and would each require their own Work Order, reviewed and approved separately, once Phase 1 is complete and validated.

---

## 10. Authorization statement

This document is a proposal only. It does not authorize implementation. Implementation may begin only after a named reviewer records an approval decision in Section 11.

---

## 11. Approval record

| Role | Decision | Name | Date |
| --- | --- | --- | --- |
| Reviewer | Pending | | |
