# Work Order 009: Human Approvals Frontend Experience

**Status:** Implementation Complete - Pending Pull Request
**Work Order ID:** WO-009
**Type:** Frontend prototype
**Implementation Authorization:** Granted
**Governing Engineering Specification:** [ES-003 Human Approvals Frontend Experience](../engineering-specifications/ES-003-human-approvals-frontend-experience.md)
**Product Specification:** [Human Approvals Functional Specification](../specifications/human-approvals-functional-specification.md)
**Architecture Authority:** [Human Approvals Architecture](../architecture/13-human-approvals.md)
**Decision Authority:** [ADR-002 Human Approvals Decision Integrity](../decisions/ADR-002-human-approvals-decision-integrity.md)
**Review Authority:** [ES-003 Review](../reviews/ES-003-human-approvals-frontend-experience-review.md)

---

## 1. Purpose

Replace the current Approvals placeholder with a production-quality, frontend-only Human Approvals prototype. The prototype must let operators review a queue, inspect a single approval, exercise clearly simulated decision and clarification paths, and consult local approval history.

This work delivers interaction and visual evidence only. It must not create a real approval capability or imply that a decision is authorized, audited, persisted, or dispatched.

### 1.1 UX success criteria

The delivered prototype is acceptable only when all of the following outcomes are demonstrated:

- An operator can locate a pending approval in no more than three primary interactions.
- An operator can understand the decision context without leaving the approval-detail experience.
- All approval workflows can be completed using keyboard-only navigation.
- Approval state, urgency, risk, and availability are not communicated by color alone.
- Simulated actions cannot reasonably be interpreted as affecting a real agent, runtime, service, or persisted record.
- Any locally simulated decision remains session-only and is clearly non-persistent.

---

## 2. Objective and User Outcome

An operator can:

- identify the approvals that need attention;
- narrow the queue through search, filters, sorting, and pagination;
- open an approval without losing queue context;
- understand the exact proposed action, risk, policy rationale, evidence, and operational impact before acting;
- perform a locally simulated approve, reject, request-clarification, or indeterminate-outcome flow; and
- review a separate history view.

The experience must read as an enterprise operations surface for governing an AI workforce, not as a consumer AI assistant or workflow builder.

---

## 3. Approved Scope

### 3.1 In scope

- Replace `/approvals` with the canonical approval queue and approval-history experience.
- Add a canonical approval-detail route at `/approvals/[approvalId]`.
- Add local fictional approval fixtures, typed view models, and a frontend-only prototype controller.
- Implement URL-backed queue and history context for view, search, filter, sort, and pagination.
- Implement queue search, filters, filter-summary chips, sort, reset, empty, loading, and error states.
- Implement desktop table and mobile card representations of the same queue content.
- Implement approval detail sections, contextual breadcrumbs, related artifact and agent metadata, decision reason capture, clarification, and an activity timeline.
- Implement simulated approve, reject, request-clarification, and indeterminate-outcome experiences.
- Implement the simulated step-up confirmation interaction required for critical approvals and applicable high-risk approvals.
- Add an accessible reusable dialog primitive aligned with the existing shared component conventions.
- Add discoverable links from the existing Agent Details Human Approvals tab to the new canonical approval-detail route when a local approval record has a stable fixture identifier.
- Add focused automated tests and record the required manual visual and accessibility evidence.

### 3.2 Explicitly out of scope

- APIs, network clients, `fetch`, server actions, backend services, runtime behavior, execution dispatch, or persistence.
- Authentication, authorization, identity, real reviewer eligibility, or real step-up authentication.
- Policy evaluation, policy changes, permissions, connector execution, notifications, SLAs, assignment, ownership changes, escalation, delegation, and bulk decisions.
- Actual audit logging, immutable audit storage, retry infrastructure, reconciliation, or export.
- Run-detail or artifact-detail destination pages that do not already exist.
- Any change to the approved Human Approvals architecture or ADR-002.

### 3.3 Scope guardrails

- Every Queue, Detail, and History surface must visibly say `Frontend prototype` and explain that displayed data and actions are local simulations.
- Any changed status or activity item must visibly use the word `Simulated`.
- A browser refresh must restore fixture state. No browser storage, database, file, or network persistence is permitted.
- The local controller must be the only mutation boundary. UI components may not call a network mechanism or mutate fixture modules directly.
- The prototype must not use language such as `authorized`, `executed`, `recorded in audit`, or `permanently saved` for a local action.
- Related Run and Artifact references whose destinations are not implemented must be visibly unavailable metadata, not misleading links.
- No frontend interaction delivered under this Work Order shall create the expectation that an approval has been executed against a real agent, runtime, service, policy engine, audit system, or persistent record.

