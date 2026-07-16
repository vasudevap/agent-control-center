# ES-003 Human Approvals Frontend Experience Review

**Status:** Review Complete - Approved After Revision
**Date:** 2026-07-13
**Reviewed Artifact:** `docs/engineering-specifications/ES-003-human-approvals-frontend-experience.md`
**Review Type:** Product, Design, Architecture, Security, Privacy, and Readiness Gate
**Disposition:** Approved for Work Order Drafting; Implementation Not Authorized

---

## 1. Executive Assessment

ES-003 makes the correct engineering decision to deliver a frontend-only Human
Approvals experience before operational platform foundations exist.

The specification is well aligned with the approved Functional Specification,
Architecture Specification, ADR-002, Atlas design principles, and the existing
frontend prototype precedent.

The draft is not yet ready for implementation. Three high-priority findings and
six medium-priority findings must be incorporated before ES-003 can receive
final approval or govern a Work Order.

No application implementation is authorized.

---

## 2. Findings

### ES003-R01 - Step-up authentication UX is missing from the prototype contract

**Priority:** High
**Affected areas:** Decision Prototype, Decision Reasons, Security and Privacy,
Acceptance Criteria

The approved architecture requires step-up authentication for every Critical
approval and specified High-risk actions. ES-003 excludes real authentication,
which is correct, but currently lets the prototype decision flow proceed without
representing the required interruption.

That omission would teach the wrong interaction model and could make later
authentication integration feel like an unexpected regression.

**Required change:**

- Add a simulated step-up boundary to affected decision previews.
- State that operational Atlas requires identity verification before the
  decision can be recorded.
- Do not render password, passcode, biometric, or identity-provider fields.
- Provide an explicitly labeled `Preview post-verification state` action for
  demonstrating the remaining prototype flow.
- Do not describe the simulated step as successful authentication.
- Add tests for Critical and applicable High-risk step-up presentation.

### ES003-R02 - Session-local decision state can still be mistaken for a real decision

**Priority:** High
**Affected areas:** Decision Prototype, Approval History, Screen States,
Acceptance Criteria

The draft requires disclosure before confirmation, but a session-local state
that changes a request to Approved or Rejected can still appear operational
after the dialog closes. A single toast or one-time warning is insufficient for
a governed action surface.

**Required change:**

- Display a persistent page-level `Frontend prototype` disclosure throughout
  Queue, Detail, and History.
- Mark every locally changed state as `Simulated` in the resulting state and Activity.
- Use prototype-specific final actions such as `Preview approval` and `Preview rejection`.
- Use `Prototype state updated` rather than success language such as `Approved`.
- Explain that refresh restores canonical fictional fixtures.
- Do not insert simulated decisions into canonical fixture History as if they
  were durable records.
- Add tests that ensure all simulated result surfaces retain disclosure.

### ES003-R03 - Prototype control boundaries need a technical non-network guarantee

**Priority:** High
**Affected areas:** Engineering Decision, Security and Privacy, Testing,
Acceptance Criteria

The specification says prototype actions make no network request, but it does
not require a design that makes accidental service integration difficult to
introduce during implementation.

**Required change:**

- Keep prototype decision behavior behind a local frontend-only adapter or
  controller whose contract cannot accept a network client.
- Keep fixtures and state transitions in the frontend feature boundary.
- Do not add environment variables, API base URLs, server actions, route
  handlers, fetch calls, mutation libraries, persistence adapters, or provider SDKs.
- Add a scoped source review to the verification plan for network and mutation primitives.
- Add a test or structural review proving prototype decision handlers remain local.

This requirement is a prototype safety boundary, not the future operational
Approval Service contract.

### ES003-R04 - Escalation appears in initial queue ordering despite being excluded

**Priority:** Medium
**Affected areas:** Attention Priority, Explicit Exclusions

The Attention Priority section includes escalated requests when future data is
represented. Assignment and escalation are explicitly excluded from the
initial single-reviewer capability. Including escalated requests in the active
queue introduces a concept the operator cannot inspect or act upon.

**Required change:**

- Remove escalation from initial queue fixtures and ordering.
- Use Near expiry, Risk, and Age as the complete initial attention ordering.
- Preserve escalation only in future extensibility documentation.

### ES003-R05 - Clarification source and destination are ambiguous

**Priority:** Medium
**Affected areas:** Request Clarification, Fixture Requirements, Activity

The architecture restricts initial clarification provenance to an authenticated
Atlas human or trusted internal actor. ES-003 does not identify who receives a
prototype clarification or who provides the fictional response.

**Required change:**

- Label the fictional destination as the requesting agent or workflow context,
  not a simulated team or external person.
- Identify returned clarification as a fictional trusted internal response.
- Display actor type, source, and timestamp in Activity.
- Do not simulate external email, chat, or notification delivery.
- Require a new fictional approval when clarification changes action, target,
  or decision-relevant content.

### ES003-R06 - Queue context preservation is underspecified

**Priority:** Medium
**Affected areas:** Approval Queue, Search Filter and Sort, Route Contract,
Acceptance Criteria

The requirement to preserve queue context `where supported` is too weak for an
approved Atlas navigation standard.

**Required change:**

- Preserve Queue or History tab, search, filters, sort, and pagination in the URL.
- Restore collection context when returning from Approval Detail.
- Preserve browser Back and Forward behavior.
- Do not require scroll restoration if the chosen framework cannot provide it
  reliably without disproportionate complexity; document that limitation.
- Replace `where supported` in acceptance criteria with deterministic behavior
  for URL-backed context.

