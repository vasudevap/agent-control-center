# ES-003 - Human Approvals Frontend Experience

**Status:** Approved - Work Order Required
**Owner:** Repository Maintainer
**Review Owner:** Repository Maintainer
**Date:** 2026-07-13
**Version:** 1.0
**Approved:** 2026-07-13
**Approved By:** Repository Maintainer
**Implementation Authorization:** Not Granted
**Target Release:** Not Assigned
**Related Functional Specification:** `docs/specifications/human-approvals-functional-specification.md`
**Related Architecture:** `docs/architecture/13-human-approvals.md`
**Related ADR:** `docs/decisions/ADR-002-human-approvals-decision-integrity.md`

---

## 1. Purpose

Define the first implementable Human Approvals engineering increment for Atlas:
a production-quality frontend experience using fictional local data and
explicitly non-operational prototype controls.

This specification translates the approved product, UX, functional, and
architecture artifacts into a bounded frontend deliverable without implying
that Atlas already has an Approval Service, runtime continuation, APIs,
authentication, authorization, policy execution, audit persistence, or
external-action execution.

This specification does not authorize implementation and does not create an
implementation Work Order.

---

## 2. Engineering Decision

ES-003 is frontend-only.

A full operational Human Approvals implementation is not ready because the
repository does not yet contain the required platform foundations:

- Backend application.
- Authentication.
- Authorization.
- Reviewer identity and step-up authentication.
- Approval Service.
- Policy Engine implementation.
- Agent Runtime.
- Run continuation.
- PostgreSQL persistence.
- Durable audit writer.
- Transactional outbox.
- Connector idempotency and reconciliation.
- Approval APIs.

Combining those foundations with the first Human Approvals interface would
create an oversized, unverifiable implementation scope and would contradict
Atlas governance and architecture-first principles.

ES-003 therefore establishes the user experience and frontend component model
while preserving a strict boundary between prototype interaction and real
authorization.

---

## 3. Intended Outcome

Operators can explore and review a realistic Human Approvals experience that
demonstrates:

- Cross-agent approval triage.
- Risk and expiry prioritization.
- Exact-action inspection.
- Evidence and governance context.
- Approve, Reject, and Request clarification interaction design.
- Decision-reason validation.
- Approval history.
- Separate execution outcomes, including Indeterminate.
- Responsive and accessible operation.

No prototype interaction authorizes or executes an action, persists a decision,
changes a run, or writes an audit event.

---

## 4. Governing References

ES-003 is governed by:

- `AGENTS.md`.
- `PROJECT.md`.
- `ROADMAP.md`.
- `docs/specifications/product-requirements.md`.
- `docs/specifications/human-approvals-functional-specification.md` version 1.1.
- `docs/architecture/13-human-approvals.md` version 1.0.
- `docs/decisions/ADR-002-human-approvals-decision-integrity.md`.
- `docs/design/00-brand.md`.
- `docs/design/01-design-principles.md`.
- `docs/design/02-product-domain-model.md`.
- `docs/design/03-information-architecture.md`.
- `docs/design/04-user-experience.md`.
- `docs/design/07-design-system.md`.
- `docs/design/08-component-library.md`.
- `docs/design/10-screen-specifications-platform.md`.
- `docs/design/decisions/DDR-001-typography-direction.md`.
- `docs/design/decisions/DDR-002-visual-language-direction.md`.
- `docs/work-orders/005-app-shell.md`.
- `docs/work-orders/006-agents-inventory.md`.
- `docs/work-orders/007-agent-details.md`.
- `docs/work-orders/008-agent-operational-controls.md`.
- `docs/engineering-specifications/ES-002-frontend-testing-infrastructure.md`.
- Canonical engineering governance under `docs/governance/`.

If a Work Order conflicts with the approved Functional Specification,
Architecture Specification, ADR-002, or accepted design decisions, the Work
Order must be corrected before implementation.

---

## 5. Approved Scope

### 5.1 Approval Queue

- Replace the current `/approvals` placeholder.
- Provide Queue and History tabs.
- Make Queue the default view.
- Present a desktop and tablet operational table.
- Present stacked approval summaries on mobile.
- Display pending count and near-expiry count.
- Display Risk, Proposed action, Target, Agent, Run, Requested, Expires, and State.
- Hide assignment and escalation controls in initial single-reviewer mode.
- Exclude row-level decision buttons.
- Open canonical Approval Detail for investigation.
- Preserve queue context after returning from detail.

