# Work Order 006 — Agents Inventory

**ID:** AGENTS-006
**Status:** Draft — Pending Readiness Approval
**Priority:** P0
**Owner:** Frontend Implementation
**Review Owner:** Product Owner and Design Director
**Architecture Review:** Required
**Design Review:** Required
**Security/Privacy Review:** Required
**Implementation Authorization:** Not granted until the Readiness Gate is approved

---

## Objective

Replace the `/agents` placeholder with a production-quality Agents Inventory that enables an operator to identify every mock agent, understand its current operational state, search and filter the inventory, and navigate to the existing Agent Details route.

This Work Order establishes the canonical Atlas collection-screen pattern without introducing backend integration, authentication, persistence, or state-changing agent operations.

---

## Intended Outcome

An operator can answer:

> Which agents exist, and what is their current operational state?

The screen must make agent identity, status, health, ownership, recent activity, upcoming activity, and version immediately scannable.

---

## Governing References

### Repository and Governance

- `AGENTS.md`
- `PROJECT.md`
- `ROADMAP.md`
- `.claude/CLAUDE.md`
- `docs/governance/engineering-governance.md`
- `docs/governance/definition-of-ready.md`
- `docs/governance/definition-of-done.md`
- `docs/governance/branching-strategy.md`
- `docs/governance/pull-request-and-review-process.md`

### Architecture

- `docs/architecture/02-architecture-principles.md`
- `docs/architecture/04-container-architecture.md`, Section 5
- `docs/architecture/05-component-architecture.md`, Section 4.4
- `docs/architecture/07-security-architecture.md`
- `docs/architecture/08-data-architecture.md`
- `docs/architecture/12-technology-strategy.md`, Sections 4 and 25

### Product and Design

- `docs/specifications/product-requirements.md`, Sections 9.1, 12.2, 12.3, 13.1, 13.6, 13.7, and 13.10
- `docs/design/01-design-principles.md`
- `docs/design/02-product-domain-model.md`
- `docs/design/03-information-architecture.md`
- `docs/design/04-user-experience.md`
- `docs/design/07-design-system.md`
- `docs/design/08-component-library.md`
- `docs/design/09-screen-specifications-overview.md`, Section 2
- `docs/design/11-developer-handoff.md`
- `docs/design/decisions/DDR-001-typography-direction.md`
- `docs/design/decisions/DDR-002-visual-language-direction.md`

### Implementation Baseline

- Work Order 005 Application Shell
- `apps/web/src/app/(shell)/agents/page.tsx`
- Existing shared shell, page-header, search-field, table, status-badge,
  empty-state, error-state, skeleton, button, and layout components

Recommendations under `docs/recommendations/` remain advisory unless this Work Order explicitly adopts a behavior.

---

## Design Authority

When this Work Order passes the Readiness Gate, it becomes the authoritative
screen specification for the `/agents` inventory only.

Where draft design documentation conflicts with this Work Order, this Work
Order governs for that screen. In particular, agent registration, bulk actions,
Run, Pause, Disable, and other state-changing operations are excluded from this
milestone.

The approved Work Order 005 application shell, existing Atlas design tokens,
shared components, DDR-001, and DDR-002 remain the implementation baseline.
Approval of this Work Order does not ratify unrelated sections of the draft
design-system, component-library, screen-specification, or developer-handoff
documents.

This section does not grant implementation authorization while the Work Order
status remains `Draft — Pending Readiness Approval`.

---

## Readiness Prerequisites

Implementation may begin only after:

1. The review owner ratifies the applicable design-system, component-library,
   screen-specification, and developer-handoff documents, or approves this Work
   Order as the authoritative Agents screen specification.
2. The automated frontend testing gap is resolved through a separately approved
   Engineering Specification (`ES-002 — Frontend Testing Infrastructure`) or a
   documented temporary manual-testing exception with an owner and revisit trigger.
3. The Product Owner and Design Director approve the field hierarchy,
   responsive behavior, state behavior, and exclusion of state-changing actions.
4. The Work Order status is changed to `Ready`.
5. A short-lived branch is created from current synchronized `main`.

---

## Approved Scope

### Route

Replace the placeholder content at:

`/agents`

Preserve the Work Order 005 application shell and route structure.

### Page Header

Display:

- Title: `Agents`
- Description: `Monitor the status, health, and activity of your AI workforce.`

Do not include Register Agent, Run Agent, or other state-changing header actions.

### Inventory Controls

Provide:

- Search by agent name, description, or agent ID
- Status filter
- Health filter
- Clear-filters action when filters are active
- Visible result count
- Client-side filtering of local mock data only

Search must be case-insensitive and update the visible inventory without navigation or persistence.

### Default Ordering

Order agents by operational attention:

1. Agents with a current issue
2. Degraded or offline agents
3. Running agents
4. Remaining agents alphabetically by name

Do not introduce user-configurable sorting unless approved as a refinement.

### Agent Information

Each agent record must include:

- Agent ID
- Name
- Description
- Lifecycle status
- Health
- Owner
- Last run
- Next run
- Version
- Current issue, when present

Use realistic fictional data only.

Do not include personal data, credentials, secrets, external account identifiers, real email content, or real organization names.

### Desktop Presentation

At desktop widths, use an operational table with these visible columns:

1. Agent
   - Name
   - Short description
2. Status
3. Health
4. Owner
5. Last Run
6. Next Run
7. Version

A current issue must be exposed within the Agent cell or an accessible supporting treatment without adding a separate visually dominant column.

Agent name must be the primary link to `/agents/[agentId]`.

### Tablet Presentation

At tablet widths:

- Preserve the table.
- Prioritize Agent, Status, Health, Last Run, and Next Run.
- Owner and Version may be hidden from the visual table if they remain available through the linked detail route.
- Avoid horizontal page overflow.
- Do not reduce text below approved token sizes.

### Mobile Presentation

At mobile widths:

- Transform each row into a stacked agent summary using existing card, badge, and typography patterns.
- Show Name, Description, Status, Health, Last Run, Next Run, and Current Issue.
- The entire summary may link to Agent Details if it has a clear accessible name.
- Do not reproduce a compressed desktop table.
- Do not expose state-changing quick actions.

Mobile supports monitoring and investigation, consistent with the approved Atlas responsive strategy.

---

## Screen States

### Populated

Show the filtered inventory and result count.

### Initial Empty

When no agents exist, explain:

- what an agent is in this context;
- that registered agents will appear here;
- that registration is not available in this frontend-only milestone.

Do not show a non-functional primary action.

### Filtered Empty

When agents exist but no result matches:

- State that no agents match the current search or filters.
- Provide a working Clear Filters action.
- Preserve the user's entered criteria until cleared.

### Loading

Provide a layout-stable, screen-specific skeleton representing the controls and inventory. Do not use a blocking spinner.

### Error

Provide an accessible screen-specific error state that explains that the inventory could not be displayed.

Because this milestone uses synchronous mock data, the state must be represented through a deterministic component interface suitable for later testing. Do not add a production-facing state switcher or query parameter solely for demonstration.

### Disabled

No state-changing agent controls are present, so a disabled action state is not applicable.

---

## Interaction Requirements

- Search and filters must be keyboard operable.
- Filter labels must remain visible or programmatically associated.
- Clearing filters must restore the complete mock inventory.
- Agent links must support normal browser navigation, history, and deep linking.
- Focus must remain visible.
- Filter changes must not unexpectedly move focus.
- Status and health must never rely on color alone.
- No destructive or privileged operation may be simulated.

---

## Accessibility Requirements

Target WCAG 2.2 AA.

Required:

- Semantic page heading hierarchy
- Semantic table markup on desktop/tablet
- Accessible names for every search, filter, and navigation control
- Keyboard access to all controls and agent links
- Visible focus indicators
- Screen-reader-readable status and health labels
- Sufficient light- and dark-theme contrast
- No color-only state communication
- Logical focus and reading order
- Touch targets consistent with the approved component library
- Responsive text without clipping at 200% browser zoom
- No horizontal page overflow at 375px

---

## Theme Requirements

- Support approved light and dark themes.
- Use approved semantic design tokens only.
- Do not introduce hard-coded visual colors, spacing, typography, radius, or shadow values.
- Preserve Inter and JetBrains Mono usage defined by DDR-001.
- Preserve the restrained editorial enterprise language defined by DDR-002.

