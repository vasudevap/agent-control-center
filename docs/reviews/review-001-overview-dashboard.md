# Review 001: Overview Dashboard Implementation Plan

**Date:** 2026-07-10
**Reviewer:** Claude (Senior Product Designer & Frontend Engineer)
**Work Order:** 001-overview-dashboard.md
**Status:** Under Review

---

## Executive Summary

Work Order 001 requests an Overview Dashboard for Atlas—the unified control plane for AI workforce management. The dashboard is the centerpiece of the Atlas product and will serve as the primary interface for monitoring fleet health, active runs, pending approvals, alerts, and upcoming schedules.

The work order is **well-scoped and strategically important**, but lacks critical specificity around data structures, metrics definitions, and approval workflows. The documentation is strong on design principles but provides insufficient detail to begin implementation without assumptions that could lead to rework.

**Recommendation:** Approved with changes pending clarification of 10 specific questions and adoption of proposed design system enhancements.

---

## Readiness Assessment

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Design Direction** | ✅ Strong | Clear principles (Control, Trust, Clarity), modern infrastructure aesthetic |
| **Technology Stack** | ✅ Clear | React, Next.js, TypeScript, Tailwind, shadcn/ui—production-tested choices |
| **Component Taxonomy** | ✅ Defined | Sidebar, TopBar, MetricCard, Table, StatusBadge, AlertCard, Button |
| **Accessibility** | ✅ Targeted | WCAG 2.2 AA stated; ready for implementation |
| **Data Model** | ❌ **Missing** | No API contracts, endpoint structures, or data shapes defined |
| **Metrics Definition** | ❌ **Missing** | Unclear which KPIs belong in "Metric Cards" or "Fleet Health" |
| **Approval Workflow** | ❌ **Missing** | Single vs. multi-level? Metadata requirements? |
| **Real-Time Strategy** | ❌ **Missing** | Polling? WebSocket? Static refresh? |
| **Color System** | ⚠️ Incomplete | Typography clear; semantic colors not specified beyond status (green/yellow/red) |
| **Responsive Strategy** | ⚠️ Incomplete | Desktop-first stated; mobile breakpoints and tablet layout undefined |

**Readiness: 60/100.** Architecture is sound; execution cannot begin without data model clarity.

---

## Strengths

### 1. **Strong Design Principles**
The "Modern Infrastructure" direction and principles (Control, Trust, Clarity, Operational first) are enterprise-appropriate and will drive cohesive UX. This compares favorably to Linear and Stripe.

### 2. **Production-Ready Tech Stack**
Next.js, React, TypeScript, Tailwind, shadcn/ui, Radix, and Lucide form a mature, battle-tested foundation. No experimental technologies—appropriate for enterprise SaaS.

### 3. **Component-First Architecture**
The guidelines favor composition and reuse over duplication. This will reduce technical debt and maintenance burden over time.

### 4. **Accessibility-First Commitment**
WCAG 2.2 AA target from the start is enterprise-grade. Shows commitment to inclusive design.

### 5. **Design Token Framework**
8px spacing system, semantic colors, and token-based approach reduce inconsistency and enable scaling.

### 6. **Clear Folder Structure**
`features/` and `components/` separation supports modularity and scalability.

---

## Issues Found

### 🔴 Critical

**1. No Data Model Specification**
- Dashboard sections require specific data shapes (agents, runs, approvals, alerts, schedules)
- Without API contracts, components will be built on assumptions that may require rewrites
- **Impact:** Potential 20-30% rework if data shape doesn't match component expectations
- **Resolution:** Provide JSON schema or API documentation before Phase 1 completion

**2. Undefined Metrics & KPIs**
- "Metric Cards" section is mentioned but metrics aren't named
- What goes in each card? (agent count, success rate, uptime %, cost, etc.?)
- Unclear if same set of metrics applies to all users or varies by role
- **Impact:** Cards may need to be redesigned or data fetching refactored
- **Resolution:** Define 4-6 core metrics with calculation logic and success criteria

**3. Vague "Fleet Health" Requirements**
- Is it a single health score? A breakdown by agent status?
- What data feeds it? How is it calculated?
- Should it show trends (good/bad trajectory)?
- **Impact:** Section architecture depends entirely on this answer
- **Resolution:** Provide Fleet Health definition, data inputs, and desired visual representation

### 🟡 High