### 5.2 Search, Filter, and Sort

- Search safe fictional metadata only.
- Search approval ID, agent name and ID, run ID, action type, target summary,
  and policy name.
- Filter by risk, agent, and age or expiry.
- Provide additional filters for action type and approval state where relevant.
- Combine search and filters predictably.
- Show accurate visible-result count.
- Provide Clear filters recovery.
- Support Attention priority, Expiry soonest, Newest requested, Oldest requested,
  and Risk highest sorting.

### 5.3 Attention Priority

Attention priority uses the approved visible ordering:

1. Near-expiry requests.
2. Higher-risk requests.
3. Older remaining requests.

Initial queue fixtures and ordering must not represent escalation. Escalation
remains a future capability.

Near-expiry presentation is derived from fictional request and expiry times:

- `Nearing expiry`: 20 percent remaining, bounded between 15 minutes and 24 hours.
- `Expiry imminent`: 5 percent remaining, bounded between 5 minutes and 1 hour.

Exact expiry timestamps remain available wherever relative time is displayed.

### 5.4 Approval Detail

- Add a canonical approval-detail route.
- Use breadcrumbs and preserve browser history.
- Use a full-page detail layout as the required initial implementation.
- Treat desktop queue-and-detail split view as optional and exclude it from the
  initial Work Order unless separately approved.
- Display Approval ID, state, risk, action, target, consequence, scope, agent,
  run, request time, expiry, environment, and governing policy.
- Display evidence source, provenance, confidence when available, content
  preview, redaction state, truncation state, and missing-evidence state.
- Display related Agent, Run, Policy, Evidence, and Audit references where the
  fictional fixture provides them.
- Display Activity in chronological order.
- Keep approval decision and execution outcome visually separate.

### 5.5 Evidence Gate

Approve is available in the prototype only when all applicable fictional
evidence requirements are complete:

- Exact action.
- Exact target.
- Expected consequence and affected scope.
- Agent and run identity.
- Risk level and risk reason.
- Request and expiry timestamps.
- Relevant content or explicit no-content declaration.
- Evidence source or provenance.
- Governing policy or reason approval is required.
- Applicable action-specific evidence.

When evidence is incomplete:

- Approve is disabled.
- Missing evidence is explained next to the disabled action and in the Evidence area.
- Reject remains available.
- Request clarification remains available.

This frontend gate demonstrates product behavior only. It is not a security or
authorization control.

### 5.6 Decision Prototype

The prototype supports:

- Approve.
- Reject.
- Request clarification.

Each action opens its approved confirmation or form experience.

The interface must state before confirmation that:

- The interaction is a prototype.
- No authorization will be recorded.
- No action will execute.
- The result will not persist after refresh or navigation outside the prototype state boundary.

After confirmation, the interface may update session-local presentation state
to demonstrate the resulting UX. Feedback must say `Prototype state updated`
or equivalent and must not claim that an approval was recorded, audited, or
executed.

A persistent `Frontend prototype` disclosure remains visible throughout Queue,
Detail, and History. Every locally changed status and Activity entry is marked
`Simulated`. Final actions use labels such as `Preview approval`,
`Preview rejection`, and `Preview clarification`. Refresh restores canonical
fictional fixture state, and simulated decisions do not enter canonical fixture
History as durable records.

### 5.6.1 Simulated Step-Up Boundary

Critical approvals and applicable High-risk actions must represent the required
step-up authentication boundary. The prototype explains that operational Atlas
requires identity verification, renders no credential or identity-provider
fields, and never claims authentication occurred. An explicitly labeled
`Preview post-verification state` action may demonstrate the remaining flow.

### 5.7 Decision Reasons

- Low and Medium approval requires a structured reason category.
- Free text is optional for Low and Medium unless `Other` is selected.
- High and Critical approval requires explanatory free text.
- Every rejection requires explanatory free text.
- Request clarification requires a specific question or missing-information reason.
- Inline validation and an accessible error summary are required.

Reason categories use fictional local metadata and must not imply a production
policy taxonomy.

### 5.8 Request Clarification

The prototype demonstrates:

- Approval remains Pending.
- Review progress becomes Awaiting information.
- Original expiry remains unchanged.
- Activity records the fictional clarification request.
- The destination is the requesting agent or workflow context.
- Returned information is labeled as a fictional trusted internal response.
- Activity displays actor type, source, and timestamp.
- Returning fictional information restores In review.
- A changed action, target, or content requires a new request rather than clarification.

No external email, chat, or notification delivery is simulated.