---

## Security and Privacy

- Use local, static, fictional mock data only.
- Do not add API clients, fetch calls, server actions, environment variables, credentials, cookies, local storage, or persistence.
- Do not make authorization decisions in the browser.
- Do not expose secrets, tokens, personal data, real operational identifiers, or sensitive connector information.
- Treat descriptions and issue text as untrusted display content: render as text, not HTML.
- State-changing agent actions remain excluded because backend authorization, audit, idempotency, and confirmation controls do not exist.
- No new trust boundary is introduced.

---

## Dependencies

### Required

- Completed Work Order 005 application shell
- Existing Next.js App Router and TypeScript configuration
- Existing Atlas design tokens and shared components
- Approved Agents screen behavior
- Accepted `ADR-001 — Frontend Component Testing`
- Approved and completed `ES-002 — Frontend Testing Infrastructure`, or an
  approved temporary manual-testing exception

### Not Required

- Backend
- Agent Registry API
- Authentication
- Authorization
- Database
- Data persistence
- Deployment changes
- New architecture or ADR

---

## Out of Scope

- Agent registration or creation
- Editing agent configuration
- Run Now
- Activate, pause, disable, or archive
- Bulk selection or bulk actions
- Schedule creation or editing
- Delete actions
- Real API integration
- Backend contracts
- Authentication or role filtering
- Persistence of filters or saved views
- Pagination
- Column customization
- Export
- Real-time updates or polling
- Agent Details implementation
- Changes to the Overview Dashboard
- Changes to the application shell
- New dependencies or framework adoption
- Storybook introduction unless separately approved
- General component-library redesign
- Unrelated dependency upgrades or advisory remediation

---

## Acceptance Criteria

1. `/agents` renders inside the approved Work Order 005 shell.
2. The placeholder page is replaced by a production-quality Agents Inventory.
3. All required mock-agent fields are represented in typed interfaces.
4. Realistic fictional data includes healthy, degraded, offline, active, paused, and issue-bearing examples.
5. Search matches agent name, description, and ID case-insensitively.
6. Status and health filters work independently and together.
7. Clear Filters restores the complete inventory.
8. The visible result count is accurate.
9. Default ordering prioritizes operational attention as specified.
10. Agent names navigate to the existing `/agents/[agentId]` route.
11. Desktop, tablet, and mobile behavior matches this Work Order.
12. Populated, initial-empty, filtered-empty, loading, and error states have deterministic component representations.
13. No state-changing or misleading non-functional agent action is exposed.
14. Light and dark themes remain visually correct.
15. Keyboard navigation and focus behavior pass manual review.
16. Status and health remain understandable without color.
17. No secrets, personal data, real external identifiers, or unsafe HTML are added.
18. No backend, API, authentication, persistence, architecture, or dependency change is introduced.
19. Existing routes and Work Order 005 shell behavior do not regress.
20. Required canonical documentation is updated in the same pull request if the approved screen specification or status changes.

---

## Verification Plan

### Automated Repository Validation

From the repository root:

- `npm ci`
- `npm run typecheck`
- `npm run lint`
- `npm run build`

If frontend test infrastructure is approved before implementation, run and record the canonical test command defined by that specification.

### Route Verification

Verify:

- `/agents`
- At least two `/agents/[agentId]` links using mock IDs
- All existing Work Order 005 routes still render

### Functional Verification

Verify:

- Search by name
- Search by ID
- Search by description
- Each status filter
- Each health filter
- Combined filters
- Clear Filters
- Filtered-empty recovery
- Agent-detail navigation
- Browser back navigation

### Responsive Verification

Capture and review:

- Desktop: 1440px
- Tablet: 768px
- Mobile: 375px
- 200% browser zoom

Confirm no clipping, inaccessible controls, or horizontal page overflow.

### Accessibility Verification

- Keyboard-only navigation
- Visible focus
- Heading and landmark structure
- Table semantics
- Control labels
- Link names
- Status text independent of color
- Light- and dark-theme contrast
- Screen-reader spot check of one desktop row and one mobile summary

