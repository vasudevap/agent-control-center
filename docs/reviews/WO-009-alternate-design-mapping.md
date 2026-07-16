# Work Order 009: Alternate Design Mapping

**Status:** Review Complete - Definition of Done Confirmed
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
Phase 2 page work remained paused during this review.

The review closed on 2026-07-16 after the repository owner confirmed the
remaining VoiceOver review and directed completion of the closure work. Earlier
table cells that say to retain a final review are chronological checkpoints;
they are superseded by the completed Step 9 evidence, the final current-`main`
quality run, and the
[WO-009 Implementation Report](./WO-009-human-approvals-implementation-report.md).

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
| Canonical Queue, History, and detail routes | `approvals/page.tsx`, `approvals-workspace.tsx`, and `[approvalId]/page.tsx` are covered by component and browser navigation evidence. | Candidate match with automated, browser, and owner evidence | No mapping gap remains. |
| Typed fictional fixtures | `approval-data.ts` defines typed records using canonical fictional agents, reserved `.example` contacts, and explicit local provenance. | Candidate match with owner and source-review evidence | No mapping gap remains. |
| Frontend-only mutation boundary | `approval-prototype-controller.ts` accepts records and values only; the scoped structural scan found no service or persistence primitive. | Candidate match with source-review evidence | Repeat the scan if the approval feature later gains a data client. |
| Session-only, non-persistent simulation | Approval Detail disclosure and controller state are component-local; refresh/remount restoration is covered by automated and owner browser evidence. | Candidate match with automated, browser, and owner evidence | No mapping gap remains. |
| No backend, auth, runtime, policy, audit, or execution implementation | The recorded structural scan found no operational network, persistence, authentication, policy, audit, runtime, or execution dependency in the WO-009 surface. | Candidate match with source-review evidence | No mapping gap remains. |

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

Step 1 evidence is retained as source-review, automated, browser, and owner
confirmation evidence. It does not mark the Work Order complete.

## Step 2 - Information architecture and navigation

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| `/approvals` is canonical Queue destination | `ApprovalsWorkspace` defaults `view` to Queue, with URL and browser behavior covered. | Candidate match with automated and browser evidence | No mapping gap remains. |
| Queue and History are URL-backed sibling views | Tab state reads and writes the `view` query parameter; a `popstate` listener restores collection controls during Back/Forward navigation. | Candidate match with component and browser evidence | No mapping gap remains; retain final accessibility and responsive review. |
| `/approvals/[approvalId]` is canonical detail | Dynamic route resolves fixture IDs and renders a tested unavailable state for unknown IDs. | Candidate match with automated and browser evidence | Retain final keyboard review. |
| Return navigation preserves collection context | Detail reads a guarded `from` value, and row/card links now preserve view, search, Risk, Review, sort, direction, and page. | Candidate match with automated evidence | Verify the final detail-to-collection keyboard workflow during accessibility review. |
| Agent Details deep-links only canonical fixtures | Agent Detail derives links from the shared fixture set; focused tests cover linked and unlinked agents. | Candidate match with automated evidence | No mapping gap remains. |