No external message or notification is sent.

### 5.9 Approval History

- Provide a read-only History tab.
- Display Approved, Rejected, Expired, and Cancelled examples.
- Display action, target, agent, run, risk, reviewer, decision time, reason,
  execution outcome, environment, and policy where available.
- Search and filter History using safe fictional metadata.
- Open read-only Approval Detail.
- Include examples where Approved has Succeeded, Failed, and Indeterminate execution outcomes.

### 5.10 Indeterminate Execution

At least one fictional historical approval demonstrates an `Indeterminate`
external execution outcome.

The experience must:

- State that the action may or may not have occurred.
- Preserve Approved as the decision.
- Present investigation and reconciliation as the required next step.
- Hide or disable Retry.
- Link to fictional run, connector, provider, and audit evidence where available.
- Avoid representing Indeterminate as Failed.

### 5.11 Screen States

The implementation must provide deterministic representations for:

- Populated queue.
- No pending approvals.
- Filtered empty.
- Empty history.
- Loading queue.
- Loading detail.
- Queue error.
- Detail unavailable.
- Unknown approval ID.
- Missing evidence.
- Approval already decided.
- Expired during review.
- Cancelled approval.
- Prototype decision state.
- Indeterminate execution outcome.

The normal route uses the canonical loaded fixture set. Alternate states are
exercised through component inputs and deterministic tests. A Work Order may
authorize explicit review-only fixture scenarios when they cannot be confused
with product controls. Do not ship a user-facing state switcher, debug panel, or
undocumented state-selection control.

### 5.12 Local Prototype Boundary

Prototype decisions use a local frontend-only adapter or controller whose
contract does not accept a network client. Fixtures and transitions remain in
the frontend feature boundary.

The implementation must not add environment variables, API base URLs, fetch or
other network requests, server actions, route handlers, mutation libraries,
persistence adapters, or provider SDKs. This adapter is a prototype safety
mechanism, not the future Approval Service client contract.

---

## 6. Explicit Exclusions

ES-003 does not include:

- Backend code.
- APIs.
- Network requests.
- Database or persistence.
- Authentication or authorization.
- Reviewer eligibility enforcement.
- Step-up authentication.
- Approval Service.
- Policy evaluation.
- Runtime continuation.
- Agent execution.
- Connector execution.
- Audit persistence.
- Transactional outbox.
- Idempotency implementation.
- Reconciliation implementation.
- Notifications.
- Real-time refresh.
- Assignment controls.
- Escalation controls.
- Bulk selection or actions.
- Saved views.
- Shared team views.
- Multi-reviewer workflows.
- Real organization, person, email, account, file, token, credential, or customer data.

---

## 7. Route Contract

The frontend increment must provide:

| Route | Responsibility |
| --- | --- |
| `/approvals` | Queue and History collection experience |
| `/approvals/[approvalId]` | Canonical individual approval detail |

Contextual Agent Details and Run Detail links may navigate to the canonical
detail route. ES-003 does not redesign unrelated Agent or Run screens unless a
separately approved Work Order explicitly includes a minimal link refinement.

Queue or History tab, search, filters, sort, and pagination must be represented
in the URL and restored when returning from Approval Detail. Browser Back and
Forward preserve this context. Scroll restoration is optional when it cannot be
provided reliably without disproportionate complexity and must be documented
as a limitation.

Unknown fictional approval IDs must produce a clear unavailable or not-found
experience inside the persistent application shell.

Internal fictional Agent and Run references may link to valid Atlas routes.
Related destinations without implemented routes render as unavailable metadata
or disabled references. Do not use `#`, fictional external domains, or links to
missing pages.

---

## 8. Frontend Domain Model

The frontend model must represent the approved product concepts without
claiming to be a backend contract.

### 8.1 Approval

- ID.
- Agent reference.
- Run and optional run-step reference.
- Environment.
- Action type and summary.
- Target summary.
- Consequence and affected scope.
- Risk and risk reason.
- Approval state.
- Review progress.
- Request and expiry timestamps.
- Policy reference.
- Evidence references and completeness.
- Reviewer and decision data for history.
- Execution outcome.
- Activity entries.

### 8.2 Canonical Approval States

- Pending.
- Approved.
- Rejected.
- Expired.
- Cancelled.

### 8.3 Review Progress

- Unopened.
- In review.
- Awaiting information.

### 8.4 Execution Outcomes

- Not available.
- Pending.
- Succeeded.
- Partially succeeded.
- Failed.
- Indeterminate.

