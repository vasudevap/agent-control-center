# Atlas

> Enterprise Agent Control Center and unified control plane for AI workforces.

---

# Vision

The Agent Control Center is a practical productivity platform and an applied AI architecture laboratory.

It has four complementary goals:

1. Build a personal productivity platform powered by AI agents.
2. Develop deep expertise in enterprise agentic architecture, governance, orchestration, and operations.
3. Produce architecture documentation and implementation examples that demonstrate enterprise AI architecture skills.
4. Serve as the governed backend platform for one external customer-facing product client acting for the single human owner and reviewer.

Rather than building isolated AI scripts, the project focuses on building the infrastructure required to manage AI agents safely and consistently.

---

# Project Objectives

The platform will eventually provide:

- Agent Registry
- Agent Dashboard
- Scheduling
- Manual Execution
- Health Monitoring
- Logs
- Outputs
- Approval Workflows
- Plugin Management
- Connector Framework
- Authentication
- Authorization
- Audit Logging
- Cost Monitoring
- Observability
- AI Governance
- Governed External Product API and Webhooks

The first production agent will be a Gmail Triage Agent.

---

# Architecture Philosophy

The project follows several core principles:

- Architecture before implementation
- Security by design
- Human approval for high-risk actions
- Least privilege
- Separation of control plane and execution plane
- Framework independence
- Progressive complexity
- Documentation as a deliverable
- Learning through implementation

---

# Repository Structure

```text
agent-control-center/
├── apps/
│   ├── api/                  # Approved Atlas FastAPI backend foundation
│   └── web/                  # Approved Atlas Next.js frontend baseline
├── docs/
│   ├── architecture/
│   ├── design/
│   ├── specifications/
│   ├── engineering-specifications/
│   ├── implementation-plans/
│   ├── governance/
│   ├── work-orders/
│   ├── reviews/
│   ├── decisions/
│   ├── recommendations/
│   └── references/
├── .claude/                 # Claude-specific guidance
├── AGENTS.md                # Tool-neutral repository guidance
├── PROJECT.md
└── ROADMAP.md
```

---

# Current Implementation

`apps/web` now serves a public Atlas landing page at `/` and the authenticated
Agent Visibility MVP under `/control-center`. Active product navigation is
limited to Overview, Agents, Executions, Alerts, and Activity. Legacy prototype
surfaces remain quarantined outside the active navigation.

`apps/api` contains the FastAPI backend foundation, owner identity/session
boundary, PostgreSQL migrations, owner-enrolled agent registry, one-time agent
credential issuance, authenticated heartbeat and execution ingestion, derived
health evaluation, alert lifecycle, activity, and owner-controlled lifecycle
actions for credential rotation, disconnect, reconnect, and archive.

Atlas remains a visibility and trust-lifecycle control center. It does not
host, deploy, schedule, execute, pause, resume, stop, or maintain external
agent runtimes.

ADP-006 has merged WO-064 through WO-070. WO-071 hosted reference-agent
verification is blocked until the production Render API environment is
provisioned with `ATLAS_API_AGENT_CREDENTIAL_PEPPER` and
`ATLAS_API_AGENT_CREDENTIAL_PEPPER_KEY_ID`; do not record secret values in the
repository, logs, screenshots, pull request text, or chat.

From the repository root:

```bash
npm ci
npm run dev
npm run typecheck
npm run lint
npm test
npm run build
```

The backend foundation lives in `apps/api`. From the repository root:

```bash
python3 -m venv apps/api/.venv
apps/api/.venv/bin/python -m pip install --upgrade pip
apps/api/.venv/bin/python -m pip install -c apps/api/constraints.txt -e "apps/api[dev]"
apps/api/.venv/bin/python -m pytest apps/api
apps/api/.venv/bin/python -m ruff check apps/api
apps/api/.venv/bin/python -m mypy apps/api/src
cd apps/api
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m alembic downgrade base
```

Alembic migration validation requires a developer-managed PostgreSQL 18
database and an uncommitted `ATLAS_API_DATABASE_URL`; see
[`apps/api/README.md`](./apps/api/README.md) for the canonical local commands.
GitHub Actions runs the migration smoke check against an ephemeral PostgreSQL 18
service using disposable synthetic CI data.

