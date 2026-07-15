# Work Order 009: Alternate Design Mapping

**Status:** Review In Progress - No Items Confirmed
**Work Order:** [WO-009 Human Approvals Frontend Experience](../work-orders/009-human-approvals-frontend-experience.md)
**Selected implementation:** `main` at and after pull request #9
**Design history:** `git log --oneline archive/gui-alternate-design`
**Date opened:** 2026-07-15

---

## 1. How this review works

This worksheet maps WO-009 requirements to candidate evidence in the selected
alternate design. A mapping is not a completion decision.

Each step uses one of four preliminary labels:

- **Candidate match:** relevant implementation or design evidence exists, but
  the item still requires confirmation.
- **Partial candidate:** some evidence exists and a gap or decision remains.
- **No candidate found:** the selected design does not currently appear to
  address the requirement.
- **Manual verification required:** code alone cannot establish the result.

No Work Order checklist item may be checked until the repository owner reviews
the relevant step, resolves any tension, and explicitly confirms the result.
Phase 2 page work remains paused during this review.

### Automated-evidence decision

On 2026-07-15, the repository owner approved replacing repetitive manual
functional confirmations with automated evidence wherever the existing test
stack can establish the behavior. The review will now:

- add passing Vitest and React Testing Library coverage for behavior already
  present;
- record uncovered requirements as explicit pending tests or review items,
  without weakening the required suite or claiming they pass;
- retain owner review for product decisions and subjective visual quality; and
- propose browser/E2E and visual-regression infrastructure separately because
  ES-002 did not authorize that testing layer.

No WO-009 Definition of Done item is completed by adopting this test strategy.

## 2. Design-history anchors

| Commit | Candidate relevance |
| --- | --- |
| `a7df730` | Introduced the alternate Human Approvals prototype, fixtures, local controller, dialogs, routes, and focused tests. |
| `7baa928` | Put risk first, made review progress explicit, and deliberately replaced the Agent filter with Review. |
| `6b21b33` | Made applicable Approvals columns sortable. |
| `e3ea2e9` | Replaced color-only state styling with icon-and-text presentation. |
| `56a8c70` | Refined the decision card and added icons to decision-state explanations. |
| `68e1dbd` | Aligned Approval Detail state, risk, and review metadata. |
| `cff37f5` | Standardized table-cell and header presentation. |
| `42881f2` | Final handoff that identifies the selected design principles and known gaps. |

These commits explain why the UI looks and behaves as it does. They do not
override the Functional Specification, Architecture 13, ADR-002, ES-003, or
WO-009.

## Step 1 - Scope, prototype boundary, and provenance

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Canonical Queue, History, and detail routes | `approvals/page.tsx`, `approvals-workspace.tsx`, and `[approvalId]/page.tsx` | Candidate match | Confirm navigation in a real browser. |
| Typed fictional fixtures | `approval-data.ts` defines typed records and local fixtures using canonical agents. | Candidate match | Review every fixture for safe, fictional content and required variety. |
| Frontend-only mutation boundary | `approval-prototype-controller.ts` accepts records and values only; it has no network client. | Candidate match | Run a scoped source review for network, persistence, server actions, and provider SDKs. |
| Session-only, non-persistent simulation | Approval Detail disclosure and controller state are component-local. | Candidate match | Confirm refresh restores fixtures and all outcome copy remains non-operational. |
| No backend, auth, runtime, policy, audit, or execution implementation | No such implementation is evident in the selected approval files. | Manual verification required | Perform and record the structural source scan required by ES-003. |

### Step 1 evidence captured for owner review

The following evidence has been collected without changing a confirmation
state:

- A scoped search of the approval feature, shared dialog, and Agent Details
  integration found no `fetch`, Axios, XMLHttpRequest, WebSocket, EventSource,
  mutation-library, server-action, browser-storage, environment-variable, or
  external-URL primitive.
- Approval feature imports are limited to React, Next.js internal links, the
  shared Atlas component library, Lucide icons, and the approved Radix dialog
  primitive.