States and facets must remain distinct. Do not create compound labels such as
`ApprovedFailed` or `PendingAwaitingInformation`.

---

## 9. Fixture Requirements

All fixtures must be fictional, deterministic, local, typed, and free of
secrets or personal information.

The fixture set must include enough variety to exercise:

- Low, Medium, High, and Critical risk.
- Multiple fictional agents and runs.
- Multiple action types.
- Multiple environments.
- On-track, near-expiry, expiry-imminent, and expired timing.
- Complete and incomplete evidence.
- Content-bearing and no-content actions.
- Modification with before-and-after evidence.
- External communication.
- External file sharing.
- Financial action.
- Approved, Rejected, Expired, and Cancelled history.
- Succeeded, Failed, Partially succeeded, and Indeterminate execution outcomes.
- Clarification requested and clarification returned.
- Redacted and truncated evidence.
- Unknown or unavailable detail.

Time-sensitive fixtures must use a deterministic reference-time strategy in
tests. Product presentation may derive relative values without making tests
depend on the developer's current wall-clock time.

---

## 10. Component Plan

Use existing shared Atlas components wherever they satisfy the requirement.

Expected reusable feature components include:

- Approval queue table.
- Mobile approval summary.
- Approval risk indicator.
- Expiry indicator.
- Approval state badge.
- Approval filters.
- Approval detail header.
- Proposed-action summary.
- Evidence panel.
- Governance summary.
- Related-object links.
- Decision action rail.
- Decision confirmation dialog.
- Decision-reason form.
- Clarification form.
- Approval activity timeline.
- Execution-outcome panel.
- Prototype disclosure.

Before implementation, the Work Order must map these needs to the existing
component library and identify only the genuinely reusable additions. Dialogs
are limited to confirmation and short forms. Complex investigation remains on
the detail page.

---

## 11. Responsive Requirements

### Desktop

- Operational table.
- Full filter row.
- Full-page detail with persistent decision access.
- No required split view.

### Tablet

- Readable table or approved compact collection presentation.
- Reduced visible columns where necessary.
- Filter drawer where inline filters no longer fit.
- Single-column detail where needed.

### Mobile

- Stacked approval summaries instead of a compressed table.
- Full-page detail.
- Sticky individual decision controls with safe-area spacing.
- Full-height filter drawer.
- No bulk workflow.
- No document-level horizontal overflow.
- Bounded horizontal scrolling only for technical payload content where unavoidable.

Light and dark themes are first-class at every supported width.

---

## 12. Accessibility Requirements

The implementation targets WCAG 2.2 AA and must support:

- Semantic table structure on desktop and tablet where a table is used.
- Accessible names for risk, state, expiry, and decision controls.
- Text or icon support in addition to semantic color.
- Keyboard operation for search, filters, queue navigation, detail, dialogs,
  decision reasons, clarification, and History.
- Visible focus states.
- Dialog focus containment and restoration.
- Escape behavior where safe.
- Accessible validation summary and field-level errors.
- Exact timestamp access for relative time.
- Non-continuous screen-reader announcements for countdowns.
- Correct heading hierarchy and landmark structure.
- Reflow and operability at 200 percent zoom.
- Reduced-motion support.
- Touch targets appropriate for mobile intervention.

When Approve is unavailable, a visible `Approval unavailable` explanation
appears before or adjacent to the decision region. Missing evidence categories
appear in Evidence. Semantic descriptive structure associates the decision
region with the explanation without relying on hover, tooltip, or focus on a
disabled control.

Accessibility defects are functional defects.

---

## 13. Security and Privacy

- Fixtures contain no real personal or organizational data.
- No secrets, tokens, credentials, provider identifiers, or real messages are used.
- No prototype action performs a network request.
- Evidence previews render as inert text or allowlisted local structures.
- No raw HTML, active document content, remote embed, or executable content is rendered.
- External links, if represented, use fictional or inert destinations.
- Search indexes safe metadata only.
- Full payload content does not appear in collection views.
- Prototype state is memory-only and is not presented as durable.
- The UI must state that frontend evidence gating is not a security boundary.
- Model-generated rationale is visibly labeled as untrusted supporting evidence.
- Sensitive-value patterns must not be introduced into fixtures or screenshots.

---

## 14. Testing Requirements

Use the approved Vitest, React Testing Library, jsdom, and user-event baseline.

Tests must cover observable behavior rather than component internals.

### 14.1 Queue