## Step 3 - Queue experience

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Title, operational description, and persistent prototype disclosure | `PageHeader` uses the owner-approved concise `Approvals` title, an operational description, and a persistent `Frontend prototype` marker. | Owner-approved prototype amendment | Revisit explanatory disclosure during production-readiness review. |
| Visible count versus total | Results summary displays visible and total Queue counts plus nearing-expiry count, with filter-sensitive tests. | Candidate match with automated evidence | No mapping gap remains. |
| Approved full-text search fields | Search covers ID, agent ID/name, action, target, run, policy, and evidence-source labels. | Candidate match with automated evidence | No mapping gap remains. |
| State, risk, agent, policy, and expiry filters | Queue uses the owner-approved concise Search, Risk, and Review controls. State, Agent, Policy, and Expiry remain formally deferred until production scale justifies them. | Owner-approved prototype amendment | Revisit the deferred controls when collection scale or operator count increases. |
| Sortable attention, requested, expiry, risk, and agent values | Commit `6b21b33` introduced the controls; the reconciliation round corrected direction handling and added focused tests for every supported sort. | Candidate match with automated evidence | Complete the remaining manual responsive and assistive-technology review. |
| Active-filter summary with individual removal and Clear filters | Active values remain visible in the Search, Risk, and Review controls, and Clear filters resets the collection. | Owner-approved prototype amendment | Keep the concise toolbar without duplicate chips; revisit chips if filters become numerous or move behind a collapsed control. |
| Accessible semantic desktop table | The table now has a screen-reader caption and the active sortable header exposes `aria-sort`; inactive sortable headers omit it. | Candidate match with automated evidence | Complete manual screen-reader and responsive review. |
| Equivalent mobile card list | `ApprovalCard` replaces the table below `md` and preserves state, risk, action, target, agent, identifier, requested time, expiry, and review/outcome context. The owner visually accepted the current content and formatting after a 320 px no-overflow check. | Candidate match with automated and owner visual evidence | Complete touch-target and accessibility evidence during the final manual review. |
| URL-backed view, search, filters, sort, direction, and page | View, query, Risk, Review, sort, direction, and page are written to and restored from the URL for the owner-approved concise control set, including Back/Forward replay. | Candidate match for the approved prototype controls | State, Agent, Policy, and Expiry filters remain formally deferred by owner decision. |
| Finite local pagination | `PAGE_SIZE`, Previous/Next controls, boundary behavior, URL page restoration, and malformed/out-of-range page normalization have focused coverage. | Candidate match with automated evidence | No mapping gap remains. |
| Loading, error, no-data, and filtered-empty states | `presentationState` and `StateCard` cover all four representations with focused tests. | Candidate match with automated evidence | Retain final visual evidence capture. |
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
| Exact action, target, payload summary, effect, and scope | Every local fixture models a distinct payload summary. Approval Detail presents it as a full-width, wrapping field alongside action, target, consequence, scope, and environment, and repeats it in the simulated-decision confirmation. | Candidate match with automated evidence | Retain final responsive and assistive-technology review. |
| Policy and governance rationale | Dedicated divided card presents policy and review rationale; all detail values use breakable wrapping and stress coverage includes a long policy reference. | Candidate match with automated evidence | Retain final visual evidence capture. |
| Evidence separated from untrusted content | System metadata, untrusted preview, and missing-evidence alert are visually separated. | Candidate match | Verify accessible association and inert rendering. |
| Related Agent, Run, and Artifact treatment | Agent links canonically; Run is visibly unavailable; optional fictional Artifact metadata is modeled and displayed with an explicit unavailable-in-prototype treatment. | Candidate match with automated evidence | Extend fixture variety only if later Artifact-page work requires it. |
| Activity timeline with `Simulated` labeling | Activity renders simulated entries with an explicit badge. | Candidate match | Test clarification and approval activity, not rejection only. |
| Accessible Approval-unavailable explanation | Missing evidence appears visibly, and every rendered Decision region references the canonical explanation through `aria-describedby`. | Candidate match with automated and browser evidence | Retain final assistive-technology review. |
| Reason behavior for approve, reject, and clarification | Reject and High/Critical approve require text; Low/Medium approve is optional; clarification requires a question. | Candidate match with automated evidence | Retain final keyboard and announcement review. |
| Confirmation restates approval and outcome | All three dialogs restate ID, action, target, payload summary, consequence, risk, expiry, and the requested simulated outcome, with focused coverage. | Candidate match with automated evidence | Retain final keyboard and screen-reader review. |
| Simulated step-up for Critical and applicable High risk | Controller and dialog require the acknowledgement for all High/Critical fixtures. | Candidate match | Confirm which High-risk policies should require it and test both required and non-required boundaries if applicable. |
| Indeterminate treatment is distinct, blocks Retry, and directs investigation | Desktop and mobile flows label Indeterminate, block Retry, and direct the operator to investigate evidence before refreshing or returning. | Candidate match with automated and browser evidence | Retain final assistive-technology review. |
| Historical approvals are read-only | Non-Pending records disable decision paths; focused tests and responsive browser evidence cover terminal detail behavior. | Candidate match with automated and browser evidence | Retain final assistive-technology review. |