- The prototype controller is a local record transformer. It accepts no
  service, network client, persistence adapter, credentials, or environment
  configuration.
- Fixture contact values use the reserved `.example` domain and no secret,
  token, credential, or real-provider identifier was found.
- Run references are plain metadata labeled unavailable; Agent references use
  internal Atlas routes.

Still pending before Step 1 can be confirmed:

- manually change a simulated decision, refresh, and verify that canonical
  fixture state returns;
- review every fixture string for fictional, non-sensitive provenance; and
- decide whether the structural scan should be captured as an automated test
  or retained as review evidence.

## Step 2 - Information architecture and navigation

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| `/approvals` is canonical Queue destination | `ApprovalsWorkspace` defaults `view` to `queue`. | Candidate match | Confirm default URL and browser behavior. |
| Queue and History are URL-backed sibling views | Tab state reads and writes the `view` query parameter; a `popstate` listener restores collection controls during Back/Forward navigation. | Candidate match with component and browser evidence | No mapping gap remains; retain final accessibility and responsive review. |
| `/approvals/[approvalId]` is canonical detail | Dynamic route resolves fixture IDs and renders unavailable state for unknown IDs. | Candidate match | Add route-level navigation and unknown-ID tests. |
| Return navigation preserves collection context | Detail reads a guarded `from` value, and row/card links now preserve view, search, Risk, Review, sort, direction, and page. | Candidate match with automated evidence | Verify the final detail-to-collection keyboard workflow during accessibility review. |
| Agent Details deep-links only canonical fixtures | Agent Detail derives links from the shared approval fixture set. | Candidate match | Add the required focused test for linked and unlinked agents. |

## Step 3 - Queue experience

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Title, operational description, and persistent prototype disclosure | `PageHeader` uses `Approvals`, an operational description, and a `Frontend prototype` marker. | Partial candidate | Decide whether the shorter selected title amends the literal `Human Approvals` title requirement. |
| Visible count versus total | Results summary displays visible and total Queue counts plus nearing-expiry count. | Candidate match | Add an accurate-count test after filters and pagination. |
| Approved full-text search fields | Search covers ID, agent ID/name, action, target, run, policy, and evidence-source labels. | Candidate match with automated evidence | No mapping gap remains. |
| State, risk, agent, policy, and expiry filters | The selected design exposes Risk and Review only. Commit `7baa928` deliberately replaced Agent with Review. | Partial candidate | Decide whether to amend WO-009 to the selected concise filter set or add the missing filters without weakening the design. |
| Sortable attention, requested, expiry, risk, and agent values | Commit `6b21b33` introduced the controls; the reconciliation round corrected direction handling and added focused tests for every supported sort. | Candidate match with automated evidence | Complete the remaining manual responsive and assistive-technology review. |
| Active-filter summary with individual removal and Clear filters | Active values remain visible in the Search, Risk, and Review controls, and Clear filters resets the collection. | Owner-approved prototype amendment | Keep the concise toolbar without duplicate chips; revisit chips if filters become numerous or move behind a collapsed control. |
| Accessible semantic desktop table | The table now has a screen-reader caption and the active sortable header exposes `aria-sort`; inactive sortable headers omit it. | Candidate match with automated evidence | Complete manual screen-reader and responsive review. |
| Equivalent mobile card list | `ApprovalCard` replaces the table below `md` and preserves state, risk, action, target, agent, identifier, requested time, expiry, and review/outcome context. The owner visually accepted the current content and formatting after a 320 px no-overflow check. | Candidate match with automated and owner visual evidence | Complete touch-target and accessibility evidence during the final manual review. |
| URL-backed view, search, filters, sort, direction, and page | View, query, Risk, Review, sort, direction, and page are written to and restored from the URL for the owner-approved concise control set, including Back/Forward replay. | Candidate match for the approved prototype controls | State, Agent, Policy, and Expiry filters remain formally deferred by owner decision. |
| Finite local pagination | `PAGE_SIZE` and Previous/Next controls are present. | Candidate match | Add pagination, URL restoration, and boundary tests. |
| Loading, error, no-data, and filtered-empty states | `presentationState` and `StateCard` cover all four representations. | Candidate match | Add the required tests; confirm the controlled states in browser review. |
| Row/card activation opens canonical detail | Desktop rows use stretched links and mobile cards are links; both encode the complete originating collection URL. | Candidate match with automated evidence | Verify the final keyboard and mobile navigation flow during accessibility review. |
| Attention prioritization without color alone | Default ordering combines expiry urgency and risk; Risk, Review, and State use icon vocabulary. | Candidate match | Verify urgency presentation and keyboard/screen-reader meaning. |
| No bulk, assignment, transfer, or escalation controls | None appear in the selected Queue. | Candidate match | Confirm through UI and source review. |