- Attention-priority ordering.
- Search across approved metadata fields.
- Independent filters.
- Combined filters.
- Sort options.
- Accurate visible count.
- Clear filters.
- Filtered-empty recovery.
- Queue-to-detail destinations.

### 14.2 Detail

- Complete scope and evidence presentation.
- Related-object links.
- Decision and execution separation.
- Read-only terminal states.
- Unknown approval handling.

### 14.3 Decisions

- Prototype disclosure.
- Low and Medium structured-reason validation.
- `Other` free-text requirement.
- High and Critical free-text requirement.
- Rejection free-text requirement.
- Clarification-question requirement.
- Evidence gate disables Approve.
- Reject and Request clarification remain available with missing evidence.
- Session-local prototype feedback does not claim persistence or execution.
- Persistent prototype disclosure remains after every simulated transition.
- Simulated states and Activity entries remain labeled `Simulated`.
- Critical and applicable High-risk flows present the step-up boundary.
- Step-up preview collects no credentials and claims no authentication.
- Decision handlers remain inside the local non-network boundary.

### 14.4 Time and State

- Near-expiry thresholds.
- Expiry-imminent thresholds.
- Exact timestamp availability.
- Expired-during-review behavior.
- Clarification does not extend expiry.
- Indeterminate outcome blocks Retry presentation.

### 14.5 Screen States

- Populated.
- Initial empty.
- Filtered empty.
- Loading.
- Error.
- Unavailable detail.
- Read-only history.

### 14.6 Navigation and References

- URL-backed tab, search, filter, sort, and pagination state.
- Browser Back and Forward context restoration.
- Valid internal Agent and Run destinations.
- Unimplemented related objects render without deceptive links.

### 14.7 Accessibility-Specific Behavior

- Visible Approval-unavailable explanation.
- Missing evidence discoverable through accessible role, name, and text.
- Decision region semantically associated with the explanation.
- Prototype disclosure discoverable without disruptive repeated announcements.

Responsive layout, visual quality, theme fidelity, focus visibility,
screen-reader output, browser history, sticky positioning, zoom, and horizontal
overflow require manual browser and design review unless a later approved
browser-testing specification adds automation.

---

## 15. Documentation Deliverables

Implementation must update only the documentation required by the approved Work
Order and Definition of Done.

Expected deliverables include:

- Approved implementation Work Order.
- Relevant component-library additions or refinements.
- Relevant screen-specification updates.
- Tests documenting observable behavior.
- Implementation report under `docs/reviews/`.
- Visual evidence for desktop, tablet, mobile, light, and dark themes.
- Explicit record that the increment remains frontend-only.

Do not rewrite approved architecture or product decisions during implementation.
Any required change returns to the appropriate review process.

---

## 16. Acceptance Criteria

ES-003 implementation is acceptable only when:

1. `/approvals` is no longer a placeholder.
2. Queue and History are available within the existing application shell.
3. Queue is the default view.
4. Pending and near-expiry counts are accurate for the fictional fixture set.
5. Queue rows expose the approved operational hierarchy.
6. Search, filters, sorting, counts, and Clear filters behave deterministically.
7. Attention priority follows the approved visible ordering.
8. `/approvals/[approvalId]` provides canonical deep-linkable detail.
9. Returning from detail restores URL-backed tab, search, filter, sort, and pagination context.
10. Detail displays exact scope, evidence, governance, relationships, and Activity.
11. Approve is unavailable when required evidence is missing.
12. Reject and Request clarification remain available with incomplete evidence.
13. Decision-reason validation follows risk-specific requirements.
14. Request clarification leaves approval Pending and preserves expiry in prototype state.
15. Assignment, escalation, bulk actions, and saved views are absent.
16. Terminal approvals are read-only.
17. Approval state and execution outcome are separate.
18. Indeterminate execution is distinct from Failed and blocks Retry.
19. Prototype disclosure appears before any decision interaction.
20. No feedback claims authorization, persistence, audit, continuation, or execution.
21. Refresh returns to canonical fictional fixture state.
22. Loading, empty, filtered-empty, error, unavailable, stale, and indeterminate states exist.
23. Desktop and tablet use an appropriate operational collection presentation.
24. Mobile uses stacked summaries and full-page individual detail.
25. No supported viewport has document-level horizontal overflow.
26. Light and dark themes preserve hierarchy and semantic meaning.
27. Keyboard operation and focus management satisfy the approved workflow.
28. State and risk never rely on color alone.
29. Component tests cover the required observable behavior.
30. Existing routes and approved Agent Details behavior do not regress.
31. Typecheck, lint, tests, and production build pass under the existing CI baseline.
32. Fixtures are fictional, local, deterministic, typed, and non-sensitive.
33. No API, backend, persistence, authentication, authorization, policy, runtime,
    connector, audit, or notification implementation is introduced.
