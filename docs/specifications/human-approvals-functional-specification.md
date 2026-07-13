# Atlas Human Approvals Functional Specification

**Status:** Approved
**Version:** 1.1
**Date:** 2026-07-13
**Capability:** Human Approvals
**Product:** Atlas
**Category:** Enterprise Agent Control Center

---

## 1. Purpose

This specification defines the user-visible behavior of the Atlas Human
Approvals capability.

Human Approvals provides a governed operational workspace in which an operator
can discover, investigate, route, and decide requests for human authorization
before an agent-proposed action may proceed.

This specification defines product behavior only. It does not define APIs,
runtime behavior, persistence, authentication, authorization, policy execution,
database design, queue processing, or infrastructure.

This document does not authorize implementation. Architecture specifications,
engineering specifications, and approved implementation work orders remain
required before implementation begins.

---

## 2. Product Intent

Human Approvals must reinforce Atlas as the unified control plane for an AI
workforce.

The experience must help an operator answer:

> Which proposed actions require authorization, what evidence supports them,
> and which decision should I make?

The capability must prioritize control, evidence, accountability, operational
clarity, and safe intervention. It must not resemble a consumer inbox, chatbot,
task manager, workflow builder, or one-click automation interface.

---

## 3. Design and Product Baseline

This specification applies the following approved Atlas principles:

- Control before automation.
- Trust through evidence.
- Information before configuration.
- Inspect before act.
- High-risk actions require deliberate interaction.
- Every meaningful action leaves evidence.
- Approval authorizes an exact proposed action.
- Approval does not itself prove that the action executed successfully.
- Approval state and execution outcome are separate concepts.
- Desktop is the primary operating environment.
- Tablet supports monitoring and investigation.
- Mobile supports operational awareness and individual intervention.
- Accessibility targets WCAG 2.2 AA.

---

## 4. Scope

### 4.1 In Scope

- Approval queue.
- Approval detail.
- Individual approval decisions.
- Individual rejection decisions.
- Request clarification workflow.
- Approval history.
- Search, filtering, and sorting.
- Assignment and ownership presentation.
- Decision confirmation.
- Decision and activity history.
- Related-object navigation.
- Approval, review, assignment, expiry, and execution-outcome presentation.
- Empty, loading, unavailable, stale, and error experiences.
- Desktop, tablet, and mobile behavior.
- Keyboard and screen-reader behavior.
- Future-ready escalation presentation rules.

### 4.2 Deferred Product Capabilities

- Bulk approval.
- Bulk assignment.
- Bulk rejection.
- Active escalation in the initial single-reviewer experience.
- Multi-reviewer approval.
- Sequential approval.
- Parallel approval.
- Quorum approval.
- Delegation and temporary coverage.
- Saved views shared across teams.
- Approval analytics and reporting.
- External-channel approval decisions.
- Approval revocation.
- Reopening a completed approval.

### 4.3 Out of Scope

- APIs.
- Runtime continuation.
- Execution engine behavior.
- Backend services.
- Persistence.
- Database schema.
- Authentication.
- Authorization.
- Reauthentication mechanics.
- Policy engine behavior.
- Notification delivery infrastructure.
- Audit storage implementation.
- Queue or scheduler behavior.
- Connector execution.
- Idempotency implementation.
- Multi-tenant behavior.

---

## 5. Users and Operating Context

### 5.1 Initial User

The initial user is the Project Owner acting as the sole operator and reviewer.

The initial experience must not display team-routing controls that have no
meaningful destination.

### 5.2 Future Users

The experience must remain extensible to:

- Operators.
- Reviewers.
- Administrators.
- Team leads.
- Risk and compliance reviewers.
- Read-only investigators.
- Environment owners.

Future roles do not define current authentication or authorization behavior.

---

## 6. Canonical Terminology