## Step 4 - History experience

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| URL-backed History view | `view=history` restores after hydration, updates through collection navigation, and participates in Back/Forward restoration without a hydration mismatch. | Candidate match with automated and browser evidence | Retain the final keyboard and assistive-technology review. |
| Queue-equivalent controls, states, pagination, and responsive fallback | History reuses the tested collection workspace, pagination/state components, desktop table, and mobile-card fallback. Its concise controls use Search, Risk, and terminal State instead of Queue's active-review progress. | Candidate match for the approved prototype controls | Reviewer, Agent, Action type, Decision date, Execution outcome, Environment, and Policy filters remain formally deferred until production-scale needs justify them. |
| Terminal and Indeterminate records | Fixtures and focused tests cover Approved, Rejected, Expired, Cancelled, Succeeded, and Indeterminate examples. | Candidate match with automated evidence | Retain the final theme and assistive-technology review. |
| Outcome, reason, decision time, reviewer, and correlation/reference context | History fixtures now model explicit `decidedAt`, reviewer, reason, outcome, and correlation fields. Table rows, mobile cards, and terminal detail expose this context. | Candidate match with automated and browser evidence | Retain final content-density and assistive-technology review. |
| Historical records are visibly distinct from actionable requests | History is a separate URL-backed tab, uses decision-time and outcome metadata, and detail disables decision controls for terminal records. | Candidate match with automated and browser evidence | Retain the final keyboard review. |
| Useful default History ordering | History defaults to newest explicit `decidedAt`; the Decided header reverses the order to oldest first. | Candidate match with automated and browser evidence | No mapping gap remains. |

## Step 5 - Approval Detail and decision safety

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Identifier, state, risk, urgency, agent, requested time, and disclosure | Header metadata, Request context, Expiry label, and prototype notice provide these facts. | Candidate match | Confirm no duplicate or missing facts at all widths. |
| Exact action, target, payload summary, effect, and scope | Proposed action card includes action, target, consequence, scope, and environment. | Partial candidate | Decide whether a distinct payload/content summary is required by the fixture model. |
| Policy and governance rationale | Dedicated divided card presents policy and review rationale. | Candidate match | Confirm long policy references wrap and remain readable. |
| Evidence separated from untrusted content | System metadata, untrusted preview, and missing-evidence alert are visually separated. | Candidate match | Verify accessible association and inert rendering. |
| Related Agent, Run, and Artifact treatment | Agent links canonically; Run is visibly unavailable; optional fictional Artifact metadata is modeled and displayed with an explicit unavailable-in-prototype treatment. | Candidate match with automated evidence | Extend fixture variety only if later Artifact-page work requires it. |
| Activity timeline with `Simulated` labeling | Activity renders simulated entries with an explicit badge. | Candidate match | Test clarification and approval activity, not rejection only. |
| Accessible Approval-unavailable explanation | Missing evidence appears visibly, and every rendered Decision region references the canonical explanation through `aria-describedby`. | Candidate match with automated and browser evidence | Retain final assistive-technology review. |
| Reason behavior for approve, reject, and clarification | Reject and High/Critical approve require text; Low/Medium approve is optional; clarification requires a question. | Candidate match with automated evidence | Retain final keyboard and announcement review. |
| Confirmation restates approval and outcome | Dialog restates ID, action, target, consequence, risk, expiry, and simulated outcome. | Candidate match | Add tests for all three decision paths. |
| Simulated step-up for Critical and applicable High risk | Controller and dialog require the acknowledgement for all High/Critical fixtures. | Candidate match | Confirm which High-risk policies should require it and test both required and non-required boundaries if applicable. |
| Indeterminate treatment is distinct, blocks Retry, and directs investigation | Desktop and mobile flows label Indeterminate, block Retry, and direct the operator to investigate evidence before refreshing or returning. | Candidate match with automated and browser evidence | Retain final assistive-technology review. |
| Historical approvals are read-only | Non-Pending records disable/hide decision paths. | Candidate match | Add terminal-state tests at desktop and mobile widths. |

