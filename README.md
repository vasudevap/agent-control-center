# Agent Control Center

> Designing and building an enterprise-inspired platform for creating, governing, and operating AI agents.

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

docs/
    architecture/
    decisions/
    specifications/
    diagrams/
    learning/
    linkedin/

agents/

backend/

dashboard/

infrastructure/

notion/

scripts/
```

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

The project is currently completing the Architecture Foundation phase.

The next milestone is establishing the repository standards, ADR process, and automated Notion workspace provisioning before implementation begins.

---

# License

This repository is currently intended for personal learning, portfolio development, and architectural research.
