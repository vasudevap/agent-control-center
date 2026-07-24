# AGENTS.md

# Agent Control Center Repository Instructions

This document defines the engineering standards, architectural principles, and working conventions for every AI coding assistant (Codex, ChatGPT, or future agent) contributing to this repository.

This file is considered authoritative.

---

# Codex Model Recommendation Preferences

When the user asks what the next step is, include a task-appropriate Codex recommendation with the exact **Model**, **Effort**, and **Speed** settings. Balance output quality, latency, and usage rather than always recommending the most capable setting.

Before beginning or resuming any substantive work session, provide the
task-appropriate **Model**, **Effort**, and **Speed** recommendation in a
standalone user-facing message, then pause without calling tools or starting
implementation. Continue only after the user confirms that the setting is
already correct or that they have changed it. If the user explicitly confirms
the setting and asks to resume in the same message, that confirmation satisfies
the pause requirement. This rule exists because the Codex task model cannot be
changed once execution is underway.

Use the model names available in the user's Codex picker as updated on 2026-07-17:

- `5.5 · High · Standard` for complex or ambiguous architecture, frontend design, governance, and high-value multi-step implementation.
- `5.6 Terra · Medium · Standard` for routine implementation, code review, and well-scoped feature work.
- `5.6 Luna · Medium · Standard` for tests, cleanup, repetitive edits, and other predictable repository work.
- `5.3 Codex Spark` with the lowest sufficient effort for very quick, simple iterations; do not recommend it for complex browser, visual, architectural, or multi-step work.

Recommend `Fast` speed only when lower latency is worth the higher usage; otherwise prefer `Standard`. The user's current task selection in the Codex UI overrides global configuration for that task. Do not use vague or unconfirmed labels such as “GPT-5 Codex.” Do not recommend Sol unless the user explicitly restores access to it. If the available model picker changes, use the updated choices the user provides and revise these preferences.

The current Atlas architecture and governance lane uses `5.5 · High · Standard`; treat this as task context, not a permanent default for every future task.

---

# Project Purpose

The Agent Control Center is an enterprise-inspired visibility and lifecycle
control center for AI agents built, deployed, scheduled, and operated outside
Atlas.

The project has three equal objectives:

1. Build a production-quality platform for agent enrollment, trust lifecycle,
   health, execution visibility, alerts, and activity.
2. Learn enterprise AI architecture through implementation.
3. Produce a professional portfolio demonstrating Enterprise and AI Solution Architecture.

Every contribution should support these objectives.

The active MVP is governed by ADR-008 and ADR-009. Atlas does not host, deploy,
schedule, execute, pause, resume, stop, or maintain external agent runtimes.
Future control-plane capabilities require separate accepted authority.

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

Implementation agents should execute planned decisions, not discover the
architecture while coding. Before provisioning infrastructure, installing
persistent services, introducing deployment resources, or implementing a major
platform capability, the project should already have:

- the target architecture documented;
- the deployment and infrastructure boundaries documented;
- the persistence location and environment strategy documented;
- required ADRs accepted;
- an accepted Engineering Specification or Work Order with explicit scope,
  exclusions, validation, and rollback expectations.

If those decisions are missing, the correct next step is planning, not
implementation.

---

# Repository Structure