## Step 6 - Fixtures and controlled states

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Low, Medium, High, and Critical pending approvals | Queue fixtures cover all four risk levels. | Candidate match | Confirm default ordering and exact risk labels. |
| Approaching expiry | Relative expiry fixtures and presentation helper provide near/imminent states. | Candidate match | Add deterministic threshold tests and exact timestamp access. |
| Blocked/incomplete evidence | `apr-2026-003` remains Pending with Blocked review progress and missing evidence. | Candidate match | Confirm state/facet separation and approval gating. |
| Clarification requested | `apr-2026-002` uses Awaiting information plus simulated activity. | Candidate match | Clarification provenance currently says `policy owner`, which must be checked against the trusted internal-source rule. |
| Approved, Rejected, Expired, Cancelled, and Indeterminate examples | History fixtures and focused collection/detail tests contain these states/outcomes. | Candidate match with automated evidence | Retain final visual evidence capture. |
| Long agent, policy, and action values | No deliberately long stress fixture is evident. | No candidate found | Add safe long-content fixtures and responsive evidence. |
| No-data, filtered-empty, loading, and recoverable-error states | Component inputs can deterministically render these states. | Candidate match | Add tests and current-design screenshots; do not ship a debug switcher. |
| Step-up-required example | Critical and High fixtures activate the simulated step-up boundary. | Candidate match | Add explicit coverage for both risk levels. |
| Deterministic time strategy | Fixtures derive timestamps relative to load time. | Partial candidate | Tests need a controlled reference clock for expiry thresholds and exact assertions. |

## Step 7 - Dialogs, accessibility, and responsive behavior

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Accessible dialog title and description | Shared Radix wrapper and decision dialog provide both. | Candidate match | Expand tests beyond one name assertion. |
| Focus containment, restoration, and Escape | Radix supplies the behavior; Escape has one focused test. | Partial candidate | Add focus-containment/restoration tests and manual keyboard evidence. |
| Unambiguous primary and destructive actions | Buttons use explicit simulated labels and destructive styling for rejection. | Candidate match | Confirm focus order and 200% zoom. |
| Dynamic outcome and validation announcements | Validation uses `role=alert`. | Partial candidate | The post-decision state/activity update has no explicit live-region behavior. |
| State, urgency, risk, availability, and errors never rely on color alone | StatusBadge, RiskChip, ReviewProgressTag, ExpiryLabel, icons, and visible explanations provide candidate evidence. | Candidate match | Verify every state in both themes and with assistive semantics. |
| 320 px reflow, mobile cards, sticky controls, and touch targets | Mobile card fallback and fixed decision bar exist. | Manual verification required | Review 320/375 px, 200% zoom, safe-area spacing, and no document overflow. |
| Long content and reduced-motion behavior | Shared layout and Radix primitives may support these cases. | Manual verification required | Add stress fixtures; inspect wrapping, focus, motion, and dialog usability. |

## Step 8 - Automated verification

