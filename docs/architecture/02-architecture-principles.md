# Architecture Principles

> **Active with revised interpretation.** Apply these principles through
> ADR-008, ADR-009, and the active Agent Visibility MVP Target Architecture.
> References to an Atlas-owned execution plane describe a deferred capability.

## Purpose

This document defines the architectural principles that guide every design and implementation decision within the Agent Control Center.

These principles establish consistency across the platform, support long-term maintainability, and provide a framework for evaluating future technologies and architectural decisions.

---

# Principle 1 — Architecture Before Implementation

## Statement

Every significant implementation begins with a documented architectural design.

## Rationale

A clear architecture reduces technical debt, improves consistency, enables better discussions, and creates reusable patterns.

## Implications

- Create architecture before writing code.
- Record major decisions as ADRs.
- Review architecture before introducing new technologies.

---

# Principle 2 — Separation of Concerns

## Statement

Each component should have a single, well-defined responsibility.

## Rationale

Separating responsibilities improves maintainability, testability, scalability, and security.

## Application

Examples include:

- Dashboard
- API
- Scheduler
- Agent Runtime
- Connectors
- Database
- Logging
- Approval Service

No component should perform multiple unrelated responsibilities.

---

# Principle 3 — Control Plane and Execution Plane Separation

## Statement

Management of agents must remain separate from execution of agents.

## Control Plane Responsibilities

- Agent Registry
- Scheduling
- Configuration
- Status
- Logging
- Approvals
- Policies
- Health
- Dashboard

## Execution Plane Responsibilities

- Execute workflows
- Call LLMs
- Call APIs
- Read email
- Save files
- Generate outputs

This separation allows new agent implementations without redesigning platform governance.

---

# Principle 4 — Security by Design

## Statement

Security must be incorporated into every architectural decision rather than added later.

## Examples

- Least privilege
- OAuth
- Secret management
- Encryption
- Approval workflows
- Audit logging
- Trust boundaries
- Secure defaults

---

# Principle 5 — Least Privilege

## Statement

Every user, connector, service, and agent receives only the permissions required for its approved responsibilities.

## Examples

- Minimum OAuth scopes
- Limited API permissions
- Restricted file access
- Read-only where possible

---

# Principle 6 — Human-in-the-Loop

## Statement

High-risk actions require explicit human approval.

## Examples

- Sending email
- Deleting messages
- Forwarding email
- Sharing files
- Modifying calendars
- Publishing content

Automation should assist decision-making rather than replace human judgment for sensitive operations.

---

# Principle 7 — Observable by Default

## Statement

Every significant platform activity should be measurable and traceable.

## Platform Observability

- Logs
- Metrics
- Run history
- Health checks
- Errors
- Outputs
- Audit events

Failures should be diagnosable without reproducing them.

---

# Principle 8 — Auditability

## Statement

Material decisions and actions must be permanently traceable.

## Audit Records

Each audit event should identify:

- User
- Agent
- Connector
- Action
- Timestamp
- Approval
- Result
- Correlation ID

---

# Principle 9 — Extensibility

## Statement

Adding a new agent should not require modifications to the platform architecture.

## Requirements

Every agent should:

- Register itself
- Describe its capabilities
- Declare required permissions
- Publish health
- Report outputs
- Use standard execution contracts

---

# Principle 10 — Progressive Complexity

## Statement

The simplest architecture capable of satisfying current requirements should be preferred.

## Examples

Current MVP:

- Plain Python
- FastAPI
- PostgreSQL
- Render Cron

Future:

- LangChain
- LangGraph
- Temporal

Technology should be introduced only when it solves an identified architectural problem.

---

# Principle 11 — Framework Independence

## Statement

Business capabilities should not depend upon a specific AI framework.

The platform should be capable of evolving between:

- Plain Python
- LangChain
- LangGraph
- CrewAI
- AutoGen

without requiring significant redesign.

---

# Principle 12 — Explicit Contracts

## Statement

Every interaction between platform components should use clearly defined contracts.

Examples include:

- Agent registration
- Scheduling
- Connectors
- Logging
- Outputs
- Approvals

Contracts reduce coupling and simplify testing.

---

# Principle 13 — Configuration over Code

## Statement

Operational behaviour should be configurable wherever practical.

Examples include:

- Schedules
- Connector settings
- Feature flags
- Retry policies
- Approval thresholds

---

# Principle 14 — Source of Truth

Every major artifact has a single authoritative source.

| Artifact      | Source of Truth            |
| ------------- | -------------------------- |
| Source code   | Git                        |
| Architecture  | Markdown                   |
| Decisions     | ADRs                       |
| Tasks         | Notion                     |
| Learning      | Notion                     |
| Runtime state | PostgreSQL                 |
| Secrets       | Environment / Secret Store |

---

# Principle 15 — Documentation as a Deliverable

Documentation is part of the product.

Architecture documentation should evolve alongside implementation.

The objective is to ensure the project can be understood, maintained, and extended without relying on undocumented knowledge.

---

# Principle 16 — Continuous Learning

The platform exists not only to solve productivity problems but also to deepen expertise in enterprise AI architecture.

Every implementation should produce:

- Architecture knowledge
- Technical documentation
- ADRs
- Learning journal entries
- Portfolio material
- LinkedIn content

Learning is considered a first-class project outcome.

---

# Review Process

These principles should be reviewed whenever:

- A new framework is introduced.
- The hosting architecture changes.
- Security requirements evolve.
- Enterprise capabilities are added.
- Major architectural decisions are made.

Any exception should be documented through an Architecture Decision Record (ADR).