| Term | Definition |
| --- | --- |
| Approval | A human decision required before an exact governed action may proceed |
| Approval request | The complete request presented for human review |
| Proposed action | The exact action for which authorization is requested |
| Target | The recipient, destination, resource, or object affected by the action |
| Evidence | Supporting information explaining the request and proposed action |
| Reviewer | The person who records the final approval decision |
| Owner | The accountable function or team responsible for the approval domain |
| Assignee | The reviewer currently expected to act on the request |
| Decision reason | The reviewer's explanation for a decision |
| Execution outcome | The result of attempting the action after authorization |
| Escalation | Routing a pending request to a higher or different review destination |
| Request clarification | Asking for missing information without approving or rejecting |

The interface must use `Approval`, not interchangeable terms such as task,
ticket, job, or message.

---

## 7. Information Architecture

### 7.1 Primary Navigation

`Approvals` remains a primary Atlas navigation destination.

The Approvals workspace contains two primary views:

1. Queue.
2. History.

Queue is the default view.

### 7.2 Detail Navigation

Every approval must have a canonical, deep-linkable detail destination.

Approval Detail must support:

- Breadcrumb navigation.
- Browser history.
- Return to previous queue context.
- Direct links to the related agent.
- Direct links to the related run.
- Direct links to related evidence.
- Direct links to the governing policy when available.
- Direct links to the related audit record when available.

### 7.3 Contextual Entry Points

An operator may enter Approval Detail from:

- Approval Queue.
- Approval History.
- Overview pending-approval summary.
- Agent Details Human Approvals tab.
- Run Detail.
- Alert Detail.
- Global search.

Contextual views must link to the canonical approval detail rather than create
separate decision experiences.

---

## 8. Approval Queue Requirements

### HA-FR-001 Queue Purpose

The queue must present actionable pending approvals across agents and runs.

### HA-FR-002 Queue Summary

The queue header must display:

- Total pending count.
- Count nearing expiry when greater than zero.
- Count currently filtered or visible.
- Last-known freshness or refresh state when relevant.

### HA-FR-003 Queue Row Information

Each queue row must display:

- Selection control where bulk actions are available.
- Risk level.
- Proposed-action summary.
- Target summary.
- Agent.
- Related run.
- Request time or age.
- Expiry time or remaining time.
- Assignee when assignment is active.
- Escalation indicator when escalation is active.
- Current approval state.

The queue must not expose full sensitive content by default.

### HA-FR-004 Default Ordering

The default sort must be named `Attention priority` and must prioritize visible
operational factors in this order:

1. Escalated requests when escalation is active.
2. Requests nearing expiry.
3. Higher-risk requests.
4. Older remaining requests.

The interface must explain the ordering. It must not present an unexplained
numeric priority score.

An approval becomes `Nearing expiry` when its remaining time is at or below 20
percent of its original approval window, with a minimum threshold of 15 minutes
and a maximum threshold of 24 hours.

An approval receives a stronger `Expiry imminent` warning when its remaining
time is at or below 5 percent of its original approval window, with a minimum
threshold of 5 minutes and a maximum threshold of 1 hour.

The interface must always display the exact expiry timestamp alongside any
relative warning. These thresholds define presentation and prioritization only;
they do not change the approval's expiry.

### HA-FR-005 Queue Interaction

Selecting a row must open Approval Detail without triggering a decision.

Returning from detail must preserve:

- Active view.
- Search query.
- Filters.
- Sort order.
- Pagination position.
- Scroll position where practical.

### HA-FR-006 Queue Views

The initial queue must provide `All pending`.

The information architecture must support future views for:

- Assigned to me.
- Unassigned.
- Escalated.
- Saved views.

Future views must not appear as active controls until their underlying product
concepts are meaningful in the current operating mode.

---

## 9. Search, Filter, and Sort Requirements

### HA-FR-007 Search Scope

Approval search must support safe metadata fields:

- Approval ID.
- Agent name.
- Agent ID.
- Run ID.
- Action type.
- Target or recipient summary.
- Policy name.
- Assignee when assignment is active.
- Decision reason in History.

Full proposed payloads and sensitive content must not be searchable by default.

### HA-FR-008 Search Feedback

Search results must identify the matching approval and preserve enough context
to distinguish similarly named requests.

No-result states must offer a direct Clear search or Clear filters action.

### HA-FR-009 Primary Filters

Queue must support filters for:

- Risk.
- Agent.
- Assignee when assignment is active.
- Age or expiry.