| Required coverage | Existing alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Search, multiple filters, sort, reset, and URL context | One test covers search, Risk, and Clear filters. | Partial candidate | Add multiple-filter, every-sort, URL restoration, direction, page, and Back/Forward coverage. |
| Queue/History distinction | Focused tests cover History selection, direct URL restoration, decision metadata, default/reversed decision-time ordering, terminal detail, and return context. | Candidate match with automated and browser evidence | Retain final keyboard and assistive-technology review. |
| Row/card navigation and return context | No focused test found. | No candidate found | Add collection-to-detail and full return-context tests. |
| Loading, error, no-data, filtered-empty | No focused test found. | No candidate found | Add deterministic state tests. |
| Approve, reject, clarification, and reason rules | Low/High/Critical approval, rejection, required clarification question, step-up, refresh, session-only state, live announcement, and expired-during-review behavior are covered. | Candidate match with automated evidence | Retain final keyboard and screen-reader workflow review. |
| Unavailable, terminal, and Indeterminate detail | Missing-evidence, terminal read-only, unknown ID, controlled expiry, and Indeterminate states are covered; mobile Indeterminate guidance is in normal reading order. | Candidate match with automated and browser evidence | Retain final responsive and theme evidence capture. |
| Dialog accessibility | Accessible name, Escape, focus restoration, and bidirectional focus containment are covered. | Candidate match with automated evidence | Retain the final 200% zoom and browser keyboard review. |
| Agent Details deep links | No focused test found. | No candidate found | Add canonical fixture-link and empty-state tests. |
| Typecheck, lint, tests, and production build | These checks passed for pull request #9 and merged `main`. | Candidate match | Re-run after all WO-009 gap work; green commands alone do not satisfy missing coverage. |

### Dependency-free automation checkpoint

The owner-approved first automation round added coverage using the existing
Vitest and React Testing Library stack only. No dependency or testing framework
was introduced.

Current results on 2026-07-15:

- `npm run test`: 8 test files, 47 passing tests, no pending tests.
- `npm run typecheck`: pass.
- `npm run lint`: pass.
- `npm run build`: pass; all 13 application routes generated successfully.

Passing coverage now includes:

- core metadata search;
- evidence-source label search;
- combined Risk and Review filters plus reset;
- the owner-approved concise prototype filter contract;
- the view-specific History State filter, URL persistence, and reset behavior;
- matching, total, and deterministic near-expiry counts;
- supported URL-state restoration and updates;
- complete detail return context, including search, filters, sort direction,
  and page;
- component-level `popstate` restoration plus repeatable real-browser Back and
  Forward verification;
- Attention, Risk, Agent, Requested, Expiry, and Review sorting, including
  announced direction;
- shared sortable-header behavior across Approvals and Agents;
- URL persistence and restoration of non-default sort direction;
- mobile-card preservation of state, risk, action, target, agent, identifier,
  requested time, expiry, and review/outcome context;
- finite local pagination;
- error, initial-empty, filtered-empty, and loading representations;
- Queue/History distinction and terminal/Indeterminate fixtures;
- direct History URL hydration without new browser console errors;
- History decision metadata in desktop rows, mobile cards, and terminal detail;
- newest-first History decision-time ordering and reversible Decided sorting;
- detail context, prototype boundaries, and canonical Agent links;
- Low-risk approval, High-risk approval, rejection, and clarification state
  transitions;
- incomplete-evidence gating;
- terminal read-only, unknown, and Indeterminate detail states;
- remount/reset behavior;
- dialog focus restoration;
- Agent Details canonical approval links and empty state;
- required clarification questions;
- semantic association between unavailable Decision regions and their evidence
  explanation;
- fictional Artifact relationship presentation;
- mobile Indeterminate investigation guidance;
- polite post-decision live announcements;
- controlled expired-during-review behavior; and
- bidirectional dialog focus containment.

No explicit pending test remains in the dependency-free WO-009 suite. This
does not complete a Definition of Done item: subjective visual acceptance,
durable evidence capture, hands-on assistive-technology review, and any
owner-level product amendments remain separate review work.

This checkpoint is automated evidence only. It does not complete a WO-009
Definition of Done item.

## Step 9 - Manual evidence and closure controls

