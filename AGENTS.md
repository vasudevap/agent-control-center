# AGENTS.md

# Agent Control Center Repository Instructions

This document defines the engineering standards, architectural principles, and working conventions for every AI coding assistant (Codex, ChatGPT, or future agent) contributing to this repository.

This file is considered authoritative.

---

# Codex Model Recommendation Preferences

When the user asks what the next step is, include a task-appropriate Codex recommendation with the exact **Model**, **Effort**, and **Speed** settings. Balance output quality, latency, and usage rather than always recommending the most capable setting.

Use the model names confirmed in the user's Codex picker on 2026-07-15:

- `5.6 Sol · High · Standard` for complex or ambiguous architecture, frontend design, governance, and high-value multi-step implementation.
- `5.6 Terra · Medium · Standard` for routine implementation, code review, and well-scoped feature work.
- `5.6 Luna · Medium · Standard` for tests, cleanup, repetitive edits, and other predictable repository work.
- `5.3 Codex Spark` with the lowest sufficient effort for very quick, simple iterations; do not recommend it for complex browser, visual, architectural, or multi-step work.

Recommend `Fast` speed only when lower latency is worth the higher usage; otherwise prefer `Standard`. The user's current task selection in the Codex UI overrides global configuration for that task. Do not use vague or unconfirmed labels such as “GPT-5 Codex.” If the available model picker changes, use the updated choices the user provides and revise these preferences.

The current Atlas design task uses `5.6 Sol · High · Standard`; treat this as task context, not a permanent default for every future task.

---

# Project Purpose

The Agent Control Center is an enterprise-inspired platform for creating, governing, scheduling, monitoring, and operating AI agents.

The project has three equal objectives:

1. Build a production-quality productivity platform.
2. Learn enterprise AI architecture through implementation.
3. Produce a professional portfolio demonstrating Enterprise and AI Solution Architecture.

Every contribution should support these objectives.

---

# Primary Design Philosophy

Always optimize for:

- clarity
- maintainability
- security
- extensibility
- observability
- architectural consistency

Do **not** optimize for writing the fewest lines of code.

Avoid unnecessary cleverness.

---

# Architecture First

Never implement major functionality before architecture exists.

Before implementing new capabilities:

- Review the architecture documentation.
- Check for existing ADRs.
- If a significant architectural decision is required, create a proposed ADR before implementation.

---

# Repository Structure

```text
apps/web/                         # Atlas frontend
docs/architecture/               # Canonical architecture
docs/design/                     # Approved product design
docs/specifications/             # Product specifications
docs/engineering-specifications/ # Engineering execution specifications
docs/work-orders/                # Authorized implementation scope
docs/reviews/                    # Review and handoff records
docs/decisions/                  # Decision indexes and non-design decisions
docs/recommendations/            # Advisory guidance
docs/references/                 # Supporting and historical material
.claude/                         # Claude-specific instructions
```

Root `AGENTS.md` is tool-neutral. Tool-specific instructions belong in their scoped configuration directories and must not override repository-wide policy.

Do not create new top-level folders without architectural justification.

---

# Documentation Standards

Every significant implementation should update documentation.

Documentation is treated as part of the product.

If implementation changes architecture:

Update:

- architecture documents
- ADRs
- README
- ROADMAP
- Notion specification (when applicable)

---

# Coding Standards

Prefer:

- explicit code
- readable code
- typed code
- modular code

Avoid:

- deeply nested logic
- hidden side effects
- unnecessary abstraction
- premature optimization
- duplicated business logic

---

# Python Standards

Use:

- Python 3.12+
- type hints
- dataclasses where appropriate
- async for IO
- dependency injection
- clear package boundaries

Prefer composition over inheritance.

---

# TypeScript Standards

Use:

- strict mode
- typed interfaces
- no implicit any
- functional React components
- reusable hooks
- server components only when justified

---

# API Standards

Every endpoint should:

- validate input
- validate output
- require authentication unless explicitly public
- return structured errors
- include correlation IDs
- avoid leaking internal implementation details