### Visual Review

Provide light- and dark-theme screenshots at all three breakpoints.

Compare typography, spacing, borders, status treatment, and component usage against the approved Atlas design baseline.

---

## Review Requirements

The pull request must include:

- Link to Work Order 006
- Focused diff
- Scope and out-of-scope confirmation
- Architecture impact statement
- Product and UX impact statement
- Security and privacy impact statement
- Validation command results
- Test results or the approved temporary testing exception
- Desktop, tablet, and mobile screenshots in both themes
- Accessibility review evidence
- Route verification evidence
- Risks, limitations, and rollback notes
- Documentation updates
- Confirmation that no unrelated dependency changes are included

Required reviewers:

- Product Owner
- Design Director
- Architecture/security self-review by the repository maintainer

Required CI must pass before merge.

---

## Documentation Updates

When approved:

1. Update the Agents section of `docs/design/09-screen-specifications-overview.md` with the approved detailed behavior or explicitly link it to this Work Order.
2. Reconcile the status of the applicable design-system, component-library, screen-specification, and developer-handoff documents.
3. Add Work Order 006 to `docs/work-orders/README.md`.
4. Update `ROADMAP.md` when implementation is complete.
5. Create the final implementation and review record under `docs/reviews/`.
6. Record any accepted testing exception and its revisit trigger.

No architecture document or DDR should change unless review discovers an actual architecture or enduring design-language change.

---

## Risks and Mitigations

### Unapproved design authority

Mitigation: resolve document status before implementation authorization.

### Action controls implying nonexistent authority

Mitigation: exclude Run, Pause, Disable, Register, and bulk actions.

### Responsive table degradation

Mitigation: use a mobile summary layout rather than compressing the desktop table.

### Mock data becoming an accidental API contract

Mitigation: keep types feature-local and document them as presentation fixtures, not backend contracts.

### Insufficient regression coverage

Mitigation: approve frontend test infrastructure first or record a temporary manual-testing exception with a named owner and revisit trigger.

---

## Rollback

Rollback consists of reverting the Work Order 006 pull request, restoring the existing `/agents` placeholder while preserving the Work Order 005 application shell and all other routes.

No data migration, backend rollback, or external-system rollback is required.

---

## Approval Record

### Product and Design Approval

**Decision:** Approved
**Approved:** 2026-07-12
**Approved By:** Repository Maintainer acting as Product Owner and Design Director

The field hierarchy, operational-attention ordering, inventory controls,
responsive behavior, deterministic screen states, Agent Details navigation, and
exclusion of state-changing actions are approved. This Work Order is approved as
the authoritative screen specification for `/agents` under the scoped Design
Authority section.

### Architecture Review

**Decision:** Approved — no runtime architecture change
**Reviewed:** 2026-07-12
**Reviewed By:** Repository Maintainer

The Work Order uses the existing Next.js frontend, Work Order 005 application
shell, local typed presentation fixtures, and shared components. It introduces
no backend contract, persistence, authentication, authorization, deployment,
runtime framework, or trust-boundary change. ADR-001 governs the separate
development-time frontend testing framework; no additional ADR is required for
the Agents Inventory.

### Security and Privacy Review

**Decision:** Approved
**Reviewed:** 2026-07-12
**Reviewed By:** Repository Maintainer

The approved scope uses fictional local data, renders descriptions and issue
text as plain text, introduces no credentials or external identifiers, and
exposes no state-changing operation. The security and privacy constraints in
this Work Order are accepted.

### Readiness Condition

These approvals resolve the product, design, architecture, security, and privacy
review prerequisites. Final implementation authorization remains withheld until
ES-002 is merged and closed, the review owner confirms the Definition of Ready,
and this Work Order's status is changed to `Ready`.

---

## Readiness Decision

This Work Order contains the required scope, states, responsive behavior, accessibility, security/privacy constraints, dependencies, acceptance criteria, verification, review, and rollback requirements.

It remains `Draft — Pending Readiness Approval` until:

- design authority is ratified;
- the frontend testing gap is resolved or explicitly accepted;
- Product Owner and Design Director approve this Work Order; and
- the review owner changes its status to `Ready`.

Do not implement before that decision.