| Required artifact | Candidate evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Desktop, tablet, mobile, light, and dark evidence | The selected design was manually reviewed during integration. | Manual verification required | Capture durable evidence for the current merged design; do not reuse superseded PR #8 screenshots. |
| Queue, History, rich detail, validation, step-up, unavailable, Indeterminate, loading, error, and empty states | Current components represent most of these states. | Manual verification required | Review and capture every required scenario in the selected design. |
| Keyboard-only and accessibility evidence | Radix and semantic controls provide candidate behavior. | Manual verification required | Record the complete keyboard workflow, focus behavior, announcements, and 200% zoom. |
| Responsive evidence and no overflow | Phase 1 reviewed several widths. | Manual verification required | Repeat the WO-009 matrix, including 320 px and controlled states. |
| Pull request link | PR #9 integrated the selected frontend; PR #8 remains open. | Partial candidate | Decide whether gap work uses an amended WO-009 PR or a follow-up governed PR. |
| Final implementation summary, final review, and completed checklist | No current-design WO-009 closure record exists. | No candidate found | Produce only after every prior step is confirmed and all gap work is merged. |

## 3. Review sequence and decision log

The review proceeds in order from Step 1 through Step 9. For each step:

1. Review the candidate evidence together.
2. Confirm whether the mapping is correct.
3. Choose whether a partial/no-match item requires implementation or an
   explicit Work Order amendment.
4. Implement and verify authorized gap work in a small decision-focused commit.
5. Record the evidence, but leave the Work Order checklist unchecked until the
   repository owner explicitly confirms the step.

### Confirmation record