**4. No Approval Workflow Definition**
- "Pending Approvals" section exists, but workflow is undefined
- Single approval? Multi-level? What are approval states (pending, approved, rejected)?
- What metadata is required per approval (timestamp, approver, reason, impact)?
- **Impact:** PendingApprovalsSection component architecture depends on this
- **Resolution:** Document approval state machine and required fields

**5. Real-Time Update Strategy Missing**
- Is dashboard static or live?
- Should Active Runs refresh every 5s? 30s? On demand?
- Should Alerts auto-update or require refresh?
- **Impact:** Will determine hook architecture, WebSocket needs, and polling strategy
- **Resolution:** Define SLA for data freshness per section

**6. Incomplete Color Specification**
- Only status colors (green/yellow/red) are implied
- No brand primary color, danger color, or interactive state colors defined
- **Impact:** Components will use shadcn defaults; rebrand later = rework
- **Resolution:** Provide color palette with semantic mappings (primary, secondary, success, warning, error, info)

### 🟠 Medium

**7. Responsive Breakpoints Undefined**
- "Responsive" is required, but breakpoints aren't specified
- Mobile view: stack vertically? Collapse sections? Hide sections?
- Sidebar behavior: always visible, collapsible, hidden on mobile?
- **Impact:** Component grid/layout may need major revisions for mobile
- **Resolution:** Define tablet (768px) and mobile (375px) layouts for each section

**8. Sidebar Navigation Structure Missing**
- Sidebar is listed as a component to build, but nav structure is undefined
- What items? Hierarchical or flat? Icons + labels?
- How does user navigate to Agents, Runs, Approvals dashboards mentioned in project-structure?
- **Impact:** Layout and information architecture depend on this
- **Resolution:** Provide sitemap or wireframe of navigation hierarchy

**9. User Context & Authorization Unclear**
- Is user authentication in scope?
- Should dashboard show data filtered by user's role or organization?
- Are there permission levels that affect what sections display?
- **Impact:** May require context provider, auth hook, and data filtering logic
- **Resolution:** Define user model, roles, and data access rules

**10. Dark Mode Decision Pending**
- UI Standards are silent on dark mode
- Enterprise dashboards typically support dark mode (accessibility + night shift oncall)
- Should be designed in, not added later
- **Impact:** If added later, CSS variable architecture needs retrofit
- **Resolution:** Decide now if dark mode is required for launch or future

---

## Recommended Improvements

### 1. **Create a Design System Package**
Rather than scattering tokens across `styles/tokens.css` and Tailwind config:
- Create `@atlas/design-system` package (or folder)
- Export design tokens as TypeScript constants
- Include color, spacing, typography, shadow tokens
- Enables easy multi-platform reuse and generates documentation

### 2. **Implement Error Boundaries**
Production dashboards fail gracefully. Wrap each section in React Error Boundary:
```
<ErrorBoundary fallback={<SectionError title="Fleet Health" />}>
  <FleetHealthSection />
</ErrorBoundary>
```
Prevents one broken section from crashing entire page.

### 3. **Add Proper Loading Skeletons**
Use `shadcn/ui Skeleton` component to create realistic loading placeholders for each section. Better UX than spinners.

### 4. **Design for Real-Time Updates**
Plan for WebSocket or polling from day one:
- Use React Query or SWR for data fetching + caching
- Design cache invalidation strategy
- Prepare components for optimistic updates (approval actions)

### 5. **Accessibility Beyond WCAG**
- Add keyboard shortcuts for power users (Cmd+K to search, etc.)
- Implement proper focus management
- Use Radix UI primitives (which enforce a11y patterns)
- Test with screen reader and keyboard-only navigation during implementation

### 6. **Storybook for Component Documentation**
Create Storybook entries for each component with:
- All states (loading, empty, error, success, disabled)
- Interactive controls to test props
- Accessibility notes
Enables design review and reuse by team.

### 7. **Performance Monitoring**
Plan to instrument dashboard with Web Vitals:
- Core Web Vitals (LCP, FID, CLS)
- Custom metrics (time to first data paint)
- Error tracking (Sentry)
Essential for enterprise reliability.

### 8. **Internationalization Prep**
Structure strings for i18n from day one:
```typescript
// Use key-based strings
<h1>{t('dashboard.title')}</h1>
```
Don't hardcode English. Easier to support multiple languages later.

---

## Proposed Design System Changes

### Add to KNOWLEDGE.md

