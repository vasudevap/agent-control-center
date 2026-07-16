# Work Order 010: Atlas Public Site

**Status:** Implementation In Progress
**Work Order ID:** WO-010
**Type:** Public website
**Implementation Authorization:** Granted
**Product Brief:** [Atlas Public Site Discovery Brief](../specifications/atlas-public-site-discovery-brief.md)
**Design Authority:** [Atlas Public Site Experience](../design/12-public-site-experience.md)
**Architecture Authority:** [ADR-003 Public Site Application and Hosting Boundary](../decisions/ADR-003-public-site-application-boundary.md)

---

## 1. Purpose

Create the first public Atlas website as an independently deployable application
inside the existing monorepo.

The website must explain the Agent Control Center category, communicate Atlas's
control, trust, and clarity principles, demonstrate product and architecture
quality, and represent current implementation maturity accurately.

## 2. User Outcome

A qualified visitor can:

- understand what Atlas is from the first viewport;
- recognize the operational problems Atlas addresses;
- understand the importance of human control and inspectable evidence;
- explore fleet, run, approval, connector, and architecture concepts;
- distinguish Built, Designed, and Planned capabilities;
- understand that Atlas is in active development;
- navigate the complete page using keyboard, touch, or assistive technology.

## 3. Approved Scope

### 3.1 In scope

- Create `apps/site` as a public, read-only website workspace.
- Implement the approved single-page information architecture.
- Create an Atlas-specific header, hero, product evidence preview, problem
  statement, pillars, walkthrough, human-authority feature, architecture
  diagram, maturity section, Gmail reference, closing action, and footer.
- Add responsive behavior from 320 CSS pixels through large desktop widths.
- Add descriptive page and social metadata. Defer favicon and social-preview
  imagery until an approved Atlas brand asset is available and passes review.
- Add focused rendered-output tests.
- Add Sites-compatible hosting configuration.
- Add root workspace scripts for independent and aggregate validation.
- Update CI, README, roadmap, project status, architecture, and technology docs.
- Produce a private hosted release after successful validation.

### 3.2 Explicitly out of scope

- Changes to Atlas product behavior in `apps/web`.
- Authentication, accounts, persistence, forms, analytics, cookies, or tracking.
- Backend services, APIs, database access, agent execution, or connectors.
- Pricing, subscriptions, trials, sales automation, or lead capture.
- Customer logos, testimonials, production metrics, or fabricated outcomes.
- A custom production domain or DNS changes.
- Public repository publication or licensing changes.
- A shared design-system package.
- Model-generated identity marks or fallback social imagery.

## 4. Required File Scope

### 4.1 Create

- `apps/site/**`
- `docs/specifications/atlas-public-site-discovery-brief.md`
- `docs/design/12-public-site-experience.md`
- `docs/decisions/ADR-003-public-site-application-boundary.md`
- `docs/work-orders/010-atlas-public-site.md`

### 4.2 Modify

- `package.json`
- `package-lock.json`
- `.github/workflows/ci.yml`
- `README.md`
- `PROJECT.md`
- `ROADMAP.md`
- `docs/architecture/06-deployment-architecture.md`
- `docs/architecture/12-technology-strategy.md`
- `docs/design/README.md`
- `docs/decisions/README.md`
- `docs/work-orders/README.md`

No implementation file in `apps/web` is authorized for modification.

## 5. Functional and Content Requirements

- The first viewport must include identity, category, primary outcome,
  active-development context, two exploration actions, and a product preview.
- Page navigation must use stable anchors and support keyboard access.
- Product evidence must use fictional, non-sensitive operational content.
- Every planned capability must be labeled as planned or architectural design.
- Built, Designed, and Planned groups must remain distinct at every viewport.
- Core content comprehension and anchor navigation must not depend on client
  state.
- The page must include no unavailable signup or sales action.

## 6. Design Requirements

- Preserve the approved Modern Infrastructure direction.
- Use strong typography, neutral surfaces, restrained semantic color, fine
  borders, and product evidence rather than decorative AI imagery.
- Avoid robots, brains, sparkles, glowing orbs, stock photography, or cyberpunk
  treatment.
- Do not reproduce the dense application shell as the website layout.
- Honor reduced-motion preferences.

## 7. Accessibility and Quality Requirements

- Target WCAG 2.2 AA.
- Include a visible-on-focus skip link.
- Use semantic landmarks and logical heading order.
- Maintain a single `h1`, visible focus states, and accessible names.
- Avoid color-only status meaning.
- Support 200 percent zoom and a 320 CSS-pixel viewport.
- Avoid document-level horizontal scrolling.
- Provide descriptive page and social metadata.

## 8. Verification

Required checks:

- site lint, rendered-output tests, and production build;
- root product typecheck, lint, tests, and aggregate build;
- inspection for secrets, development URLs, fabricated claims, and inaccessible
  navigation;
- private deployment status confirmation.

Browser screenshots or interactive browser QA are not required unless explicitly
requested during review.

## 9. Definition of Done

- [ ] Discovery, design, and architecture records are approved and consistent.
- [ ] `apps/site` exists as a sibling workspace to `apps/web`.
- [ ] All required page sections and content are implemented.
- [ ] Built, Designed, and Planned claims are distinct and accurate.
- [ ] The site meets responsive and accessibility requirements.
- [ ] No existing `apps/web` implementation file is changed.
- [ ] Root scripts and CI validate both applications.
- [ ] Documentation reflects the new public application and hosting boundary.
- [ ] Required local checks pass.
- [ ] A private Sites deployment succeeds.
- [ ] A review record captures final evidence and deferred work.

## 10. Risks and Controls

| Risk | Required control |
| --- | --- |
| Prototype is mistaken for a production platform | Visible active-development context and maturity labels |
| Marketing language overstates capability | Claims tied to Built, Designed, or Planned status |
| Public site disrupts product work | Separate application and no `apps/web` implementation changes |
| Brand diverges | Inherit approved brand and Modern Infrastructure direction |
| New hosting expands the trusted boundary | Static content with no secrets, data, auth, or connectors |
| CI becomes ambiguous | Independent scripts plus aggregate root checks |

## 11. Approval Record

| Role | Decision | Name | Date |
| --- | --- | --- | --- |
| Product owner | Approved | Repository Maintainer | 2026-07-15 |
| UX/design reviewer | Approved | Repository Maintainer | 2026-07-15 |
| Architecture reviewer | Approved | Repository Maintainer | 2026-07-15 |
| Engineering reviewer | Approved | Repository Maintainer | 2026-07-15 |

## 12. Authorization Statement

This Work Order authorizes only the bounded public-site implementation described
above. It does not authorize changes to product behavior, backend services,
authentication, production agent execution, commercial claims, repository
visibility, or custom-domain configuration.