---

## 4. Required File Scope

### 4.1 Modify

- `apps/web/src/app/(shell)/approvals/page.tsx`
  - Replace `PlaceholderPage` with the approval queue/history workspace entry point.
- `apps/web/src/app/(shell)/agents/[agentId]/agent-detail-workspace.tsx`
  - Link local Human Approvals entries with stable fixture identifiers to `/approvals/[approvalId]`.
- `apps/web/package.json`
  - Add only the approved accessible dialog dependency, `@radix-ui/react-dialog`, if it is required for the shared dialog primitive.
- The associated package lockfile, only if `package.json` changes.

### 4.2 Create

- `apps/web/src/app/(shell)/approvals/approval-data.ts`
  - Typed, fictional local fixtures covering all required representative queue, history, detail, and alternate states.
- `apps/web/src/app/(shell)/approvals/approval-prototype-controller.ts`
  - The local-only controller and view-state transitions for simulated actions. No network or persistence behavior.
- `apps/web/src/app/(shell)/approvals/approvals-workspace.tsx`
  - The client-side queue/history workspace and URL-synchronized controls.
- `apps/web/src/app/(shell)/approvals/approvals-workspace.test.tsx`
  - Focused queue, filter, state, and disclosure coverage.
- `apps/web/src/app/(shell)/approvals/[approvalId]/page.tsx`
  - Canonical approval-detail route entry point.
- `apps/web/src/app/(shell)/approvals/[approvalId]/approval-detail-workspace.tsx`
  - Detail layout and simulated decision/clarification interactions.
- `apps/web/src/app/(shell)/approvals/[approvalId]/approval-detail-workspace.test.tsx`
  - Focused detail, reason capture, confirmation, unavailable, and indeterminate-state coverage.
- `apps/web/src/components/ui/dialog.tsx`
  - Shared accessible dialog wrapper consistent with existing Atlas UI primitives.
- `apps/web/src/components/ui/dialog.test.tsx`
  - Keyboard, accessible-name, focus, and dismiss behavior coverage for the reusable dialog.

No other files are in scope without an approved Work Order amendment.

---

## 5. Functional Delivery Requirements

### 5.1 Information architecture and navigation

- `/approvals` is the canonical destination for the approval queue.
- Queue and History are sibling views within `/approvals`; the active view is URL-backed.
- `/approvals/[approvalId]` is the canonical detail destination.
- Detail breadcrumbs must represent `Approvals / [Queue or History] / [Approval identifier]`.
- Returning from detail must preserve the originating queue context when it is available in navigation history or the return affordance.
- Existing Agent Details approval entries must deep-link only when their fixture record is represented by the canonical approval data. Otherwise, keep them as non-interactive context.

### 5.2 Queue

The Queue view must include:

- a `Human Approvals` page title, enterprise-operations description, and persistent prototype disclosure;
- a count that distinguishes visible results from the total local fixture set;
- full-text search across approval identifier, agent name, action summary, policy reference, and relevant source labels;
- filters for state, risk, agent, policy, and expiry/urgency;
- sortable columns for priority/urgency, requested time, expiry, risk, and agent;
- a compact active-filter summary with individual removal and `Clear filters`;
- a desktop semantic table with an accessible name and sortable-column semantics;
- an equivalent mobile card list, not a squeezed desktop table;
- URL-backed `view`, search, filter, sort, and page state;
- URL-backed pagination, with a finite local page size even when fixture volume is low;
- clearly distinct loading, recoverable error, no-data, and no-matching-results states;
- row and card activation that opens the canonical detail route; and
- visual prioritization of soon-expiring, critical-risk, and blocked/clarification-needed requests without relying on color alone.

The queue must not present bulk selection, assignment controls, ownership transfer, escalation controls, or decision controls as available functionality.

### 5.3 History

The History view must include:

- its own URL-backed active view state;
- the same search, filter, sort, pagination, reset, loading, error, empty, and responsive behavior patterns as the Queue where applicable;
- terminal and indeterminate example records;
- decision outcome, reason availability, decision time, reviewer placeholder, and correlation/reference context represented as fictional local data; and
- a clear distinction between historical records and currently actionable requests.