```markdown
## Color Palette (Semantic)

### Neutral Scale
- **bg-primary**: #ffffff
- **bg-secondary**: #f9fafb
- **bg-tertiary**: #f3f4f6
- **text-primary**: #111827
- **text-secondary**: #6b7280
- **text-tertiary**: #9ca3af
- **border-default**: #e5e7eb

### Functional Colors
- **success**: #10b981 (green)
- **warning**: #f59e0b (amber)
- **error**: #ef4444 (red)
- **info**: #3b82f6 (blue)

### Component States
- **hover**: 5% darker than component bg
- **active**: 10% darker than component bg
- **disabled**: opacity 50%, cursor not-allowed

## Breakpoints

- **Desktop**: ≥ 1280px (primary target)
- **Tablet**: 768px - 1279px (optimize layout)
- **Mobile**: < 768px (stack vertically, collapse non-critical)

## Real-Time Update SLA

- **Metrics**: Refresh every 30s (not critical)
- **Active Runs**: Refresh every 10s (semi-critical)
- **Alerts**: Immediate on backend event (critical)
- **Approvals**: Immediate on action (critical)
- **Schedule**: Refresh on page load (non-critical)
```

### Add to UI Standards

```markdown
## Dark Mode

Support dark mode via CSS variable overrides:
- Use `prefers-color-scheme: dark` media query
- Maintain 7:1 contrast ratio in both modes
- Test with dark mode enabled during development

## Motion

- Use Framer Motion only for:
  - Page transitions (fade in, slide in)
  - Status changes (state badges animating)
  - Micro-interactions (hover effects)
- Respect `prefers-reduced-motion` always
- No gratuitous animations; motion must convey meaning
```

---

## Proposed Work Order Changes

### Current Work Order 001 (as-is)

**Deliver:**
- React, Next.js, Tailwind, shadcn/ui, Responsive, Accessible

**Create:**
- Sidebar, Top Navigation, Page Header, Metric Cards, Fleet Health, Active Runs, Pending Approvals, Alerts, Upcoming Schedule

### Proposed Changes

**Add to Work Order 001 dependencies:**

Before implementation begins:
1. ✅ Define data model (API schema for dashboard data)
2. ✅ Specify 4-6 core metrics with calculation
3. ✅ Define "Fleet Health" (score calculation, data inputs)
4. ✅ Document approval workflow state machine
5. ✅ Determine real-time update strategy
6. ✅ Provide color palette (semantic mappings)
7. ✅ Define responsive breakpoints and layouts
8. ✅ Provide sidebar navigation structure
9. ✅ Clarify user context / auth scope
10. ✅ Decide on dark mode requirement

**Phase breakdown (clarified):**
- Phase 1: Foundation (Sidebar, TopBar, DashboardLayout)
- Phase 2: Core Components (MetricCard, StatusBadge, PageHeader, States)
- Phase 3: Sections (FleetHealth, ActiveRuns, Approvals, Alerts, Schedule)
- Phase 4: Integration (wire data, loading states)
- Phase 5: Polish (accessibility audit, responsive, micro-interactions)

**Acceptance criteria:**
- [ ] All states supported (loading, empty, error, success)
- [ ] WCAG 2.2 AA passes on desktop + mobile
- [ ] Keyboard navigation fully functional
- [ ] Mobile layout tested at 375px
- [ ] Tablet layout tested at 768px
- [ ] Error boundaries prevent cascade failures
- [ ] Performance: LCP < 2.5s, CLS < 0.1
- [ ] All components in Storybook with docs
- [ ] Dark mode functional (if in scope)

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Data model mismatch** | High | Requires component rework (days lost) | Nail data spec before Phase 1 |
| **Scope creep** | High | Timeline overrun | Lock feature list, separate nice-to-haves |
| **Responsive complexity** | Medium | Mobile layout doesn't work at 375px | Start mobile-first design for sections |
| **Accessibility gaps** | Medium | WCAG audit failure, rework needed | Test keyboard + screen reader weekly |
| **Real-time complexity** | Medium | WebSocket/polling architecture rework | Prototype data fetching pattern early |
| **Token/design inconsistency** | Low | Visual debt, rework in polish phase | Centralize all tokens, audit at Phase 3 |
| **API not ready** | Medium | Can't wire real data | Use mock data/Storybook during development |
| **Design review churn** | Low | Back-and-forth on comps | Get design sign-off on component library first |

---

## Questions

**Critical (block implementation):**

