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
- Governed Knowledge Store Persistence Foundation
- External Knowledge API Foundation

## Status

In progress. The backend foundation, owner identity/session boundary,
PostgreSQL migration foundation, hosted deployment path, and Agent Visibility
MVP service layer through WO-070 are implemented. Queue, Scheduler, broader
multi-user authentication, and operational platform services remain future
increments.

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
- Governed Knowledge Fact CRUD and Confirmation Contract
- Fact Volatility and Re-confirmation Contract
- Approval Evidence `facts_used` Contract
- Ask-Instead-of-Guess Question and Answer API
- Knowledge Question, Answer, and Re-confirmation Webhook Contracts
- Health Monitoring

## Status

In progress. ES-009 and ADP-006 re-scoped the active MVP to honest Agent
Visibility and Trust Lifecycle behavior. WO-064 through WO-070 are merged:
active navigation is rooted under `/control-center`, owner-enrolled agents use
one-time Atlas telemetry credentials, external runtimes can submit heartbeats
and executions, Atlas derives observed health and alerts, and owners can rotate
credentials, disconnect, reconnect, and archive without Atlas claiming runtime
control.

WO-071 hosted reference-agent verification is blocked until the production
Render API environment is provisioned with the missing agent credential pepper
settings.

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
- Ask-Instead-of-Guess Before Drafting
- Learn Governed Facts From Human Answers
- Learn Governed Facts From Confirmed Approved Sends
- Attachment Saving
- Google Drive Integration

## Phase 6 Safety Requirement

An inbound message classified as clinical or as containing protected health
information must not produce an automatic draft or an approvable send. The
Policy Engine must suppress drafting and route the message to a hold or manual
handling outcome. Human approval is not an override for this suppression.

This is a scope requirement for the Gmail Agent and Policy Engine engineering
scope. It does not authorize any future release behavior that bypasses the
accepted suppression gate.

R8 applies the same suppression before knowledge retrieval, question creation,
or learning from history. A suppressed clinical or
protected-health-information message and its content must never become a
knowledge fact or learning source. Ask-instead-of-guess questions are not
approvals and confer no authorization.

---

# Phase 7 — Operational Maturity

## Objectives

Make the Gmail Agent MVP Candidate operable for normal single-owner personal
use on the approved deployment path, with release evidence, runbooks, recovery
paths, monitoring, and accepted residual risk.

## Deliverables

- Controlled-account release verification or accepted deferral
- Dashboard productization for MVP-critical operator workflows
- Environment, OAuth, and secrets readiness
- Netlify and Render deployment and migration readiness
- Health, readiness, logs, metrics, alerts, and recovery paths
- Release runbooks and rollback
- MVP release candidate validation
- MVP acceptance and Phase 7 closeout

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