| Step | Item | Owner decision | Scope of confirmation | Date |
| --- | --- | --- | --- | --- |
| Step 1 | 1. Canonical approval routes | Confirmed | The alternate design provides the required Queue, History, and Approval Detail route structure. This does not confirm collection-context preservation or complete WO-009 navigation behavior. | 2026-07-15 |
| Step 1 | 2. Fixture data | Confirmed | The approval fixtures are appropriately typed, fictional, local, and non-sensitive for the frontend prototype. This does not confirm complete fixture coverage or every WO-009 controlled state. | 2026-07-15 |
| Step 1 | 3. Local-only decision controller | Confirmed | Simulated approval decisions use an isolated local controller and are not connected to an operational service. This does not confirm refresh/reset behavior or the complete structural source boundary. | 2026-07-15 |
| Step 1 | 4. Refresh resets simulated state | Confirmed | Refreshing Approval Detail restores the canonical fictional fixture and removes the session-local simulated state and Activity entry. | 2026-07-15 |
| Step 1 | 5. Structural prototype boundary | Confirmed | The WO-009 approval implementation introduces no operational network, persistence, authentication, policy, audit, runtime, or execution capability. This finding is scoped to the WO-009 implementation surface. | 2026-07-15 |
| Step 2 | 1. URL state and browser history | Confirmed partial mapping | Direct Queue/History URLs restore the active view and selections update the URL, but `replaceState` prevents browser Back/Forward from replaying those view changes. Back/Forward preservation remains outstanding work. | 2026-07-15 |
| Step 2 | 2. Unknown Approval Detail behavior | Confirmed | Unknown approval IDs show a clear unavailable state inside the Atlas shell and provide a working return to Queue. This confirms behavior and basic clarity only, not full visual, responsive, theme, or accessibility acceptance. | 2026-07-15 |
| Step 2 | 3. Return with complete collection context | Confirmed partial mapping | Approval Detail preserves Queue versus History, but the return link discards search, filters, sort, direction, and page. Complete collection-context restoration remains outstanding work. | 2026-07-15 |
| Step 2 | 4. Agent Details approval links | Confirmed | Agent Details derives pending approval links from the shared canonical fixture collection, and agents without a matching pending fixture receive an appropriate empty state. Full visual acceptance remains pending. | 2026-07-15 |
| Step 3 | 1. Queue header and prototype disclosure | Confirmed by owner as designed | Keep the concise `Approvals` title and `Frontend prototype` marker without an additional explanatory disclosure while Atlas remains a single-operator prototype. Revisit explanatory disclosure during production-readiness review. No UI change is authorized now. | 2026-07-15 |
| Step 3 | 2. Queue and History result counts | Confirmed | The collection distinguishes matching-result counts from the total fixture count, and Queue separately reports records nearing expiry. | 2026-07-15 |
| Step 3 | 3. Search coverage | Confirmed partial mapping | Search covers core approval metadata but not evidence-source labels. Evidence-source search remains an outstanding WO-009 decision or implementation item. | 2026-07-15 |
| Review process | Automated functional evidence | Confirmed | Replace repetitive manual functional checks with dependency-free component tests; preserve subjective GUI review and propose browser/E2E infrastructure separately. | 2026-07-15 |
| Review process | Agent-owned repeatable verification | Confirmed | The agent performs every feasible automated, browser, responsive, theme, and structural accessibility check. The owner is asked only for subjective product decisions or evidence that cannot be established repeatably by the agent. | 2026-07-15 |
| Step 3 | 4. Queue filters | Confirmed by owner as designed | Risk and Review are the approved concise prototype filter set. State, Agent, Policy, and Expiry filters are deferred until production-scale needs justify them. | 2026-07-15 |
| Step 3 | 5. Collection sorting | Confirmed correction authorized and implemented | Approvals and Agents now share one sortable-header component. All supported Approval sorts honor and announce direction; non-default direction is URL-backed. Automated tests cover the correction, while manual responsive and assistive-technology review remains outstanding. | 2026-07-15 |
| Step 3 | 6. Active-filter summary chips | Confirmed by owner as designed | Keep active values visible in the Search, Risk, and Review controls with a single Clear filters action. Do not add duplicate removable chips for the concise prototype. Revisit chips if the filter set grows or becomes hidden behind a collapsed control. | 2026-07-15 |
| Step 3 | 7. Accessible desktop table structure | Confirmed through automated evidence | The Queue and History tables have accessible names and expose sort direction only on the active sortable column. Hands-on screen-reader and responsive verification remains outstanding for the final accessibility review. | 2026-07-15 |
| Step 3 | 8. Mobile approval-card context | Confirmed by owner after correction | Mobile cards preserve state, risk, action, target, agent, identifier, requested time, expiry, and review/outcome context. The owner accepted the current content and formatting after automated content coverage and a 320 px no-overflow check. Touch-target and accessibility evidence remain for the final review. | 2026-07-15 |
| Design direction | Navigation labels and Approvals icon consistency | Confirmed correction authorized and implemented | The compact rail and mobile drawer now show readable navigation labels. The Approvals page header and navigation use one shared icon source. This owner decision supersedes the earlier icon-only handoff convention. | 2026-07-15 |
| Step 2 / Step 3 | URL history, complete return context, and evidence-source search corrections | Verified through automated and browser evidence | Back/Forward restores supported collection state, detail links preserve the complete originating context, and evidence-source labels participate in search. These findings update the earlier partial mappings without marking a Definition of Done item complete. | 2026-07-15 |
| Step 5 | Repeatable Approval Detail and dialog gaps | Verified through automated and browser evidence | Required clarification questions, unavailable-region semantics, Artifact context, mobile Indeterminate guidance, live announcements, controlled expiry, and dialog focus containment now have executable evidence. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 4 | History decision context and ordering | Verified through automated and browser evidence | History now restores safely from its direct URL, exposes explicit decision time, reviewer, reason, outcome, and correlation context across desktop, mobile, and detail views, and defaults to newest decision first. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 4 | Concise History filter contract | Confirmed by owner and verified through automated evidence | History replaces the inapplicable Review-progress filter with terminal State while retaining Search and Risk. Reviewer, Agent, Action type, Decision date, Execution outcome, Environment, and Policy filters are deferred until production-scale needs justify them. No Definition of Done item is marked complete. | 2026-07-15 |

No WO-009 Definition of Done item has been marked complete.