## Step 6 - Fixtures and controlled states

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Low, Medium, High, and Critical pending approvals | Queue fixtures cover all four risk levels. | Candidate match | Confirm default ordering and exact risk labels. |
| Approaching expiry | Relative expiry fixtures and the presentation helper provide near/imminent states; pure tests cover none, expired, imminent, nearing, and scheduled thresholds against a fixed clock. | Candidate match with automated evidence | No mapping gap remains. |
| Blocked/incomplete evidence | `apr-2026-003` remains Pending with Blocked review progress and missing evidence. | Candidate match | Confirm state/facet separation and approval gating. |
| Clarification requested | `apr-2026-002` uses Awaiting information and records the fictional authenticated `Prototype reviewer` as the requesting actor. No returned clarification is accepted from an untrusted source. | Candidate match with source-review evidence | Retain final activity-timeline review. |
| Approved, Rejected, Expired, Cancelled, and Indeterminate examples | History fixtures and focused collection/detail tests contain these states/outcomes. | Candidate match with automated evidence | Retain final visual evidence capture. |
| Long agent, policy, and action values | Controlled test fixtures exercise long unbroken identifiers, agent names, actions, policies, and payloads across collection and detail surfaces; shared fields use explicit breakable wrapping. | Candidate match with automated evidence | Retain final 200% zoom review. |
| No-data, filtered-empty, loading, and recoverable-error states | Component inputs deterministically render all four states with focused coverage; no debug switcher ships. | Candidate match with automated evidence | Retain final visual evidence capture. |
| Step-up-required example | Critical and High fixtures activate the simulated step-up boundary, with focused coverage across approval and rejection paths. | Candidate match with automated evidence | No mapping gap remains. |
| Deterministic time strategy | Presentation helpers accept an explicit reference clock; fixed-clock tests cover threshold classification and relative labels, and decision confirmation uses an injected clock for expiry-at-confirmation behavior. | Candidate match with automated evidence | No mapping gap remains. |

## Step 7 - Dialogs, accessibility, and responsive behavior

| WO-009 requirement | Candidate alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Accessible dialog title and description | Shared Radix wrapper and decision dialogs provide both, with focused accessible-name coverage. The owner confirmed the title, prototype description, reason field, step-up control, and decision actions are understandable through VoiceOver. | Candidate match with automated, browser, and owner evidence | No mapping gap remains; this does not complete a Definition of Done item. |
| Focus containment, restoration, and Escape | Focused tests cover Escape, trigger restoration, and bidirectional containment. A browser check exposed and then verified the correction of page-level focus restoration for the ordinary decision buttons used by Approval Detail. The owner confirmed the VoiceOver Escape workflow returns to `Simulate approval`. | Candidate match with automated, browser, and owner evidence | No mapping gap remains; this does not complete a Definition of Done item. |
| Unambiguous primary and destructive actions | Buttons use explicit simulated labels and destructive styling for rejection. The confirmation footer remains reachable through the dialog's internal scroll region at a 200%-equivalent reflow viewport, and the owner confirmed its VoiceOver output. | Candidate match with browser and owner evidence | No mapping gap remains; this does not complete a Definition of Done item. |
| Dynamic outcome and validation announcements | Validation uses `role=alert`; post-decision and expiry-at-confirmation outcomes use polite status announcements with focused tests. | Candidate match with automated evidence | Retain final screen-reader evidence. |
| State, urgency, risk, availability, and errors never rely on color alone | StatusBadge, RiskChip, ReviewProgressTag, ExpiryLabel, icons, and visible explanations provide candidate evidence. | Candidate match | Verify every state in both themes and with assistive semantics. |
| 320 px reflow, mobile cards, sticky controls, and touch targets | Mobile card fallback and fixed decision bar have browser no-overflow evidence at narrow widths; tall dialogs remain viewport-contained and internally scrollable. A 640-by-400 CSS-pixel viewport was used as the layout equivalent of 200% zoom on a 1280-by-800 display. Queue, History, pending detail, terminal detail, and Indeterminate detail produced no document overflow. The visible search hit area was corrected from 20 px to 34 px, leaving no visible form control below 24 CSS pixels in the audited Queue. Current production captures preserve the mobile card and fixed decision-control layouts. | Candidate match with browser, automated, and durable visual evidence | No mapping gap remains; this does not complete a Definition of Done item. |
| Long content and reduced-motion behavior | Controlled stress fixtures cover long collection/detail content and tall dialog usability. The scoped source scan found only short color transitions in the approval collection and no spatial, continuous, or essential motion. The 200%-equivalent browser audit kept long-content pages and the internally scrolling dialog free of document-level horizontal overflow. | Candidate match with automated, source-review, browser, and durable visual evidence | No mapping gap remains; this does not complete a Definition of Done item. |