```text
apps/api/                         # Atlas backend foundation
apps/web/                         # Atlas frontend
docs/architecture/               # Canonical architecture
docs/design/                     # Approved product design
docs/specifications/             # Product specifications
docs/engineering-specifications/ # Engineering execution specifications
docs/implementation-plans/       # Cross-work-order implementation planning
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

Do not bypass an accepted platform boundary. Tool Registry, Connector Runtime,
Policy Engine, Approval Service, and Atlas-owned execution are deferred
capabilities rather than active MVP dependencies.

---

# Agent Standards

Every new agent should:

- be enrolled by the Atlas owner;
- use a credential scoped to its Atlas identity;
- call the versioned Atlas REST API from its external runtime;
- send authenticated heartbeats where heartbeat monitoring is selected;
- report bounded execution summaries using stable identities;
- declare version, build, environment, and structured health checks;
- keep provider credentials, business configuration, tools, schedules, and
  runtime control outside Atlas;
- exclude secrets and unnecessary business content from telemetry;
- tolerate bounded retries and idempotent replay;
- support credential rotation and immediate Atlas rejection after disconnect.

Do not create agent-specific Atlas routes or schemas that bypass the published
agent integration contract.

---

# Connector Standards

Connectors are outside the active MVP. If a future accepted capability
reactivates them, every connector should:

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

## GitHub Actions free-tier discipline

GitHub Actions provides merge and release evidence. It is not the primary debugging loop.

For every source-bearing implementation:

1. Run focused local checks while iterating.
2. Before the first push, run the complete local Node, Python, PostgreSQL migration, test, lint, typecheck, and build validation represented in `.github/workflows/ci.yml`.
3. Record the commands and results in the pull request description.
4. Consolidate changes and push once per coherent review update. Do not push merely to discover failures in GitHub.
5. Keep work local until the full local suite is green. A draft pull request is not permission to spend hosted minutes on unfinished validation.
6. Do not manually rerun successful or superseded workflows.
7. Do not change CI workflows, required checks, branch protection, runner selection, deployment controls, credentials, or security scanning without explicit owner authorization.
8. Never weaken or bypass a required check because the Actions allowance is exhausted. Wait for the allowance reset or use an owner-approved self-hosted runner.

Until the path-aware `ci-gate` workflow is confirmed on `main`, assume every pushed pull request update may run the full hosted suite.

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

## Autonomous Delivery Continuation

When the Repository Maintainer explicitly authorizes autonomous delivery for a
set of accepted Work Orders, the assistant must carry that delivery through
without voluntary pauses. This includes implementing each dependency-ready Work
Order, validating it, creating its governed pull request, monitoring required
CI, merging after required CI passes, updating the local branch, and beginning
the next dependency-ready Work Order.

Do not stop merely because a pull request is open, CI is running, a merge has
completed, a status update has been sent, or a Work Order boundary has been
crossed. Status updates are commentary, not a handoff. Continue until every
authorized Work Order is complete or a genuine stop condition occurs.

The existing model-selection pause applies only before a new substantive Codex
task/session. Once the Repository Maintainer confirms the selected model and
authorizes autonomous delivery in that session, do not ask for another model
confirmation between Work Orders.

The assistant must still stop and request direction when a documented
stop-and-ask trigger applies, when new authority is required, when live
infrastructure or real credentials would be used, when a significant
architectural decision lacks an accepted authority, or when required CI fails.

## Project Status Reporting

When the user asks for status, use this compact format and update percentages
from repository evidence:

`**Completed:** Stage 6: Live Product Integration | 100%`

| Stage | Sequence | % |
|---|---|---:|
| 1. Engineering readiness | Accept ES-009 and Work Orders | 100% |
| 2. Honest active surface | Reduce navigation and quarantine simulations | 100% |
| 3. Enrollment | Agent registration and credentials | 100% |
| | Credential rotation and revocation | 100% |
| 4. Telemetry | Heartbeat ingestion | 100% |
| | Execution ingestion | 100% |
| 5. Health | Derived health evaluator | 100% |
| | Alert lifecycle | 100% |
| 6. Product | Live active dashboard surfaces | 100% |
| 7. Verification | Hosted reference-agent acceptance blocked on hosted API credential configuration | 0% |

---

# Long-Term Vision

The repository should evolve into an enterprise-quality agent operations
product demonstrating:

- Solution Architecture
- Enterprise Architecture
- AI Architecture
- Secure AI Systems
- Agent identity and trust lifecycle
- Agent integration contracts
- Agent Operations
- Observability
- Secure telemetry ingestion
- Honest control-plane boundaries

Human-in-the-loop workflows, production connectors, scheduling, orchestration,
and runtime control remain possible future capabilities rather than active MVP
commitments.

The quality of the architecture is more important than the quantity of implemented features.