### ES003-R07 - Non-default states need a controlled demonstration strategy

**Priority:** Medium
**Affected areas:** Screen States, Fixture Requirements, Testing, Verification

ES-003 requires loading, error, unavailable, empty, stale, and indeterminate
states but does not define how reviewers can inspect them without a backend.
Adding visible debug controls or undocumented production query switches would
weaken the product experience.

**Required change:**

- Keep the normal route on the canonical loaded fixture set.
- Exercise alternate collection and detail states through component inputs and
  deterministic tests.
- Permit review-only fixture scenarios only when they are explicitly scoped by
  the Work Order and cannot be confused with production controls.
- Do not ship a user-facing state switcher or debug panel.
- Require screenshot evidence for states selected by the Work Order's visual
  review plan.

### ES003-R08 - Disabled Approve explanation needs an accessible interaction contract

**Priority:** Medium
**Affected areas:** Evidence Gate, Accessibility, Testing

A disabled button is normally removed from keyboard focus and may not expose
its explanatory relationship consistently. Merely placing a tooltip on a
disabled Approve control would not satisfy keyboard or screen-reader needs.

**Required change:**

- Present a visible `Approval unavailable` explanation before or adjacent to
  the decision controls.
- List missing evidence categories in the Evidence area.
- Associate the decision region with the explanation using semantic descriptive structure.
- Do not rely on hover tooltip or disabled-control focus.
- Verify the explanation through accessible role, name, and visible-text tests.

### ES003-R09 - Inert links and evidence previews need explicit review behavior

**Priority:** Medium
**Affected areas:** Approval Detail, Indeterminate Execution, Security and Privacy

The specification allows fictional related links but does not distinguish
valid internal routes from inert external/provider evidence references.

**Required change:**

- Internal fictional Agent and Run references may use valid Atlas routes.
- Provider, connector, audit, or evidence destinations that do not have an
  implemented Atlas route must render as unavailable metadata or a disabled
  reference, not a deceptive link.
- Do not use `#`, fake external domains, or controls that navigate to a missing page.
- Explain unavailable related objects without blocking approval investigation.

---

## 3. Cross-Disciplinary Review

### Product

The collection-to-detail workflow, individual decision scope, reason rules,
clarification, History, and indeterminate outcome align with approved product
behavior. Removing escalation from the initial queue is required for scope
clarity.

### Design

The full-page detail choice is appropriate for the first implementation. The
persistent prototype disclosure and simulated-state treatment must be designed
as calm operational metadata rather than a warning banner that overwhelms the
screen.

### Architecture

Frontend-only scope conforms to approved boundaries. The local adapter
requirement should make accidental backend expansion visible during review.

### Security

Fictional local fixtures and inert evidence are appropriate. Step-up must be
represented without collecting credentials, and simulated decisions must never
be confused with real authorization.

### Privacy

The fixture requirements are acceptable if all identifiers, content, targets,
and evidence remain fictional. Screenshots must receive the same fixture review.

### Accessibility

The target and keyboard requirements are appropriate. The evidence-gate
explanation and persistent prototype disclosure need semantic requirements and
test coverage.

---

## 4. Approved Direction

The following ES-003 decisions are affirmed:

- Frontend-only implementation.
- No Work Order or implementation authorization yet.
- Queue and History at `/approvals`.
- Canonical full-page Approval Detail.
- No required split view.
- No assignment, escalation, bulk actions, saved views, or teams.
- Individual Approve, Reject, and Request clarification prototype interactions.
- Evidence-gated Approve presentation.
- Risk-specific decision reasons.
- Separate approval and execution outcomes.
- Indeterminate execution presentation.
- Fictional local typed fixtures.
- Existing frontend test infrastructure.
- Manual responsive, theme, browser, zoom, and accessibility review.

---

## 5. Required ES-003 Revisions

Before approval, ES-003 must:

1. Add the simulated step-up boundary.
2. Make prototype disclosure persistent and simulated-state labeling durable.
3. Define the local non-network prototype adapter boundary.
4. Remove escalation from initial queue data and ordering.
5. Define clarification provenance and destination.
6. Require URL-backed queue context preservation.
7. Define controlled alternate-state demonstration.
8. Add the accessible Approval-unavailable explanation.
9. Define behavior for unimplemented related-object destinations.
10. Extend tests and acceptance criteria for every change above.

---

## 6. Readiness Disposition

**Not Ready.**

ES-003 may become Ready only after:

- All required revisions are incorporated.
- A final Product, Design, Architecture, Security, Privacy, and Accessibility
  conformance review passes.
- The Repository Maintainer approves the revised specification.
- A separate implementation Work Order defines exact file scope and grants
  implementation authorization.

No branch, application change, dependency change, or implementation Work Order
is authorized by this review.

---

## 7. Recommended Next Step

Approve or revise the nine findings in Section 2. After approval, update ES-003
and perform a final readiness review.

---

## 8. Final Readiness Review

The approved findings were incorporated into ES-003 version 1.0.

Final review confirms that step-up is represented without collecting
credentials; prototype disclosure and simulated-state labeling persist;
decision handlers remain local and non-networked; escalation is absent;
clarification provenance is explicit; queue context is URL-backed; alternate
states require no shipped debug controls; unavailable approval is explained
accessibly; and unimplemented related objects are not deceptive links.

Tests, acceptance criteria, verification, and source review cover all required
revisions. Product, Design, Architecture, Security, Privacy, and Accessibility
conformance passes at the Engineering Specification level.

**Final disposition:** ES-003 version 1.0 is approved as the basis for an
implementation Work Order. It does not authorize implementation.