## Step 8 - Automated verification

| Required coverage | Existing alternate-design evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Search, multiple filters, sort, reset, and URL context | Focused tests cover combined filters, view-specific filters, every supported sort, reset, URL restoration, direction, pagination, and Back/Forward replay. | Candidate match with automated and browser evidence | No mapping gap remains. |
| Queue/History distinction | Focused tests cover History selection, direct URL restoration, decision metadata, default/reversed decision-time ordering, terminal detail, and return context. | Candidate match with automated and browser evidence | Retain final keyboard and assistive-technology review. |
| Row/card navigation and return context | Focused tests cover canonical row/card links and complete encoded collection return context. | Candidate match with automated evidence | Retain final keyboard and touch navigation review. |
| Loading, error, no-data, filtered-empty | Focused tests cover every deterministic collection state. | Candidate match with automated evidence | Retain final visual evidence capture. |
| Approve, reject, clarification, and reason rules | Low/High/Critical approval, rejection, required clarification question, step-up, refresh, session-only state, live announcement, and expired-during-review behavior are covered. | Candidate match with automated evidence | Retain final keyboard and screen-reader workflow review. |
| Unavailable, terminal, and Indeterminate detail | Missing-evidence, terminal read-only, unknown ID, controlled expiry, and Indeterminate states are covered; mobile Indeterminate guidance is in normal reading order. | Candidate match with automated and browser evidence | Retain final responsive and theme evidence capture. |
| Dialog accessibility | Accessible name, Escape, focus restoration, and bidirectional focus containment are covered. Approval Detail now explicitly returns focus to the ordinary decision button that opened its controlled dialog; the regression test, browser Escape workflow, and owner VoiceOver confirmation pass. | Candidate match with automated, browser, and owner evidence | No mapping gap remains; this does not complete a Definition of Done item. |
| Agent Details deep links | Focused tests cover canonical fixture links and the no-approval empty state. | Candidate match with automated evidence | No mapping gap remains. |
| Typecheck, lint, tests, and production build | These checks passed for pull requests #9, #10, and #12 and were rerun from current `main` for final closure. | Complete | No verification gap remains. |

### Dependency-free automation checkpoint

The owner-approved first automation round added coverage using the existing
Vitest and React Testing Library stack only. No dependency or testing framework
was introduced.

Current results on 2026-07-15:

- `npm run test`: 10 test files, 58 passing tests, no pending tests.
- `npm run typecheck`: pass.
- `npm run lint`: pass.
- `npm run build`: pass; all 13 application routes generated successfully.

Final closure results on current `main` on 2026-07-16:

- `npm run typecheck`: pass.
- `npm run lint`: pass.
- `npm run test`: 10 test files, 58 passing tests, no pending tests.
- `npm run build`: pass; all 13 application routes generated successfully.
- The final scoped source scan found no operational network, persistence,
  authentication, runtime, policy, audit, or execution primitive in the WO-009
  implementation surface. The only URL constructor matches were localhost-only
  test assertions.

Passing coverage now includes:

- core metadata search;
- evidence-source label search;
- combined Risk and Review filters plus reset;
- the owner-approved concise prototype filter contract;
- the view-specific History State filter, URL persistence, and reset behavior;
- matching, total, and deterministic near-expiry counts;
- a canonical approaching-expiry fixture in the normal Queue rather than only
  a test-local override;
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
- normalization of malformed and out-of-range pagination URLs;
- error, initial-empty, filtered-empty, and loading representations;
- Queue/History distinction and terminal/Indeterminate fixtures;
- direct History URL hydration without new browser console errors;
- server-validated detail return context without hydration-dependent URL reads
  or production hydration warnings;
- collection-aware Approval Detail return labels for Queue and History;
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
- explicit local payload summaries in detail and decision confirmation, including long-content wrapping;
- viewport-contained, internally scrolling tall dialogs at desktop and mobile sizes;
- mobile Indeterminate investigation guidance;
- polite post-decision live announcements;
- controlled expired-during-review behavior;
- fixed-clock expiry thresholds and relative-time labels;
- long identity, identifier, action, policy, and payload wrapping;
- governed-context restatement across all three decision dialogs;
- bidirectional dialog focus containment; and
- Approval Detail focus restoration to the exact decision button used to open
  its controlled dialog.

The 200%-equivalent browser checkpoint also verified:

