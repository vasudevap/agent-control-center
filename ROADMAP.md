# Agent Control Center Roadmap

---

# Purpose

This roadmap defines the strategic evolution of the Agent Control Center.

It describes:

- major delivery phases
- architectural milestones
- learning objectives
- portfolio objectives

It intentionally does **not** define detailed implementation tasks.

Detailed implementation is managed through the Product Backlog.

---

# Vision

Create an enterprise-quality Agent Control Center capable of managing AI agents safely, consistently, and observably.

The project should become:

- a daily productivity platform
- an AI architecture learning laboratory
- a professional portfolio
- a reusable enterprise architecture reference

---

# Phase 1 — Architecture Foundation

## Objectives

Establish the architecture before implementation.

## Deliverables

- Project Charter
- Repository Standards
- Product Requirements
- Architecture Documentation
- Technology Strategy
- Security Architecture
- Data Architecture
- Runtime Architecture
- Connector Architecture
- Deployment Architecture
- Observability Architecture

## Status

Completed

---

# Phase 2 — Repository Foundation

## Objectives

Prepare the repository for implementation.

## Deliverables

- ADR Process
- Notion Provisioner
- Coding Standards
- Development Workflow
- GitHub Repository
- Repository Automation

## Status

Completed. ES-000 established and closed the canonical repository and frontend workspace. ES-001 established engineering governance, pull-request controls, continuous integration, release management, and dependency-risk tracking.

---

# Phase 3 — Platform Foundation

## Objectives

Build the platform infrastructure.

## Deliverables

- Backend
- Authentication
- PostgreSQL
- Migrations
- Configuration
- Health Endpoints
- Queue
- Scheduler
- Governed External Platform API Foundation
- External Product Client Authentication Boundary
- Outbound Webhook Delivery Foundation

---

# Phase 4 — Dashboard

## Objectives

Build the operational dashboard.

## Deliverables

- Dashboard
- Agent List
- Status Cards
- Logs
- Outputs
- Schedules
- Settings
- Dark Mode
- Responsive Layout

## Status

Completed for the frontend-only milestone. Work Orders 005 through 012 deliver
the application shell and the reviewed Agents, Agent Detail, Approvals, Runs,
Artifacts, Alerts, Audit, Connectors, Policies, and Settings surfaces. Work
Orders 013 and 014 complete cross-surface indicator and responsive consistency
maintenance. All related pull requests are merged.

WO-007 remains `Design Review Locked` and WO-008 remains `Frontend Prototype
Authorized` in their governing records. This phase status does not silently
close or broaden either artifact.

The current dashboard uses deterministic local fixtures and clearly labeled
simulations. It does not authorize or imply backend services, persistence,
authentication, connector calls, policy evaluation, runtime execution, or
operational audit storage.

---

# Phase 5 — Agent Framework

## Objectives

Create the reusable agent platform.

## Deliverables

- Agent Registry
- Runtime
- Tool Registry
- Connector Runtime
- Policies
- Approval Framework
- External Pending-Approval and Evidence API
- External Approve or Reject Decision API
- Approval-Pending and Send-Outcome Webhooks
- Held-for-Manual-Handling Non-Approval Webhook Contract
- External Decision Channel Audit Provenance
- Health Monitoring

---

# Phase 6 — Gmail Agent

## Objectives

Deliver the first production agent.

## Deliverables

- Gmail OAuth
- Gmail Connector
- Classification
- Clinical and PHI classification suppression with hold or manual handling
- Labels
- Archive
- Draft Replies
- Attachment Saving
- Google Drive Integration

## Phase 6 Safety Requirement

An inbound message classified as clinical or as containing protected health
information must not produce an automatic draft or an approvable send. The
Policy Engine must suppress drafting and route the message to a hold or manual
handling outcome. Human approval is not an override for this suppression.

This is a scope requirement for the future Gmail Agent and Policy Engine
Engineering Specifications. It does not authorize implementation in the
current frontend phase.

---

# Phase 7 — Operational Maturity

## Objectives

Improve reliability.

## Deliverables

- Retry Logic
- Error Recovery
- Better Logging
- Metrics
- Cost Monitoring
- Alerts
- Health Dashboard

---

# Phase 8 — Advanced Agentic Workflows

## Objectives

Evaluate more advanced AI frameworks.

Potential Deliverables

- LangChain
- LangGraph
- MCP
- LangSmith

Adoption depends on architectural need rather than project schedule.

---

# Phase 9 — Durable Orchestration

Potential Deliverables

- Temporal
- Long-running workflows
- Persistent checkpoints
- Human approval continuation
- Advanced scheduling

---

# Phase 10 — Additional Agents

Potential agents include:

- Calendar Agent
- Resume Agent
- Recruiter Agent
- Shopping Agent
- Finance Agent
- Travel Agent
- Document Filing Agent
- Local File Agent

---

# Phase 11 — Enterprise Features

Potential capabilities:

- RBAC
- Multi-user
- Multi-tenant
- Object Storage
- Secret Manager
- Advanced Monitoring
- Policy Engine
- Plugin Marketplace

---

# Learning Roadmap

Alongside implementation the project should develop practical experience in:

- Enterprise Architecture
- AI Architecture
- OAuth
- Security
- Observability
- LangChain
- LangGraph
- Temporal
- MCP
- OpenTelemetry
- AI Governance

---

# Portfolio Roadmap

The project should produce:

- Architecture diagrams
- ADRs
- Technology evaluations
- Public GitHub repository
- LinkedIn article series
- Demonstration videos
- Interview-ready examples

---

# Success Criteria

The roadmap is successful when:

- The platform becomes useful in daily work.
- Multiple agents operate through a shared control plane.
- The implementation reflects the documented architecture.
- Learning objectives are achieved.
- Portfolio assets demonstrate enterprise architecture capability.
