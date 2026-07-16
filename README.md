# Atlas

> Enterprise Agent Control Center and unified control plane for AI workforces.

---

# Vision

The Agent Control Center is a practical productivity platform and an applied AI architecture laboratory.

It has three complementary goals:

1. Build a personal productivity platform powered by AI agents.
2. Develop deep expertise in enterprise agentic architecture, governance, orchestration, and operations.
3. Produce architecture documentation and implementation examples that demonstrate enterprise AI architecture skills.

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
│   ├── web/                  # Atlas control-center application
│   └── site/                 # Public Atlas product website
├── docs/
│   ├── architecture/
│   ├── design/
│   ├── specifications/
│   ├── engineering-specifications/
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

`apps/web` contains the Atlas control-center frontend. Its approved prototypes
cover the application shell, operational overview, agent inventory and detail,
agent controls, and Human Approvals. These experiences use fictional local data;
business APIs, authentication, backend services, and production agent behavior
remain future work.

`apps/site` contains the public Atlas website authorized by Work Order 010. It
explains the product, architecture, and delivery status without sharing the
future authenticated product boundary.

From the repository root:

```bash
npm ci
npm run dev
npm run dev:site
npm run typecheck
npm run lint
npm test
npm run build
```

Product component tests use Vitest, React Testing Library, and jsdom. The public
site adds rendered-output checks against its production worker build. Run
`npm test` for the canonical all-workspace suite or
`npm --workspace @atlas/web run test:watch` during local development. Tests are
colocated with product feature code using the `*.test.ts` or `*.test.tsx` suffix.

ES-000 is closed. ES-001 establishes the engineering-governance and continuous-integration baseline for subsequent approved work.

# Engineering Governance and CI

Repository changes follow the [Atlas engineering-governance handbook](./docs/governance/README.md), including the [branching strategy](./docs/governance/branching-strategy.md), [pull-request process](./docs/governance/pull-request-and-review-process.md), [Definition of Ready](./docs/governance/definition-of-ready.md), and [Definition of Done](./docs/governance/definition-of-done.md).

GitHub Actions runs `npm ci`, typecheck, lint, tests, and production builds for
both frontend workspaces on pull requests targeting `main` and pushes to `main`.

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

See:

```
docs/architecture/
```

---

# Current Technology Direction

| Area                   | Technology               |
| ---------------------- | ------------------------ |
| Frontend               | Next.js + TypeScript     |
| Public Site            | Next.js-compatible vinext + TypeScript |
| Backend                | FastAPI + Python         |
| Database               | PostgreSQL               |
| Hosting                | OpenAI Sites + Netlify + Render |
| Agent Runtime          | Plain Python (initially) |
| LLM                    | Direct Provider SDK      |
| Authentication         | Google Identity          |
| External Authorization | OAuth 2.0                |
| Documentation          | Markdown + Notion        |

Frameworks such as LangChain, LangGraph, MCP, and Temporal will be introduced only when architectural requirements justify their adoption.

---

# Project Roadmap

High-level phases:

- Phase 1 — Architecture Foundation
- Phase 2 — Notion Workspace Automation
- Phase 3 — Platform Foundation
- Phase 4 — Dashboard
- Phase 5 — Agent Registry
- Phase 6 — Scheduler
- Phase 7 — Gmail Agent
- Phase 8 — Deployment
- Phase 9 — Advanced Agentic Workflows
- Phase 10 — Additional Agents

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

The architecture and product-design foundations are documented. `apps/web`
contains the approved frontend prototypes, while `apps/site` provides the
independently deployable public product narrative. ES-000 is closed and ES-001
provides the governance and CI baseline. Production application behavior still
requires reviewed work orders and engineering specifications.

---

# License

This repository is currently intended for personal learning, portfolio development, and architectural research.