### 5.4 Approval detail

The detail view must include, in a scan-friendly hierarchy:

- approval identifier, current state, risk, urgency/expiry, agent, requested time, and a visible prototype disclosure;
- the proposed action and effect, including target, payload summary, and operational impact;
- policy and governance rationale, including human-readable policy reference and why review is required;
- evidence and context with untrusted or external material visually separated from system metadata;
- related agent link when implemented, plus Run and Artifact metadata that is unavailable when no destination exists;
- decision history/activity timeline using explicit `Simulated` labeling after a local interaction;
- an accessible `Approval unavailable` explanation wherever Approve is disabled or unavailable;
- a reason input and validation for reject; a reason input that is optional for approve; and a reason input for clarification;
- decision confirmation dialogs that restate the affected approval and the intended simulated outcome;
- the simulated step-up confirmation for every Critical approval and applicable High-risk approval; and
- an indeterminate-outcome treatment that makes clear the result is unresolved locally and directs the operator to refresh or return to the queue context.

The detail view must not render a real approval as granted, reject an actual request, execute a proposed action, or claim to have written an audit event.

### 5.5 Representative fixtures and controlled alternate states

Local fixtures must cover at least:

- pending approvals at Low, Medium, High, and Critical risk;
- an approval with an approaching expiry;
- a policy/validation-blocked approval where approval is unavailable;
- a clarification-requested approval;
- approved and rejected historical approvals;
- an expired approval;
- an indeterminate execution-outcome record;
- missing or unavailable evidence;
- a long agent name, long policy reference, and long action summary;
- no approvals, filtered-empty, loading, and recoverable error states; and
- a step-up-required example.

Alternate states may be exposed only through a controlled development/test mechanism. Do not provide an operator-facing debug switcher in the product UI.

### 5.6 Reusable dialog primitive

The new shared dialog must:

- have an accessible title and description;
- trap focus while open, restore focus when closed, and support Escape dismissal when dismissal is allowed;
- make its destructive and primary actions unambiguous;
- support the simulated decision-confirmation and step-up flows without duplicating dialog accessibility logic in feature components; and
- follow current Atlas styling, responsive behavior, and motion conventions.

If adding `@radix-ui/react-dialog` is necessary, use the stable package version compatible with the repository's existing Radix dependencies. Do not introduce an unrelated modal framework.

---

## 6. UX and Accessibility Requirements

- Preserve the established Atlas application shell, spacing, typography, color semantics, and shared UI component patterns.
- Use `PageHeader`, `Breadcrumb`, `SearchField`, `Table`, `Badge`, `Button`, `Card`, `EmptyState`, `ErrorState`, `Skeleton`, and the new `Dialog` where each is appropriate. Do not create parallel versions of these primitives.
- Use real labels, headings, buttons, table headers, and links. Icon-only controls require accessible names and tooltips.
- Announce dynamic simulated decision outcomes and validation errors through appropriate live-region behavior.
- Keep keyboard focus predictable through filtering, dialogs, route changes, and state changes.
- Never use color as the sole expression of risk, state, urgency, disabled behavior, or error.
- Support a 320 CSS-pixel viewport without document-level horizontal scrolling.
- At narrow widths, use stacked filter controls and cards; preserve all key identifiers, state, risk, expiry, and action context.
- Ensure long labels, identifiers, policy references, and action summaries wrap or truncate with accessible full values.
- Ensure dialog content remains usable at 200% zoom and with reduced-motion preferences.

---

## 7. Required Tests and Evidence

### 7.1 Automated tests

Add or update tests that demonstrate:

- queue search, multiple filters, sort, reset, and URL-context behavior;
- Queue and History distinctions;
- queue row/card navigation and return context;
- loading, recoverable error, no-data, and filtered-empty states;
- reason validation and simulated approve, reject, and clarification paths;
- step-up confirmation and indeterminate-outcome presentation;
- disabled/unavailable approval explanation;
- dialog focus, keyboard behavior, and accessible name; and
- Agent Details deep-link behavior when a canonical fixture identifier exists.

The implementing engineer must run the project-standard quality checks specified in ES-003: lint, typecheck, unit tests, production build, and the applicable smoke or end-to-end checks. This draft does not authorize running them now.

### 7.2 Manual evidence for review