1. **What is the data model for dashboard data?**
   Provide JSON schema or API documentation for:
   - `/api/dashboard/metrics` (Metric Cards)
   - `/api/dashboard/fleet-health` (Fleet Health)
   - `/api/dashboard/active-runs` (Active Runs table)
   - `/api/dashboard/approvals` (Pending Approvals)
   - `/api/dashboard/alerts` (Alerts)
   - `/api/dashboard/schedule` (Upcoming Schedule)

2. **Define "Fleet Health" calculation and representation.**
   - Is it a single score (0-100%)? Or breakdown (X healthy, Y degraded, Z offline)?
   - What data feeds it? (agent status poll? external system?)
   - Should it show trends?

3. **Which 4-6 core metrics should appear in Metric Cards?**
   Example: Total Agents, Healthy Agents, Success Rate, Avg Runtime, Pending Approvals, Total Cost?
   Or different set?

4. **Define approval workflow state machine.**
   - What states? (pending, approved, rejected, expired?)
   - Single-level or multi-level approval?
   - Required metadata per approval?
   - What actions can user take? (approve, reject, comment?)

5. **What is the real-time update strategy?**
   - Which sections should live-update? (frequency?)
   - Which can be static? (refresh on page load?)
   - WebSocket or polling? SLA for data freshness?

6. **Provide the semantic color palette.**
   - Primary action color?
   - Secondary/tertiary button colors?
   - All six status colors (neutral, success, warning, error, info, brand)?
   - Should match enterprise aesthetic (not vibrant or pastel).

7. **Define responsive layout for each section at 375px and 768px.**
   - Sidebar: always visible, collapsible, or hidden on mobile?
   - Metric cards: grid collapse? 2 cols on tablet, 1 on mobile?
   - Tables: horizontal scroll? Simplified view on mobile?

8. **Provide sidebar navigation structure.**
   - What nav items? (Dashboard, Agents, Runs, Approvals, Settings?)
   - Hierarchical (expandable) or flat?
   - Icons only or icon + label?
   - Where do users navigate from sidebar?

9. **Is user authentication and role-based access control in scope?**
   - Should dashboard filter data by user role?
   - Are there permission levels that affect section visibility?
   - How is user context provided? (Next.js middleware? Session provider?)

10. **Is dark mode required for launch or future nice-to-have?**
    - If required: needs to be designed from day one
    - If future: still structure CSS variables for easy retrofit

**Non-blocking (clarifying):**

11. Is error recovery automatic (retry button?) or manual (user refresh)?
12. Should Metric Cards show historical trends or just current values?
13. Should Active Runs table be sortable/filterable?
14. Should Alerts be dismissible or permanent until resolved?
15. Should UpcomingSchedule show time zone of user or fixed UTC?

---

## Final Recommendation

**Approved with Changes**

### Rationale

The work order is **strategically sound and architecturally viable**, but **cannot proceed to implementation without clarification** of the 10 critical questions above. The documentation demonstrates strong design principles and tech choices (enterprise-grade), but lacks the specificity needed to prevent assumption-driven rework.

The proposed implementation plan is comprehensive and realistic. With the proposed design system changes and work order clarifications, this is a 4-5 day implementation (assuming 1 engineer, sequential phases).

### Prerequisites for Phase 1 Start

**Must complete before touching code:**
- ✅ Resolve all 10 critical questions (or provide mock data contracts)
- ✅ Approve proposed design system additions
- ✅ Lock down responsive breakpoints and layouts
- ✅ Confirm color palette
- ✅ Decide dark mode scope

**Recommended before Phase 1:**
- ✅ Provide Figma comps or detailed wireframes (if available)
- ✅ Confirm approval workflow (design review)
- ✅ Establish mock API endpoints or Storybook + MSW strategy

### Contingency

If clarifications are delayed:
- Proceed with Phase 1 (Sidebar, TopBar, DashboardLayout) using best-guess assumptions
- Build Storybook mock data for components
- Phase 2-3 can start in parallel once data model is defined
- Aim for <1 day rework when real data arrives

### Success Criteria

When this work order is "done":
- ✅ Dashboard loads in < 2.5s on 3G
- ✅ All sections have loading, empty, error states
- ✅ WCAG 2.2 AA on desktop, tablet, mobile
- ✅ Keyboard navigation fully functional
- ✅ 95+ Lighthouse score
- ✅ All components documented in Storybook
- ✅ Approval workflow fully wired
- ✅ Real-time updates working (or mocked if backend pending)

---

**Status:** Ready for stakeholder review.
**Next Step:** Address questions and approve changes, then proceed to Phase 1.