---

# Security Standards

Always follow:

- least privilege
- deny by default
- secure by design
- explicit trust boundaries

Never:

- log secrets
- expose OAuth tokens
- expose API keys
- expose database credentials

Never disable security controls for convenience.

---

# LLM Standards

Treat every LLM response as untrusted.

Every model output must be:

- validated
- schema checked
- policy checked
- audited when appropriate

The model never authorizes actions.

---

# Tool Standards

Agents may only use tools explicitly assigned to them.

Do not bypass:

- Tool Registry
- Connector Runtime
- Policy Engine
- Approval Service

---

# Agent Standards

Every new agent should:

- register itself
- declare capabilities
- declare required connectors
- declare required tools
- declare required permissions
- declare risk level
- expose health
- support structured outputs

Do not create one-off agents that bypass platform contracts.

---

# Connector Standards

Every connector should:

- implement the connector contract
- support health checks
- normalize errors
- normalize results
- support audit logging
- avoid exposing provider SDKs directly

---

# Database Standards

PostgreSQL is the runtime system of record.

Avoid:

- business logic in SQL
- duplicated state
- unnecessary JSON blobs

Prefer normalized schemas.

---

# Logging Standards

Use structured logging.

Every log should include:

- timestamp
- component
- severity
- correlation ID
- run ID when applicable

Never log:

- OAuth tokens
- passwords
- secrets
- API keys
- full email bodies by default

---

# Audit Standards

Material actions must generate audit events.

Examples:

- approvals
- connector changes
- external actions
- security changes
- policy changes

Audit events should not be deleted.

---

# Testing Standards

Every feature should include appropriate tests.

Possible test types:

- unit
- integration
- contract
- end-to-end

Critical platform components require integration tests.

---

# Architecture Decision Records

Create an ADR whenever:

- introducing a framework
- selecting hosting
- changing authentication
- changing runtime
- introducing infrastructure
- changing data architecture
- changing deployment strategy

Never make significant architectural decisions silently.

---

# Framework Adoption

Default order:

1. Plain Python
2. Direct SDK
3. LangChain (only when justified)
4. LangGraph (stateful workflows)
5. Temporal (durable orchestration)

Frameworks are introduced because requirements demand them.

Never because they are popular.

---

# Pull Request Expectations

Every significant change should answer:

Why?

What changed?

What architecture changed?

Which documents changed?

Which ADRs changed?

How was it tested?

All contributions must follow the canonical engineering controls under `docs/governance/`:

- meet the Definition of Ready before implementation
- use a short-lived branch linked to an approved Work Order, Engineering Specification, defect, or maintenance task
- merge through a pull request after required CI passes
- provide the evidence required by the pull-request and review process
- meet the Definition of Done before the work is closed or released

Do not bypass, disable, or weaken required CI. Failed required checks block merge. Exceptions must follow the documented exception process and must not silently change architecture, product, design, or security authority.

---

# Commit Messages

Use clear messages.

Examples:

```
Add Gmail connector contract

Implement Agent Registry

Define runtime adapter interface

Create approval workflow

Introduce connector health model
```

Avoid:

```
updates

misc

fix

changes
```

---

# Notion

Git is the technical source of truth.

Notion is the operational workspace.

The Notion Provisioner should synchronize selected repository content into Notion.

Do not edit generated Notion structures manually unless documented.

---

# AI Assistant Behaviour

AI coding assistants should:

- prefer existing architecture
- avoid duplicate abstractions
- explain significant trade-offs
- keep implementations consistent
- recommend ADRs when appropriate
- update documentation when needed

When uncertain:

Ask rather than invent.

---

# Long-Term Vision

The repository should evolve into an enterprise-quality AI platform demonstrating:

- Solution Architecture
- Enterprise Architecture
- AI Architecture
- Secure AI Systems
- Agent Governance
- Agent Operations
- Observability
- Human-in-the-loop workflows
- Production-ready integrations

The quality of the architecture is more important than the quantity of implemented features.