### HA-FR-010 Additional Filters

The filter experience must remain extensible to:

- Environment.
- Action type.
- Policy.
- Escalation.
- Approval state.
- Review progress.
- Request date.

### HA-FR-011 History Filters

History must support filters for:

- Approval state.
- Reviewer.
- Agent.
- Action type.
- Risk.
- Decision date.
- Execution outcome.
- Environment.
- Policy.

### HA-FR-012 Sort Options

Queue must support:

- Attention priority.
- Expiry soonest.
- Newest requested.
- Oldest requested.
- Risk highest.

History must support newest and oldest decision time at minimum.

---

## 10. Approval Detail Requirements

### HA-FR-013 Detail Purpose

Approval Detail must enable the operator to answer:

> Should this exact proposed action be authorized?

### HA-FR-014 Detail Header

The header must display:

- Approval ID.
- Approval state.
- Risk level.
- Proposed-action title.
- Expiry status.
- Environment when available.

### HA-FR-015 Exact Scope

The detail must display:

- Exact proposed action.
- Exact target or destination.
- Expected consequence.
- Affected scope.
- Relevant content preview.
- Request reason.
- Agent.
- Run.
- Request timestamp.
- Expiry timestamp.

### HA-FR-016 Evidence

Evidence must be visually distinct from authoritative system state.

The evidence area must support:

- Source references.
- Agent-provided rationale.
- Confidence information when available.
- Relevant input summary.
- Structured content or change preview.
- Redaction and truncation notices.
- Missing-evidence warning.

Agent-provided or model-generated rationale must be labeled as supporting
evidence and must not be presented as a policy decision or verified fact.

Approve must be unavailable unless the detail provides the minimum evidence
needed to understand the exact authorization scope:

- Exact proposed action.
- Exact target or destination.
- Expected consequence and affected scope.
- Agent and related run.
- Risk level and reason for that risk.
- Request timestamp and expiry timestamp.
- Relevant content or payload preview, or an explicit statement that the action
  has no content payload.
- Evidence source or provenance.
- Governing policy or an explicit explanation of why human approval is required.

Additional evidence is mandatory when applicable:

- A before-and-after comparison for an action that modifies an existing object.
- Exact proposed content for communication or publication actions.
- Audience and sensitivity context for external sharing.
- Amount, currency, recipient, and purpose for financial actions.
- File identity, destination, and sensitivity for file-transfer actions.

If required evidence is missing, the interface must explain what is missing and
why approval is unavailable. Reject and Request clarification must remain
available while the request is otherwise actionable.

### HA-FR-017 Governance Context

The detail must display when available:

- Why approval was required.
- Governing policy.
- Risk reason.
- Requested exception or unusual condition.
- Related environment.

### HA-FR-018 Related Objects

The detail must link directly to related objects without requiring manual ID
lookup.

### HA-FR-019 Decision Visibility

Approve and Reject must remain visible while the approval is actionable.

Request clarification must remain available as a secondary action while the
approval is actionable.

Assignment actions must be visually separate from decision actions.

Decided, expired, and cancelled approvals must not display active decision
controls.

---

## 11. Individual Decision Requirements

### HA-FR-020 Approve

Approve must open a deliberate confirmation experience that restates:

- Exact proposed action.
- Exact target.
- Expected consequence.
- Risk.
- Expiry status.

Confirmation language must state that approval authorizes the proposed action
but does not confirm successful execution.

### HA-FR-021 Approval Reason

A decision reason is required for every approval decision.

- Low and Medium risk approval requires at least one structured reason category;
  explanatory free text remains optional.
- High and Critical risk approval requires explanatory free text; a structured
  category may supplement but must not replace it.

Reason categories must be specific enough to be meaningful in decision history
and must include an `Other` option that requires free text.

### HA-FR-022 Reject

Reject must require a decision reason.

The rejection experience must explain that the proposed action will not be
authorized. Rejection must be presented as a valid governed outcome, not an
error.

### HA-FR-023 Decision Feedback

After a decision, the experience must display:

- Recorded approval state.
- Reviewer.
- Decision time.
- Decision reason.
- Separate execution-outcome area.