`apps/api/constraints.txt` is the canonical resolved backend dependency input
for local and CI installs. Update it intentionally from a clean Python 3.12
environment after the backend validation suite passes. The API uses the
`ATLAS_API_` configuration prefix; its default `local` environment requires no
database, while `staging`, `production`, or `ATLAS_API_REQUIRE_DATABASE=true`
require `ATLAS_API_DATABASE_URL` for readiness.

Frontend component tests use Vitest, React Testing Library, and jsdom. Run
`npm test` for the canonical one-shot suite or
`npm --workspace @atlas/web run test:watch` during local development. Tests are
colocated with feature code using the `*.test.ts` or `*.test.tsx` suffix.

ES-000 is closed. ES-001 establishes the engineering-governance and
continuous-integration baseline for subsequent approved work. ES-009 governs
the current Agent Visibility and Lifecycle MVP; ADP-006 remains blocked at
WO-071 hosted verification until the hosted credential configuration gap is
resolved.

# Engineering Governance and CI

Repository changes follow the [Atlas engineering-governance handbook](./docs/governance/README.md), including the [branching strategy](./docs/governance/branching-strategy.md), [pull-request process](./docs/governance/pull-request-and-review-process.md), [Definition of Ready](./docs/governance/definition-of-ready.md), and [Definition of Done](./docs/governance/definition-of-done.md).

GitHub Actions runs frontend validation, backend typecheck, backend lint,
backend tests, backend migration validation, and the production frontend build
for pull requests targeting `main` and pushes to `main`.

---

# Current Architecture Documentation

The architecture documentation currently includes:

- Executive Summary
- Architecture Principles
- System Context
- Container Architecture
- Component Architecture
- Deployment Architecture
- Security Architecture
- Data Architecture
- Agent Runtime
- Connector Framework
- Observability
- Technology Strategy
- Human Approvals

See:

```
docs/architecture/
```

Cross-work-order implementation planning lives under:

```text
docs/implementation-plans/
```

---

# Current Technology Direction

| Area                   | Technology               |
| ---------------------- | ------------------------ |
| Frontend               | Next.js + TypeScript     |
| Backend                | FastAPI + Python         |
| Database               | PostgreSQL               |
| Hosting                | Netlify + Render         |
| Agent Runtime          | Plain Python (initially) |
| LLM                    | Direct Provider SDK      |
| Authentication         | Google Identity          |
| External Authorization | OAuth 2.0                |
| Documentation          | Markdown + Notion        |

Frameworks such as LangChain, LangGraph, MCP, and Temporal will be introduced only when architectural requirements justify their adoption.

---

# Project Roadmap

High-level phases:

- Phase 1 - Architecture Foundation
- Phase 2 - Repository Foundation
- Phase 3 - Platform Foundation
- Phase 4 - Dashboard
- Phase 5 - Agent Framework
- Phase 6 - Gmail Agent
- Phase 7 - Operational Maturity
- Phase 8 - Advanced Agentic Workflows
- Phase 9 - Durable Orchestration
- Phase 10 - Additional Agents
- Phase 11 - Enterprise Features

---

# Learning Goals

This repository is intentionally used to learn:

- Enterprise AI Architecture
- Agent Design
- Agent Governance
- LangChain
- LangGraph
- Temporal
- MCP
- OAuth
- Security Architecture
- Observability
- Prompt Engineering
- AI Operations
- AI Product Design

Every implementation should improve both the platform and the author's architectural understanding.

---

# Documentation Standards

Architecture documentation is maintained before implementation.

Major decisions are documented through Architecture Decision Records (ADRs).

The Git repository is the technical source of truth.

Notion serves as the operational workspace for:

- Backlog
- Learning Journal
- Build Log
- Architecture Review
- LinkedIn Content Pipeline
- Project Progress

---

# Current Status

The architecture, product design, engineering governance, hosted foundation,
owner identity boundary, and Agent Visibility MVP through WO-070 are documented
and merged. The work-order index preserves the exact status of each delivery
artifact, including WO-071 as blocked on hosted API credential configuration.

ADR-008 and ADR-009 govern the active Atlas Agent Visibility MVP: Atlas is not
an agent runtime host or scheduler, and active lifecycle controls remain bounded
to enrollment, telemetry trust, health, alerts, activity, credential rotation,
disconnect, reconnect, and archive.

---

# License

This repository is currently intended for personal learning, portfolio development, and architectural research.
