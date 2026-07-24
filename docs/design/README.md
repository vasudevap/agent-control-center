# Atlas Design Documentation

**Purpose**

This directory contains the product design documentation for **Atlas**, the
Agent Control Center.

The active MVP experience is defined by
[`12-agent-visibility-mvp-experience.md`](./12-agent-visibility-mvp-experience.md)
and DDR-003. Earlier product-domain, information-architecture, journey, and
screen documents preserve the original execution-platform design and remain
historical or future-capability references where they conflict.

---

# Design Philosophy

Atlas is designed as an enterprise-grade operational product.

Its interface should inspire confidence through:

- Control
- Trust
- Clarity
- Predictability
- Observability
- Governance

The goal is not to make AI appear magical.

The goal is to make autonomous systems understandable and controllable.

---

# Scope

This repository covers:

- Brand strategy
- UX foundations
- Information architecture
- User experience
- Visual identity
- Design language
- Design system
- Component library
- Screen specifications
- Developer design handoff

This repository does **not** define:

- deployment architecture
- backend services
- APIs
- databases
- runtime architecture
- orchestration
- infrastructure
- security implementation

Those belong in `/docs/architecture`.

---

# Active document dependency

```text
ADR-008 + ADR-009
        |
        v
DDR-003
        |
        v
12 Agent Visibility MVP Experience
        |
        +--> 01 Design Principles
        +--> 05 Visual Identity
        +--> 07 Design System
        +--> 08 Component Library
```

The original brand, domain, information architecture, journey, and screen
documents remain legacy references where they conflict with this dependency.

---

# Current Design Documents

| Document | Active status |
|-----------|---------|
| `12-agent-visibility-mvp-experience.md` | Active MVP experience and screen responsibilities |
| `01-design-principles.md` | Active |
| `05-visual-identity.md` | Active |
| `07-design-system.md` | Active |
| `08-component-library.md` | Active |
| `00-brand.md` | Legacy broad positioning; revise during implementation |
| `02-product-domain-model.md` | Legacy broad domain |
| `03-information-architecture.md` | Superseded for active navigation |
| `04-user-experience.md` | Legacy broad journeys |
| `09-screen-specifications-overview.md` | Legacy screen baseline |
| `10-screen-specifications-platform.md` | Legacy/deferred screen baseline |
| `11-developer-handoff.md` | Legacy broad handoff |

---

# Design Principles

Every design decision should reinforce the following principles.

1. Information before configuration.
2. Operators remain in control.
3. Every autonomous action is observable.
4. Trust is earned through evidence.
5. Complex systems should feel understandable.
6. Consistency is more valuable than novelty.
7. Interfaces should scale from individuals to organizations.
8. Enterprise quality is expressed through restraint, not decoration.

---

# Quality Gates

Before a design document is considered complete, confirm that it:

- has a single, well-defined responsibility
- avoids duplicating other documents
- uses canonical Atlas terminology
- supports future enterprise scale
- remains implementation-agnostic where appropriate
- aligns with the Brand Strategy and UX Foundation

---

# Design Decision Records

Future design decisions should be captured under:

```text
design/
└── decisions/
```

Each Design Decision Record (DDR) should include:

- Decision
- Context
- Alternatives Considered
- Rationale
- Consequences
- Status

Active design decisions:

- DDR-001 - Typography Direction
- DDR-002 - Visual Language Direction
- DDR-003 - Agent Visibility MVP Information Architecture

---

# Canonical Terminology

Use consistent terminology throughout the design documentation.

Active MVP examples:

- Agent
- Agent credential
- Heartbeat
- Execution
- Observed health
- Reported health
- Alert
- Activity
- Environment
- Version

Run, Connector, Policy, Approval, Artifact, Output, and Workspace remain
reserved future-capability terms.

Avoid introducing synonyms unless they represent distinct concepts.

---

# Contribution Guidelines

When adding or revising documentation:

- Update the smallest responsible document.
- Avoid duplicating content.
- Reference related documents rather than repeating them.
- Preserve canonical terminology.
- Keep design concerns separate from architecture concerns.

---

# Success Criteria

The design repository is successful when a new designer or engineer can understand:

- what Atlas is
- how the product is organized
- why design decisions were made
- how interfaces should behave
- how future work should remain consistent

without requiring tribal knowledge.

---

# Long-Term Goal

This directory should evolve into a complete product design handbook suitable for an enterprise software organization.

It should demonstrate disciplined product thinking, cohesive UX strategy, and production-quality design documentation suitable for implementation and long-term maintenance.