Decision feedback must not claim that an approved action executed unless an
execution outcome explicitly confirms it.

### HA-FR-024 Stale Decision Protection

If the approval becomes decided, expired, cancelled, or otherwise unavailable
while open, active controls must be removed and the current state must be
explained.

The interface must not imply that an unrecorded or unsuccessful decision was
accepted.

### HA-FR-025 No Undo

Completed approval decisions must not expose Undo, Reopen, or Revise actions.

A future revocation capability, if required, must be defined as a separate
governed action and must not rewrite decision history.

---

## 12. Request Clarification Requirements

### HA-FR-026 Request Clarification

Request clarification must require:

- A specific question or missing-information reason.
- A visible destination when a meaningful destination exists.

### HA-FR-027 Clarification State

Request clarification must not approve or reject the request.

The approval state remains `Pending`. Review progress becomes
`Awaiting information`.

### HA-FR-028 Clarification Expiry

The original expiry continues unchanged while clarification is pending.

The operator must be warned that requesting clarification does not extend the
authorization window.

If the approval expires, it becomes read-only. A newly created approval request
is required for any later authorization.

### HA-FR-029 Clarification Return

If clarification becomes available before expiry, the review-progress facet
returns to `In review` or an equivalent actionable presentation.

The original request, clarification question, response, and elapsed time must
remain visible in Activity.

---

## 13. Assignment and Ownership Requirements

### HA-FR-030 Distinct Accountability Concepts

The experience must distinguish:

- Owner.
- Assignee.
- Reviewer.

The agent owner must not automatically be presented as the approval owner.

### HA-FR-031 Optional Assignment

Assignment is optional and must not block an otherwise valid decision.

The final reviewer must be displayed independently of assignment.

### HA-FR-032 Assignment Actions

When assignment is active, the experience must support:

- Assign.
- Reassign.
- Clear assignment.
- Claim for myself.
- Optional assignment note.

### HA-FR-033 Assignment History

Assignment changes must appear in Activity with:

- Previous assignee.
- New assignee.
- Initiating operator.
- Timestamp.
- Note when supplied.

### HA-FR-034 Single-Reviewer Mode

The initial single-reviewer experience must hide assignment controls. It must
not display simulated teams or destinations. The reviewer remains visible after
a decision.

---

## 14. Escalation Requirements

### HA-FR-035 Initial Availability

Escalation must not appear as an active action in the initial single-reviewer
experience because no meaningful escalation destination exists.

### HA-FR-036 Future Escalation

When meaningful destinations exist, escalation must require:

- Destination.
- Reason.
- Expected response time when applicable.
- Clear ownership after escalation.

Escalation must leave the approval state as `Pending` and must appear in
Activity. It must not approve or reject the request.

---

## 15. Deferred Bulk Workflow Requirements

### HA-FR-037 Selection

Bulk decision controls are not part of the initial single-reviewer capability.
The following requirements preserve the approved future workflow and do not
authorize bulk actions in the first implementation milestone.

Bulk selection must display the exact number of selected approvals.

Cross-page selection must never be implicit. If supported later, it must state
the exact total scope.

### HA-FR-038 Bulk Action Availability

The initial capability must not expose bulk decision or assignment actions.

A future capability may support:

- Bulk assignment when assignment is active.
- Bulk rejection.

Bulk approval is prohibited in the initial capability.

Bulk escalation remains unavailable while escalation is unavailable.

### HA-FR-039 Bulk Review

When introduced through a later approved specification, bulk rejection must
open a dedicated review experience that displays:

- Exact selected count.
- Risk distribution.
- Action-type distribution.
- Agent distribution.
- Expiry warnings.
- Expandable list of every included approval.
- Shared decision reason.

### HA-FR-040 Bulk Reason

A shared decision reason is mandatory for every bulk rejection.

### HA-FR-041 Filter and Selection Safety

A filter or search change that makes selection scope ambiguous must clear the
selection or require explicit confirmation to retain it.

### HA-FR-042 Bulk Results

Bulk results must be presented per approval.

The experience must distinguish:

- Recorded decisions.
- Unchanged requests.
- Stale requests.
- Failed or unavailable requests.

An aggregate success message must not hide partial results.

---

## 16. Approval History Requirements

### HA-FR-043 History Purpose

History must provide a read-only record of approval decisions and their related
execution outcomes.

### HA-FR-044 History Information

Each history record must display:

- Approval state.
- Proposed action.
- Target.
- Agent.
- Run.
- Risk.
- Reviewer.
- Decision time.
- Decision reason.
- Execution outcome.
- Environment when available.
- Policy when available.

### HA-FR-045 Historical Detail

Opening a history record must show the Approval Detail in read-only form.

Historical detail must retain the decision context and evidence associated
with the reviewed request.

### HA-FR-046 Approval and Execution Separation

An approved request whose execution later fails remains `Approved`.

The failed execution must appear as a separate execution outcome and must link
to the related run or evidence when available.

### HA-FR-046A Indeterminate Execution Outcome

When Atlas cannot determine whether an external action occurred, the execution
outcome must display `Indeterminate` rather than success or failure.

The experience must explain that the action may or may not have occurred,
preserve the `Approved` decision unchanged, link to available investigation
evidence, and prevent retry until reconciliation establishes that retry is
safe. The eventual reconciled outcome must be appended without rewriting the
earlier history.

---

## 17. State Model

### 17.1 Approval States

| State | Meaning | Actionable |
| --- | --- | --- |
| Pending | Awaiting a human decision | Yes, unless temporarily unavailable |
| Approved | Exact proposed action authorized | No |
| Rejected | Proposed action denied | No |
| Expired | Authorization window ended | No |
| Cancelled | Request withdrawn or no longer applicable | No |

### 17.2 Orthogonal Facets

The following must remain facets rather than approval states:

| Facet | Values |
| --- | --- |
| Assignment | Unassigned, Assigned |
| Review progress | Unopened, In review, Awaiting information |
| Escalation | Normal, At risk, Escalated |
| Expiry | On track, Nearing expiry, Expired |
| Execution outcome | Not available, Pending, Succeeded, Partially succeeded, Failed, Indeterminate |

The interface must not combine facets into compound state labels.

---

## 18. Activity and Decision History

### HA-FR-047 Activity Timeline

Approval Detail must provide a chronological Activity section.

Activity must be able to represent:

- Approval requested.
- Review opened when meaningful.
- Assignment changed.
- Clarification requested.
- Clarification received.
- Escalation initiated when active.
- Approval decided.
- Approval expired.
- Approval cancelled.
- Execution outcome received.

### HA-FR-048 Event Clarity

Each activity entry must identify:

- Event type.
- Actor or source when available.
- Timestamp.
- Reason or note when relevant.
- Related object link when relevant.

---

## 19. Empty States

### HA-FR-049 Empty Queue

When no approvals are pending, display:

> No actions currently require authorization.

The state must link to History and must not use celebratory inbox-zero language.

### HA-FR-050 Filtered Empty

When filters or search produce no results, explain that no approvals match the
current criteria and provide Clear filters.

### HA-FR-051 Empty History

When no decisions exist, explain that no approval decisions have been recorded.

### HA-FR-052 Contextual Empty

When an agent or run has no approvals, state that the object has not requested
human authorization and provide a link to the broader Approvals workspace when
useful.

---

## 20. Loading and Refresh Requirements

### HA-FR-053 Layout Stability

Loading states must preserve the application shell and expected page geometry.

### HA-FR-054 Queue Loading

Queue loading must use structured row or card skeletons rather than a blocking
full-page spinner.

### HA-FR-055 Detail Loading

Detail loading must reserve regions for:

- Header.
- Proposed action.
- Evidence.
- Governance context.
- Decision controls.
- Activity.

### HA-FR-056 Background Refresh

Background refresh must not unexpectedly clear filters, selection, scroll
position, or keyboard focus.

---

## 21. Error and Unavailable States

### HA-FR-057 Error Content

Errors must explain:

- What could not be completed.
- Current known approval state.
- Operational impact.
- Available next action.

### HA-FR-058 Queue Unavailable