34. The implementation report records scope, evidence, limitations, risks, and
    frontend-only status.
35. Frontend prototype disclosure remains visible throughout Queue, Detail, and History.
36. Session-local state and Activity changes are labeled Simulated and remain separate from canonical fixture History.
37. Critical and applicable High-risk decisions show the step-up boundary without collecting credentials or claiming authentication.
38. Prototype decision handlers remain behind the local non-network adapter boundary.
39. Initial queue fixtures and ordering contain no escalation behavior.
40. Clarification Activity identifies trusted fictional provenance and the requesting agent or workflow context.
41. Alternate states are testable without a shipped user-facing debug control.
42. Approval-unavailable explanation is visible and associated with the decision region.
43. Unimplemented related-object destinations do not render as deceptive links.

---

## 17. Verification Plan

When implementation is later authorized, verification must include:

```text
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

Manual browser review must cover:

- 1440px desktop.
- 1024px desktop or compact desktop.
- 768px tablet.
- 375px mobile.
- Light theme.
- Dark theme.
- Queue and History.
- Approval Detail.
- Decision dialogs and validation.
- Keyboard focus flow.
- 200 percent zoom.
- Loading, empty, error, expired, and indeterminate states.
- No document-level horizontal overflow.
- No unexpected console errors.

Scoped source review must confirm the approvals feature introduces no network
client, server action, route handler, API base URL, persistence adapter,
mutation library, or provider SDK.

No validation is authorized by this draft alone.

---

## 18. Risks and Mitigations

### Prototype mistaken for operational authorization

Mitigation: persistent prototype disclosure, decision-specific disclosure, no
network or persistence, precise feedback, and implementation-report limitation.

### Rubber-stamp interaction design

Mitigation: no row-level decisions, evidence-first detail, risk-specific reason
requirements, and deliberate confirmation.

### Sensitive content in fixtures

Mitigation: fictional safe metadata, inert evidence, scoped search, and explicit
fixture review.

### Time-dependent test instability

Mitigation: deterministic reference time and controlled derivation.

### State-model drift from architecture

Mitigation: one frontend domain model aligned to the approved Functional
Specification and Architecture Specification.

### Scope expansion into backend behavior

Mitigation: explicit exclusions, no network path, no persistence, and review of
every changed file against ES-003 scope.

### Over-complex first implementation

Mitigation: full-page detail, no split view requirement, no assignment,
escalation, saved views, or bulk workflow.

---

## 19. Rollback

Rollback of a future ES-003 implementation consists of reverting its approved
frontend pull request, restoring the `/approvals` placeholder and removing the
new route, feature components, fictional fixtures, tests, and implementation
documentation.

No production data, approval, external action, backend service, or deployment
state requires recovery because ES-003 is frontend-only.

---

## 20. Future Operational Engineering Specification

A separate Engineering Specification is required before Human Approvals can
become operational.

That later specification must address:

- Authentication and reviewer identity.
- Authorization and step-up authentication.
- Approval Service contracts.
- Policy Engine integration.
- Agent Runtime waiting and continuation.
- PostgreSQL approval model.
- Approval revision and concurrency.
- Decision-context manifests.
- Durable audit events.
- Transactional outbox.
- Idempotent continuation consumers.
- Connector idempotency declarations.
- Indeterminate-outcome reconciliation.
- API contracts and structured errors.
- Retention and redaction.
- Metrics, logs, alerts, and operational recovery.
- Integration, contract, security, and end-to-end testing.

ES-003 must not be treated as satisfying any of these requirements.

---

## 21. Readiness Decision

ES-003 is approved as the engineering basis for drafting an implementation Work
Order. Product, Design, Architecture, Security, Privacy, and Accessibility
review passed after revision.

ES-003 is not implementation authorization.

Before implementation may begin:

1. A Work Order identifies component reuse and exact authorized file and behavior scope.
2. The Work Order and ES-003 satisfy the Definition of Ready.
3. The Repository Maintainer approves the Work Order.
4. Implementation authorization is explicitly granted.

Until these conditions are satisfied, do not create an implementation branch,
change application code, install dependencies, or begin implementation.