- Queue, History, pending detail, terminal detail, and Indeterminate detail at
  a 640-by-400 CSS-pixel viewport with no document-level horizontal overflow;
- the Critical approval dialog contained within the viewport with internal
  scrolling for its complete payload, step-up, reason, and action content;
- keyboard Escape dismissal returning focus to `Simulate approval`;
- light- and dark-theme rendering without page-level overflow; and
- no visible Queue form control below 24 CSS pixels after expanding the shared
  search input's actual hit area to fill its visible field.

No explicit pending test remains in the dependency-free WO-009 suite. This
does not complete a Definition of Done item: the governed review decision and
checklist closure remain separate review work.

This checkpoint is automated evidence only. It does not complete a WO-009
Definition of Done item.

## Step 9 - Manual evidence and closure controls

| Required artifact | Candidate evidence | Preliminary mapping | Outstanding review |
| --- | --- | --- | --- |
| Desktop, tablet, mobile, light, and dark evidence | Current-design production captures cover desktop, tablet, mobile, light, and dark presentations without development tooling overlays. The owner accepted the selected visual direction. | Complete with durable visual and owner evidence | No closure gap remains; superseded PR #8 screenshots are excluded. |
| Queue, History, rich detail, validation, step-up, unavailable, Indeterminate, loading, error, and empty states | The production evidence set covers every listed scenario, including filtered-empty as a separate collection state. The owner accepted the current formatting, hierarchy, spacing, readability, and GUI direction. | Complete with durable visual and owner evidence | No closure gap remains. |
| Keyboard-only and accessibility evidence | Automated tests cover focus containment, restoration, Escape, accessible names, and live regions. Browser evidence verifies page-level Escape dismissal and exact trigger focus restoration at the 200%-equivalent viewport. The owner completed the VoiceOver review. | Complete with automated, browser, and owner evidence | No closure gap remains. |
| Responsive evidence and no overflow | The 320 px audit and the 640-by-400 200%-equivalent audit found no document-level overflow across Queue, History, pending detail, terminal detail, or Indeterminate detail. Current production screenshots cover 1440, 768, and 375 px evidence, and the owner accepted the responsive visual direction. | Complete with browser, durable visual, and owner evidence | No closure gap remains. |
| Pull request link | PR #9 integrated the selected frontend, PR #10 merged the reconciliation and gap corrections, and PR #12 merged the post-verification hydration correction. Superseded PR #8 is obsolete. | Complete | No closure gap remains. |
| Final implementation summary, final review, and completed checklist | The final implementation report records scope, conformance, validation, evidence, limitations, rollback, and closeout; the Work Order checklist is complete. | Complete | Closed after all gap work merged, the owner completed the remaining VoiceOver review, and the current-main quality suite passed. |

### Current-design production evidence

These files were captured from a production build of the current PR #10 branch.
The controlled loading, error, and empty presentations were exposed only during
the local evidence session through the component's existing presentation-state
input; no debug route or state switcher remains in the product source.

