# Agent Control Center

## 1. Project Purpose

The Agent Control Center is a practical productivity platform and applied AI architecture laboratory.

The project has three primary objectives:

1. Build a useful platform for creating, scheduling, monitoring, governing, and operating AI agents.
2. Develop hands-on proficiency in agentic architecture, orchestration, security, observability, governance, and modern AI development tools.
3. Create portfolio and LinkedIn content that demonstrates enterprise architecture thinking and practical AI implementation experience.

## 2. Product Vision

Create a centralized control plane where users can:

- View all registered agents.
- Activate, pause, disable, or run agents on demand.
- Schedule recurring and one-time agent executions.
- Review agent health, status, next run, last run, and current issues.
- Access logs, outputs, links, generated artifacts, and execution history.
- Review and approve high-risk actions.
- Manage integrations, plugins, credentials, and permissions.
- Add future agents without redesigning the dashboard.
- Operate agents through a consistent lifecycle and governance model.

## 3. Initial Use Case

The first production agent will be a Gmail Triage Agent.

It will eventually:

- Connect securely to Gmail using OAuth.
- Classify emails into categories such as family, friends, work, recruiters, shopping, subscriptions, receipts, and travel.
- Apply Gmail labels.
- Archive selected low-risk emails.
- Create draft replies.
- Save attachments to approved storage locations.
- Route sensitive actions through a human approval process.
- Record decisions, actions, outputs, and errors.

## 4. Target Users

### Primary User

The initial primary user is the project owner.

### Future Users

The architecture should support future use by:

- Individual professionals.
- Small consulting teams.
- Enterprise architecture teams.
- Operations teams managing internal AI agents.
- Organizations requiring governed agent execution.

## 5. Core Capabilities

The platform should provide:

- Agent registry
- Agent lifecycle management
- Scheduling and orchestration
- Manual run capability
- Execution history
- Centralized logging
- Output and artifact management
- Approval workflows
- Plugin and connector management
- Authentication and authorization
- Secret and credential management
- Health monitoring
- Error handling and retries
- Cost and usage tracking
- Versioning
- Auditability
- Responsive dashboard
- Light and dark modes

## 6. Design Principles

The solution will follow these principles:

- Architecture before implementation
- Least-privilege access
- Human approval for high-risk actions
- Separation of control plane and agent execution
- Clear system-of-record ownership
- Explicit audit trails
- Modular and extensible components
- Frameworks introduced only when justified
- Secure-by-design implementation
- Observable and recoverable operations
- Version-controlled documentation
- Incremental delivery
- Learning documented alongside implementation

## 7. Initial Scope

The initial project scope includes:

- Notion workspace provisioner
- Project documentation
- Architecture decision records
- Responsive dashboard
- Backend API
- PostgreSQL database
- Agent registry
- Scheduler
- Worker execution model
- Central logging
- Approval queue
- Gmail integration
- Gmail Triage Agent
- Google Drive attachment storage
- Deployment to Netlify and Render

## 8. Out of Scope for the First MVP

The first MVP will not include:

- Multi-tenant SaaS support
- Billing and subscription management
- Public plugin marketplace
- Fully autonomous outbound communication
- Automatic deletion of sensitive content
- Enterprise SSO
- Complex multi-agent collaboration
- Temporal orchestration
- LangGraph workflows
- Native desktop application
- Native mobile application

These may be introduced later through documented architecture decisions.

## 9. Success Criteria

The MVP will be considered successful when:

- The dashboard displays all registered agents.
- An agent can be activated, paused, disabled, and run manually.
- Scheduled runs execute reliably.
- Run status, last run, next run, logs, and outputs are visible.
- The Gmail Agent can classify and label emails.
- Safe actions can execute automatically.
- High-risk actions require explicit approval.
- Every agent action is auditable.
- Credentials are not exposed in code or logs.
- The platform is deployed and accessible.
- Architecture, decisions, lessons, and build progress are documented.
- At least one LinkedIn article is published based on the project.

## 10. Learning Objectives

The project will be used to develop practical knowledge of:

- Agent architecture
- LLM tool calling
- Agent workflows
- LangChain
- LangGraph
- Temporal
- Model Context Protocol
- OAuth
- API security
- Secrets management
- PostgreSQL
- Redis and queues
- FastAPI
- Next.js
- Docker
- Render
- Netlify
- Observability
- OpenTelemetry
- LangSmith
- Human-in-the-loop design
- AI governance
- Prompt and model evaluation
- Production AI operations

## 11. Career and Portfolio Outcomes

The project should demonstrate the ability to:

- Design an enterprise-inspired AI control plane.
- Translate business needs into architecture.
- Define trust boundaries and security controls.
- Govern agent permissions and actions.
- Build auditable AI workflows.
- Evaluate agent frameworks objectively.
- Implement production-oriented integrations.
- Communicate architecture through diagrams, ADRs, documentation, and articles.
- Bridge enterprise architecture and hands-on engineering.

## 12. Delivery Approach

The project will be delivered in phases:

1. Vision and requirements
2. Architecture
3. Notion workspace provisioner
4. Core platform foundation
5. Dashboard
6. Agent registry
7. Scheduling and execution
8. Logging and approvals
9. Gmail integration
10. Gmail Triage Agent
11. Deployment
12. Advanced agentic capabilities
13. Additional agents
14. Portfolio and LinkedIn publication

## 13. Source of Truth

The Git repository is the technical source of truth for:

- Architecture documentation
- ADRs
- Specifications
- Source code
- Infrastructure configuration
- Notion workspace definitions

Notion is the operational and learning workspace for:

- Progress tracking
- Backlog management
- Learning journal
- Build log
- Architecture review
- Article pipeline
- Project dashboards

## 14. Current Status

- Architecture, product requirements, brand, and product-design foundations are documented.
- The canonical repository structure is established around `apps/web` and governed documentation under `docs/`.
- The approved Work Order 005 Atlas application shell is implemented with responsive light and dark themes and placeholder routes.
- Backend, authentication, APIs, connectors, and business workflows remain future work subject to architecture and work-order approval.
