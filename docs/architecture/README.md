# Architecture Documentation

## Purpose

This directory contains the modular architecture documentation for the Agent Control Center.

The documentation is organized so each architectural concern can be reviewed, updated, versioned, and referenced independently.

---

## Architecture Documents

1. [Executive Summary](./01-executive-summary.md)
2. [Architecture Principles](./02-architecture-principles.md)
3. [System Context](./03-system-context.md)
4. [Container Architecture](./04-container-architecture.md)
5. [Component Architecture](./05-component-architecture.md)
6. [Deployment Architecture](./06-deployment-architecture.md)
7. [Security Architecture](./07-security-architecture.md)
8. [Data Architecture](./08-data-architecture.md)
9. [Agent Runtime Architecture](./09-agent-runtime.md)
10. [Connector Framework](./10-connector-framework.md)
11. [Observability Architecture](./11-observability.md)
12. [Technology Strategy](./12-technology-strategy.md)
13. [Human Approvals](./13-human-approvals.md)

---

## Recommended Reading Order

For a high-level understanding:

1. Executive Summary
2. Architecture Principles
3. System Context
4. Container Architecture
5. Technology Strategy

For implementation planning:

1. Component Architecture
2. Deployment Architecture
3. Data Architecture
4. Agent Runtime Architecture
5. Connector Framework

For governance and operations:

1. Security Architecture
2. Observability Architecture
3. Architecture Decision Records
4. Human Approvals

---

## Related Repository Documents

- [`PROJECT.md`](../../PROJECT.md)  
  Defines the project purpose, scope, goals, and success criteria.

- [`ROADMAP.md`](../../ROADMAP.md)  
  Defines the phased delivery plan.

- [`AGENTS.md`](../../AGENTS.md)  
  Defines repository conventions and instructions for AI coding agents.

- [`README.md`](../../README.md)  
  Provides the repository-level overview and setup guidance.

---

## Architecture Decision Records

Major decisions should be documented under:

```text
docs/decisions/
```

Each ADR should include:

- Context
- Decision drivers
- Considered options
- Decision
- Consequences
- Risks
- Revisit triggers

Architecture documents should reference related ADRs where appropriate.

---

## Documentation Standards

Architecture documents should:

- Use Markdown
- Use Mermaid for diagrams
- Use clear headings
- Avoid undocumented implementation assumptions
- Reference relevant ADRs
- Identify open questions
- Record current status
- Be updated when implementation changes materially

---

## Source of Truth

The Git repository is the technical source of truth for architecture documentation.

Notion is the operational workspace for:

- Progress tracking
- Learning notes
- Backlog management
- Build logs
- Architecture review
- LinkedIn content planning

The Notion provisioner may synchronize selected content from this directory into the AI Architecture Lab workspace.

---

## Current Status

The initial architecture baseline is documented.

The next architecture activities are:

- Create Architecture Decision Records
- Define detailed API contracts
- Define the physical PostgreSQL schema
- Define the plugin manifest
- Create detailed dashboard interaction flows
- Validate the architecture against the Gmail Agent MVP