Attach review evidence showing:

- desktop Queue with active filters and an urgency/risk combination;
- mobile Queue card list;
- History view;
- a rich approval detail including proposed action, policy rationale, evidence, and activity;
- reject reason validation and confirmation;
- simulated step-up confirmation;
- disabled approval explanation;
- indeterminate-outcome state;
- loading, error, empty, and filtered-empty states; and
- keyboard-only dialog use and a narrow viewport with no document-level overflow.

### 7.3 Required closure artifacts

WO-009 cannot be closed until the implementation review contains all of the following artifacts:

- desktop screenshots;
- tablet screenshots;
- mobile screenshots;
- light-theme verification;
- dark-theme verification;
- keyboard-only workflow verification;
- accessibility verification evidence;
- responsive verification evidence;
- automated test evidence;
- pull request link;
- final implementation summary;
- final review record; and
- completed verification checklist.

---

## 8. Definition of Done

- [x] The approved ES-003 requirements are implemented without expanding scope.
- [x] `/approvals` no longer renders the generic placeholder page.
- [x] Queue, History, and canonical detail routes are complete and navigable.
- [x] All operator actions remain visibly simulated, local-only, and non-persistent.
- [x] No frontend interaction creates the expectation that an approval has been executed against a real agent, runtime, service, policy engine, audit system, or persistent record.
- [x] No API, backend, runtime, policy, persistence, auth, or execution behavior has been introduced.
- [x] The shared dialog satisfies its accessibility requirements.
- [x] Existing Agent Details approval entries deep-link only where fixture identity permits.
- [x] Automated tests and required quality checks pass.
- [x] Manual responsive and accessibility evidence is attached to the implementation review.
- [ ] All required closure artifacts in Section 7.3 are attached and complete.
- [x] Documentation, code comments, and UI copy do not overstate prototype behavior.
- [x] The implementation review confirms conformance with the functional specification, architecture, ADR-002, and ES-003.

---

## 9. Risks and Controls

| Risk | Required control |
| --- | --- |
| Prototype behavior is mistaken for real governance | Persistent disclosure, explicit simulated language, no persistence, and no execution claims. |
| Decision UI creates unsafe expectations | Required action context, confirmation, reason capture, unavailable explanation, and simulated step-up. |
| Queue becomes unusable at enterprise scale | Server-independent URL context, predictable filters, sorts, pagination, and responsive representations. |
| Untrusted evidence appears authoritative | Separate external/untrusted material from system metadata with clear labels. |
| Dialog accessibility is inconsistently reimplemented | One shared dialog primitive with focused automated coverage. |
| Scope drifts into backend behavior | File-scope limit, no-network controller rule, and explicit non-goals. |
| Future assignment, escalation, or bulk work is implied as present | Present those concepts only as unavailable future scope; do not add operable controls. |

---

## 10. Dependencies and Sequencing

- ES-003 must remain the controlling frontend specification.
- The Functional Specification, Architecture 13, and ADR-002 remain authoritative for terminology, state semantics, integrity boundaries, and future extensibility.
- This Work Order must be approved before any branch is created or implementation begins.
- Assignment, ownership, escalation, and bulk decisions require a separate approved specification and Work Order.
- Real approval actions require future approved architecture and delivery work for identity, eligibility, step-up authentication, authoritative decisions, audit, and execution outcome reconciliation.

---

## 11. Approval Record

| Role | Decision | Name | Date |
| --- | --- | --- | --- |
| Product owner | Approved | Repository Maintainer | 2026-07-13 |
| UX/design reviewer | Approved | Repository Maintainer | 2026-07-13 |
| Engineering reviewer | Approved | Repository Maintainer | 2026-07-13 |

---

## 12. Authorization Statement

This approved Work Order authorizes only the bounded frontend prototype described in this document. It does not authorize architecture changes, backend behavior, APIs, persistence, authentication, authorization, runtime execution, policy-engine behavior, real audit completion, assignment, escalation, delegation, bulk decisions, or any real approval action. Delivery must follow the repository's documented branch, pull-request, CI, review, and Definition of Done controls.

---

## 13. Implementation Evidence

The implementation evidence is recorded in [WO-009 Human Approvals Frontend Implementation Review](../reviews/WO-009-human-approvals-frontend-implementation-review.md).

Before this Work Order can be closed, the pull request link, final merge review, and completed pull-request controls must be added to that record.
