# Architecture Documentation

## Purpose

This directory contains the architecture documentation for the Agent Control Center.

The active MVP architecture is defined by
[Agent Visibility MVP Target Architecture](./14-agent-visibility-mvp-target-architecture.md),
ADR-008, and ADR-009. Documents 01 through 13 preserve the original
execution-platform baseline and remain useful historical or future-capability
references. They do not override the active baseline where they conflict.

---

## Architecture Documents

1. [Agent Visibility MVP Target Architecture](./14-agent-visibility-mvp-target-architecture.md) - active
2. [Architecture Principles](./02-architecture-principles.md) - retained, interpreted through ADR-008 and ADR-009
3. [Executive Summary](./01-executive-summary.md) - legacy baseline
4. [System Context](./03-system-context.md) - legacy baseline
5. [Container Architecture](./04-container-architecture.md) - legacy baseline
6. [Component Architecture](./05-component-architecture.md) - legacy baseline
7. [Deployment Architecture](./06-deployment-architecture.md) - legacy baseline with reusable hosting decisions
8. [Security Architecture](./07-security-architecture.md) - legacy baseline with reusable controls
9. [Data Architecture](./08-data-architecture.md) - legacy baseline
10. [Agent Runtime Architecture](./09-agent-runtime.md) - deferred Atlas-owned runtime
11. [Connector Framework](./10-connector-framework.md) - deferred capability
12. [Observability Architecture](./11-observability.md) - legacy broad platform model
13. [Technology Strategy](./12-technology-strategy.md) - legacy broad platform model
14. [Human Approvals](./13-human-approvals.md) - deferred capability

---

## Recommended Reading Order

For active work:

1. ADR-008
2. ADR-009
3. Agent Visibility MVP Product Requirements
4. Agent Visibility MVP Target Architecture
5. Agent Integration API
6. Atlas Agent Visibility MVP Reset Plan

Read documents 01 through 13 only for historical rationale, reusable controls,
or a separately accepted future capability.

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

ADR-008 and ADR-009 establish the active agent-visibility direction. The
original execution-platform architecture remains preserved but is no longer
the active implementation target.

The next architecture activities are:

- refine and accept ES-009;
- define the physical PostgreSQL schema and current-to-target table mapping;
- select exact credential verifier, rate, retention, and health thresholds;
- define route and active-component disposition;
- define forward migration, evaluator deployment, validation, and rollback;
- authorize bounded implementation Work Orders.
