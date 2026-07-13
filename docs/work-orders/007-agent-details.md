# Work Order 007 — Agent Details

**ID:** AGENTS-007
**Status:** Design Review Locked
**Priority:** P0
**Owner:** Frontend Implementation
**Review Owner:** Product Owner and Design Director
**Architecture Review:** Required
**Design Review:** Required
**Security/Privacy Review:** Required
**Implementation Authorization:** Granted

---

## Objective

Replace the existing `/agents/[agentId]` placeholder with a production-quality
Agent Details screen that lets an operator investigate one mock agent selected
from the Agents Inventory.

This work order extends the approved Work Order 006 collection pattern without
introducing backend integration, authentication, persistence, or state-changing
agent operations.

---

## Intended Outcome

An operator can answer:

> What is this agent responsible for, how healthy is it, and what needs attention?

The screen should provide enough detail to support investigation while keeping
the inventory screen scan-first and uncluttered.

---

## Governing References

- `AGENTS.md`
- `PROJECT.md`
- `ROADMAP.md`
- `docs/governance/engineering-governance.md`
- `docs/governance/definition-of-ready.md`
- `docs/governance/definition-of-done.md`
- `docs/governance/branching-strategy.md`
- `docs/governance/pull-request-and-review-process.md`
- `docs/work-orders/005-app-shell.md`
- `docs/work-orders/006-agents-inventory.md`
- `docs/design/07-design-system.md`
- `docs/design/08-component-library.md`
- `docs/design/09-screen-specifications-overview.md`

---

## Design Authority

When approved, this work order becomes the authoritative screen specification
for `/agents/[agentId]` only.

Work Order 006 remains authoritative for the Agents Inventory. The Agent Details
screen may expose technical identifiers, version information, full descriptions,
and deeper operational context that were intentionally removed from the
inventory presentation.

---

## Readiness Prerequisites

Implementation may begin because:

1. Product Owner approval of the detail-screen content hierarchy has been granted.
2. Design Director approval of the layout, visual hierarchy, and responsive
   behavior.
3. Architecture approval that the screen remains frontend-only and does not
   introduce new runtime boundaries.
4. Security and privacy approval of all mock data fields.
5. Implementation authorization is explicitly granted.

---

## Proposed Scope

### Route

Replace the placeholder content at:

`/agents/[agentId]`

Preserve the Work Order 005 application shell and navigation structure.

### Page Header

Display:

- Agent name
- Lifecycle status badge
- Health badge
- Back link to Agents Inventory

The header should not repeat the agent description, version, or technical ID
when those details are already available in the investigation cards below.

Run, pause, and resume controls are governed separately by Work Order 008. They
remain frontend prototype controls until runtime authorization, policy,
idempotency, audit, and persistence integration are implemented.

### Detail Content

Provide read-only sections for:

- Overview summary
- Operational status
- Current issue or attention state
- Ownership and responsibility
- Schedule and recent run timing
- Version and technical agent ID
- Capabilities
- Required connectors
- Required permissions
- Recent mock activity

Use realistic fictional data only.

### Locked Design Decisions

The product owner approved the current Agent Details design direction for this
milestone:

- The page header is a clean command header with agent name, icon, navigation,
  and operational prototype controls.
- Summary cards use the labels `Runs Completed`, `Automation Confidence`,
  `Operator Time Saved`, and `Approvals Required`.
- `Runs Completed` represents execution activity, not human review.
- `Approvals Required` is the highest-priority action signal for operators.
- `Automation Confidence` is the primary risk and quality signal.
- `Operator Time Saved` is retained as an estimated value signal.
- The configuration card is titled `Effective Configuration` and is visually
  read-only, not form-like.
- Effective configuration is presented as the currently approved registry
  snapshot with version and change-control context.

### Investigation Hierarchy

The screen should prioritize:

1. Current issue and health state
2. What the agent does
3. Who owns it
4. When it last ran and when it runs next
5. What it depends on
6. Technical metadata

### Responsive Behavior

Desktop should use a two-column investigation layout with a primary detail area
and a secondary metadata rail.

Tablet may collapse the metadata rail beneath the primary detail area.

Mobile should use stacked sections with no horizontal overflow and no compressed
desktop table.

---

## Out of Scope

- Backend data fetching
- Agent mutation actions
- Authentication or authorization changes
- Connector execution
- Live run history
- Editable agent configuration
- Real organization, person, email, account, token, or credential data

---

## Acceptance Criteria

- `/agents/[agentId]` renders a production-quality Agent Details screen for
  known mock agent IDs from the inventory.
- Unknown agent IDs render an appropriate not-found or unavailable state.
- Technical ID and version are available on the detail screen.
- No state-changing controls are exposed.
- The screen uses approved Atlas tokens, components, icons, and the locked light
  and dark mode surface hierarchy.
- Desktop, tablet, and mobile layouts remain readable without horizontal
  overflow.
- Mock data remains fictional and contains no secrets or personal data.
- Existing validation commands pass before PR review.

---

## Approval Checklist

- [x] Product approval
- [x] Design approval
- [x] Architecture approval
- [x] Security approval
- [x] Privacy approval
- [x] Implementation authorization