| Scenario | Evidence |
| --- | --- |
| Filtered Queue, Critical risk, Unopened review, approaching expiry, desktop light | [1440 px Queue](./assets/wo-009-queue-desktop-1440-light-filtered.png) |
| History, desktop dark | [1440 px History](./assets/wo-009-history-desktop-1440-dark.png) |
| History, tablet light | [768 px History](./assets/wo-009-history-tablet-768-light.png) |
| Queue mobile-card fallback, mobile light | [375 px Queue](./assets/wo-009-queue-mobile-375-light.png) |
| Rich Critical Approval Detail, desktop light | [1440 px detail](./assets/wo-009-detail-critical-desktop-1440-light.png) |
| Critical Approval Detail and fixed decision controls, mobile dark | [375 px detail](./assets/wo-009-detail-critical-mobile-375-dark.png) |
| Rejection validation plus simulated step-up, tablet dark | [768 px confirmation](./assets/wo-009-rejection-validation-step-up-tablet-768-dark.png) |
| Approval-unavailable explanation and disabled Approve | [1440 px unavailable detail](./assets/wo-009-detail-approval-unavailable-desktop-1440-light.png) |
| Indeterminate execution guidance, mobile light | [375 px Indeterminate detail](./assets/wo-009-detail-indeterminate-mobile-375-light.png) |
| Controlled loading state | [768 px loading](./assets/wo-009-queue-loading-tablet-768-light.png) |
| Controlled recoverable error state | [768 px error](./assets/wo-009-queue-error-tablet-768-light.png) |
| Controlled initial-empty state | [768 px empty](./assets/wo-009-queue-empty-tablet-768-light.png) |
| Filtered-empty recovery state | [768 px filtered empty](./assets/wo-009-queue-filtered-empty-tablet-768-light.png) |

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
| Step 5 | Proposed payload summary | Confirmed by owner and verified through automated evidence | Every fictional approval now declares a payload summary. Detail and final simulated-decision confirmation present it in a full-width wrapping field so the operator can inspect what would be authorized. No service connection or Definition of Done completion was introduced. | 2026-07-15 |
| Step 5 / Step 7 | Payload dialog viewport correction | Verified through automated and browser evidence | Adding payload context exposed excessive dialog height. The shared dialog now remains inside desktop and mobile viewports and scrolls internally; focused component coverage guards the constraint. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 6 / Step 8 | Deterministic timing and long-content stress coverage | Verified through automated, source-review, and browser evidence | Fixed-clock tests cover all expiry urgency thresholds and relative labels. Controlled fixtures exercise long identifiers, agents, actions, policies, and payloads; constrained viewports retain internal dialog scrolling without document overflow. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 7 / Step 9 | 200%-equivalent reflow, touch targets, and focus restoration | Verified through automated, browser, owner, and durable visual evidence | Queue, History, and representative detail states have no document-level overflow at the 200%-equivalent viewport. The shared search input's actual hit area fills its visible field, Approval Detail returns focus to the exact decision button after Escape, the owner confirmed VoiceOver operation, and the production evidence set covers the responsive tiers. Final owner acceptance and governed closure remain separate. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 7 / Step 9 | VoiceOver dialog workflow | Confirmed working by owner | VoiceOver communicates the simulated-decision dialog title, prototype boundary, required reason, step-up control, and actions; Escape returns focus to `Simulate approval`. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 6 / Step 9 | Canonical approaching-expiry fixture | Verified through automated and production-browser evidence | The normal Queue now includes a Critical request with `Nearing` expiry rather than requiring a test-only override. A regression test guards the representative fixture. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 2 / Step 9 | Hydration-safe return context | Verified through automated and production-browser evidence | Approval Detail receives the validated collection return path from its server page. A direct History detail load renders the History return link without hydration warnings or browser console errors. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 9 | Durable current-design evidence set | Captured through production-browser evidence | Thirteen current-design images cover the required responsive tiers, themes, core workflows, validation/step-up, unavailable/Indeterminate states, and controlled collection states. Governed closure remains separate. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 9 | Final visual-direction acceptance | Confirmed by owner | The owner accepted the current Queue, History, and Approval Detail formatting, visual hierarchy, spacing, readability, responsive presentation, themes, and overall GUI as the frontend direction Atlas should retain. This records subjective design acceptance only; governed review and all Definition of Done decisions remain separate. | 2026-07-15 |
| Governed self-review | Navigation and pagination corrections | Identified and corrected during review | Approval Detail now labels History return navigation accurately, and collection pagination normalizes malformed or out-of-range URL values before rendering controls or encoding detail return context. Regression coverage passes. No Definition of Done item is marked complete. | 2026-07-15 |
| Post-merge verification | Overview approval-expiry hydration | Defect identified and corrected on a governed follow-up branch | The Overview client previously imported relative-time approval fixtures directly, allowing server and browser module evaluation to produce different expiry timestamps. Overview now creates the fixtures on the server and passes the exact serialized approvals into `AttentionQueue`. A component regression test and a fresh-browser load confirm the attention queue renders with no warning or error logs. No Definition of Done item is marked complete. | 2026-07-15 |
| Step 7 / Step 9 | Remaining VoiceOver review | Confirmed working by owner | The owner confirmed the remaining VoiceOver review complete and accepted the accumulated automated, browser, and hands-on accessibility evidence. | 2026-07-16 |
| Closure | Consolidated WO-009 implementation | Confirmed by owner and final evidence | The owner directed completion after confirming the implementation had already been reviewed and tested. The current-main quality suite and scoped safety scan passed, and the final implementation report records conformance and closure. | 2026-07-16 |

All WO-009 Definition of Done items are complete. Earlier statements that no
item was complete describe the state at those historical checkpoints.