Queue failure must preserve visible controls and filter context where practical
and provide Retry.

### HA-FR-059 Detail Unavailable

Detail failure must preserve the approval identity when known and provide a
safe return to Queue.

### HA-FR-060 Decision Not Recorded

If a decision cannot be confirmed as recorded, the interface must not show a
success state or remove the request from the actionable context without an
explanation.

### HA-FR-061 Approval Changed During Review

If an approval is no longer actionable, display its current state, reviewer or
source of change when available, and decision time when applicable.

An indeterminate execution must not be presented as a decision-recording error.
It must use the recovery experience defined by HA-FR-046A.

### HA-FR-062 Evidence Unavailable

Missing required evidence must be clearly identified. The interface must not
hide the condition behind an empty panel.

### HA-FR-063 Partial Bulk Result

Partial bulk outcomes must remain visible until the operator acknowledges or
navigates away from the result summary.

---

## 22. Responsive Requirements

### HA-FR-064 Desktop

Desktop must support:

- Full operational table.
- Dense filters.
- Multi-selection.
- Bulk workflows.
- Persistent or sticky decision controls.
- Optional queue-and-detail split presentation.

A split presentation must not replace the canonical detail destination.

### HA-FR-065 Tablet

Tablet must support:

- Readable collection presentation.
- Reduced visible columns or compact rows.
- Filter drawer.
- Single-column detail when needed.
- Persistently reachable decision controls.

### HA-FR-066 Mobile

Mobile must support:

- Stacked approval summaries instead of a compressed desktop table.
- Full-page individual detail.
- Individual Approve and Reject.
- Request clarification.
- Safe access to evidence and policy context.
- Sticky decision controls with safe-area accommodation.
- Filter drawer.
- No document-level horizontal overflow.

Bulk approval must not be introduced on mobile. Mobile bulk workflows may be
further restricted when exact scope cannot be presented safely.

---

## 23. Accessibility Requirements

### HA-FR-067 Accessibility Target

The capability must target WCAG 2.2 AA.

### HA-FR-068 Non-Color Communication

Risk, state, expiry, escalation, errors, and execution outcomes must use text or
icons with accessible names in addition to color.

### HA-FR-069 Keyboard Operation

All queue, filter, detail, assignment, clarification, decision, and history
functions must be operable by keyboard.

### HA-FR-070 Focus Management

Dialogs and drawers must:

- Move focus to a meaningful starting point.
- Contain focus while modal.
- Close with Escape where safe.
- Restore focus to the invoking control.

### HA-FR-071 Decision Naming

Decision controls and confirmations must expose accessible names that include
the action and enough target context to avoid ambiguity.

### HA-FR-072 Time Presentation

Relative times and countdowns must expose exact timestamps.

Countdowns must not generate continuous screen-reader announcements. Only
meaningful expiry thresholds may be announced.

### HA-FR-073 Zoom and Reflow

Core content and decision controls must remain usable at 200 percent zoom and
must not obscure one another.

### HA-FR-074 Error Association

Validation errors must be associated with their fields. Error summaries must
link to affected fields when multiple errors exist.

### HA-FR-075 Reduced Motion

Motion must respect reduced-motion preferences and must not be required to
understand state changes.

---

## 24. Content, Privacy, and Safety Requirements

### HA-FR-076 Operational Language

Content must be concise, factual, calm, and consequence-oriented.

### HA-FR-077 Sensitive Content

Collection views must expose only the minimum content needed to distinguish
requests.

### HA-FR-078 Safe Preview

Content previews must:

- Be bounded.
- Identify truncation.
- Identify redaction.
- Separate source content from proposed content.
- Avoid presenting untrusted external content as trusted interface chrome.

### HA-FR-079 Confirmation Language

Confirmation text must identify scope and consequence. Generic confirmation
such as `Are you sure?` is insufficient.

### HA-FR-080 Status Language

Success feedback must confirm only the result known to the approval experience.
It must not imply execution success when only authorization is known.

---

## 25. Acceptance Criteria

The Human Approvals functional design is acceptable when all of the following
are satisfied:

1. An operator can identify urgent pending approvals within five seconds.
2. Queue rows expose risk, action, target, source, age, expiry, and state.
3. Search and filters can narrow the queue without exposing full sensitive content.
4. Opening an approval never triggers a decision.
5. Approval Detail shows exact action, target, consequence, evidence, governance context, and relationships.
6. Approve requires a scope-specific confirmation.
7. Every approval records a decision reason; lower-risk approval may use a structured category while High and Critical approval requires explanatory free text.
8. Reject always requires a decision reason.
9. Request clarification leaves the approval Pending and does not extend expiry.
10. Assignment remains separate from reviewer identity and does not block a decision.
11. Escalation is absent from the initial single-reviewer experience.
12. All bulk decision and assignment actions are unavailable in the initial single-reviewer capability.
13. Decided, expired, and cancelled approvals are read-only.
14. Approval state and execution outcome are displayed separately.
15. History preserves reviewer, decision time, reason, and related outcome.
16. Queue context is preserved after detail investigation.
17. Loading states preserve layout and application-shell continuity.
18. Error states explain impact and recovery without implying an unrecorded decision succeeded.
19. Desktop, tablet, and mobile layouts support their defined operating roles.
20. The complete individual decision workflow is keyboard operable.
21. State and risk do not rely on color alone.
22. Mobile decision controls remain usable at 200 percent zoom.
23. Approve is unavailable when required evidence is missing, while Reject and Request clarification remain available.
24. `Critical` is available as a visible risk level.
25. No screen implies that Atlas already has runtime, backend, API, authentication, authorization, persistence, or policy behavior that has not been specified and implemented.
26. An indeterminate external execution is shown as `Indeterminate`, blocks unsafe retry, and directs the operator to reconciliation without changing the approval decision.

---

## 26. Approved UX Decisions

The following decisions are approved for this specification:

| Decision | Resolution |
| --- | --- |
| Request clarification | Retained; approval remains Pending; review progress becomes Awaiting information; expiry continues |
| Bulk approval | Excluded from the initial capability |
| Bulk rejection and assignment | Deferred from the initial implementation milestone |
| Decision reasons | Required for every decision; Low/Medium may use a structured category; High/Critical approval and rejection require explanatory free text |
| Assignment | Optional in the domain model; controls hidden in initial single-reviewer mode; reviewer recorded separately |
| Escalation | Not exposed in initial single-reviewer mode; preserved for future team operation |
| Critical risk | Required as a visible risk level in the initial capability |
| Desktop split view | Optional enhancement; canonical detail navigation remains required |
| Expiry warnings | Nearing expiry at 20 percent remaining, bounded to 15 minutes through 24 hours; imminent at 5 percent, bounded to 5 minutes through 1 hour |
| Evidence gate | Approve unavailable until required action, target, consequence, provenance, risk, timing, governance, and applicable content-specific evidence are present |
| Indeterminate execution | Displayed separately from approval; unsafe retry blocked until reconciliation establishes a safe outcome |

---

## 27. Dependencies and Next Specifications

This functional specification depends on the existing Atlas product, domain,
information-architecture, UX, design-system, component-library, screen, and
application-shell baselines.

Before implementation, Atlas requires:

1. Product review and approval of this Functional Specification.
2. Design review and approval of screen and interaction details.
3. Human Approvals Architecture Specification.
4. Security and privacy review.
5. Approved engineering specification where required.
6. Approved implementation work order meeting the Definition of Ready.

---

## 28. Product and Design Review Decisions

Product and Design Review resolved the specification questions as follows:

| Question | Decision |
| --- | --- |
| Visible Critical risk level | Yes; required in the initial capability |
| Lower-risk approval reasons | Structured reason required; free text optional for Low/Medium risk |
| Request clarification in first milestone | Yes |
| Bulk rejection in first milestone | No; deferred |
| Assignment controls in single-reviewer mode | Hidden |
| Desktop split view | Optional |
| Nearing-expiry threshold | 20 percent remaining, bounded to 15 minutes through 24 hours |
| Minimum evidence before Approve | Required evidence gate defined in HA-FR-016 |

No unresolved Product or Design Review questions remain in this specification.
