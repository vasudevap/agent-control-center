# System Context

## 1. Purpose

This document defines the system context for the Agent Control Center using a C4 Level 1 perspective.

The goal is to show:

- Who interacts with the platform
- Which external systems the platform depends on
- What responsibilities belong inside the Agent Control Center
- Where major trust boundaries exist
- How information flows between the platform and external services

---

## 2. System in Scope

The **Agent Control Center** is a centralized platform for registering, scheduling, executing, monitoring, governing, and auditing AI agents.

The platform provides one management layer for:

- Agent inventory
- Agent configuration
- Scheduling
- Manual execution
- Health monitoring
- Run history
- Logs
- Outputs
- Approvals
- Connectors
- Permissions
- Policies

The platform does not replace Gmail, Google Drive, Notion, or other external systems. It connects to them through controlled integrations.

---

## 3. Primary Actor

### Project Owner

The Project Owner is the initial user and administrator of the platform.

The Project Owner can:

- View all registered agents
- Activate, pause, disable, or run agents
- Configure schedules
- Review health and failures
- Review logs and outputs
- Approve or reject sensitive actions
- Manage connectors and credentials
- Review costs and usage
- Add or configure future agents

The initial solution is single-user, but the architecture should not prevent future support for multiple users and roles.

---

## 4. Future Actors

Future actors may include:

### Administrator

Manages:

- Platform configuration
- Users and roles
- Connectors
- Policies
- Secrets
- Agent deployment

### Operator

Manages:

- Agent schedules
- Agent status
- Failed runs
- Retries
- Operational issues

### Reviewer

Reviews:

- Approval requests
- Sensitive outputs
- Draft communications
- High-risk actions

### Read-Only User

Can view:

- Agent status
- Run history
- Logs
- Outputs
- Health

but cannot change configuration or approve actions.

---

## 5. External Systems

### 5.1 Gmail

The Agent Control Center connects to Gmail to:

- Read eligible emails
- Retrieve email metadata and content
- Apply labels
- Archive messages
- Create drafts
- Retrieve attachments
- Send messages only after approved workflows are implemented

Authentication:

- OAuth 2.0

Key security concerns:

- Least-privilege scopes
- Refresh token protection
- Sensitive message content
- Prompt injection through email content
- Outbound email approval

---

### 5.2 Google Drive

The Agent Control Center connects to Google Drive to:

- Save attachments
- Create folders
- Store outputs
- Organize generated artifacts
- Support synchronization to a local computer through Google Drive Desktop

Authentication:

- OAuth 2.0

Key security concerns:

- Folder-level access
- External sharing
- File retention
- Sensitive documents
- Malware or unsafe attachments

---

### 5.3 Notion

The Agent Control Center project uses Notion to maintain:

- Project dashboards
- Backlog
- Learning journal
- Architecture decision records
- Build log
- LinkedIn content pipeline
- Progress tracking

The initial Notion connection is used by the repository-based Notion provisioner.

Authentication:

- Internal Notion connection token

Key security concerns:

- Access limited to the designated parent page
- Token protection
- Avoiding destructive synchronization
- Preventing duplicate content

---

### 5.4 LLM Provider

The platform connects to one or more LLM providers to perform:

- Classification
- Summarization
- Draft generation
- Structured decision support
- Tool selection
- Workflow reasoning

Initial provider access will use a direct SDK.

Key security concerns:

- Data minimization
- Sensitive data exposure
- Prompt injection
- Invalid structured output
- Cost controls
- Model availability
- Provider lock-in

---

### 5.5 Identity Provider

A trusted identity provider authenticates the Project Owner.

Potential initial option:

- Google identity

The identity provider confirms who is accessing the dashboard, but the Agent Control Center remains responsible for authorization.

Key security concerns:

- Secure sessions
- Token validation
- Session expiry
- Reauthentication for sensitive actions
- Future role mapping

---

### 5.6 GitHub

GitHub stores:

- Source code
- Architecture documents
- ADRs
- Infrastructure definitions
- Version history
- Future CI/CD workflows

Key security concerns:

- Secret leakage
- Branch protection
- Dependency security
- Access control
- Supply-chain risk

---

### 5.7 Netlify

Netlify hosts the dashboard frontend.

Responsibilities:

- Serve the web interface
- Provide deployment previews
- Deliver static assets
- Route browser requests to the backend API

Netlify must not contain privileged backend credentials.

---

### 5.8 Render

Render hosts the main runtime platform.

Expected services include:

- Backend API
- Background workers
- Scheduler
- PostgreSQL
- Queue or key-value service

Render is part of the trusted hosting boundary but must still be configured using least privilege and environment separation.

---

### 5.9 Local Computer

The Project Owner's local computer is used for:

- Development
- Codex-assisted implementation
- Git operations
- Local testing
- Google Drive Desktop synchronization
- Reviewing downloaded files

The local computer is outside the hosted platform boundary.

Key security concerns:

- Local secrets
- File permissions
- Malware scanning
- Accidental Git commits
- Token storage
- Device compromise

---

## 6. System Context Diagram

```mermaid
flowchart LR
    Owner[Project Owner]

    subgraph ACC[Agent Control Center]
        Platform[Agent Control Center Platform]
    end

    Gmail[Gmail]
    Drive[Google Drive]
    Notion[Notion]
    LLM[LLM Provider]
    IdP[Identity Provider]
    GitHub[GitHub]
    Netlify[Netlify]
    Render[Render]
    Local[Local Computer]

    Owner -->|Manages agents, schedules, approvals, logs and outputs| Platform

    Platform -->|OAuth API calls| Gmail
    Platform -->|OAuth API calls| Drive
    Platform -->|API calls| LLM
    Platform -->|Authentication requests| IdP

    Local -->|Provisioning and synchronization| Notion
    Local -->|Source control| GitHub
    Local -->|Development and deployment| Netlify
    Local -->|Development and deployment| Render

    Netlify -->|Hosts dashboard| Platform
    Render -->|Hosts API, workers, database and scheduler| Platform
    Drive -->|Desktop synchronization| Local
```

---

## 7. Context Relationships

| Source               | Target               | Purpose                       | Data                                  |
| -------------------- | -------------------- | ----------------------------- | ------------------------------------- |
| Project Owner        | Agent Control Center | Manage and review agents      | Commands, approvals, configuration    |
| Agent Control Center | Gmail                | Email processing              | Messages, labels, drafts, attachments |
| Agent Control Center | Google Drive         | Store outputs and attachments | Files, folders, metadata              |
| Agent Control Center | LLM Provider         | AI reasoning                  | Prompts, structured inputs, outputs   |
| Agent Control Center | Identity Provider    | Authentication                | Identity claims, session tokens       |
| Local Computer       | Notion               | Provision workspace content   | Pages, databases, records             |
| Local Computer       | GitHub               | Version control               | Source code and documentation         |
| Netlify              | Project Owner        | Deliver dashboard             | Web interface                         |
| Render               | Agent Control Center | Host runtime services         | API, jobs, database operations        |
| Google Drive         | Local Computer       | Sync approved files           | Files and folders                     |

---

## 8. Trust Boundaries

### 8.1 User Device Boundary

Separates:

- Browser
- Local development environment
- Local file system

from hosted services.

Controls:

- Secure browser sessions
- Local secret protection
- Device security
- No privileged credentials in frontend code

---

### 8.2 Frontend-to-Backend Boundary

Separates:

- Netlify-hosted dashboard
- Render-hosted API

Controls:

- TLS
- Authentication
- Authorization
- CSRF protection where applicable
- Input validation
- Rate limiting
- Secure session handling

---

### 8.3 Platform-to-External-Service Boundary

Separates the Agent Control Center from:

- Gmail
- Google Drive
- LLM providers
- Notion
- Future connectors

Controls:

- OAuth or scoped tokens
- Least privilege
- Network encryption
- Request validation
- Response validation
- Rate-limit handling
- Connector-specific audit logs

---

### 8.4 Execution-to-Data Boundary

Separates:

- Workers and agent runtime
- PostgreSQL
- Queue
- Secrets

Controls:

- Service credentials
- Encryption
- Restricted network access
- Role-specific database permissions
- Secret references instead of plaintext storage

---

### 8.5 AI Decision-to-Action Boundary

Separates:

- LLM-generated recommendations
- Actual external side effects

Controls:

- Structured output schemas
- Policy validation
- Tool allowlists
- Confidence thresholds
- Human approval
- Idempotency
- Audit logging

This is one of the most important trust boundaries in the solution.

---

## 9. In-Scope Responsibilities

The Agent Control Center is responsible for:

- Agent registration
- Agent configuration
- Schedule management
- Triggering runs
- Tracking execution state
- Managing approvals
- Recording logs
- Recording audit events
- Storing output metadata
- Enforcing permissions
- Enforcing action policies
- Monitoring health
- Coordinating connectors
- Presenting operational information through the dashboard

---

## 10. Out-of-Scope Responsibilities

The Agent Control Center is not responsible for:

- Operating Gmail infrastructure
- Operating Google Drive
- Training foundation models
- Replacing external identity providers
- Providing general-purpose cloud storage
- Acting as an antivirus platform
- Guaranteeing external API availability
- Managing the operating system on the user's local computer
- Publishing directly to LinkedIn in the initial phases
- Supporting multiple organizations in the first MVP

---

## 11. Key Data Flows

### 11.1 Manual Agent Run

```text
Project Owner
    |
    v
Dashboard
    |
    v
Backend API
    |
    v
Create Run Record
    |
    v
Queue Job
    |
    v
Worker Executes Agent
    |
    v
External Services
    |
    v
Store Logs and Outputs
    |
    v
Dashboard Displays Result
```

---

### 11.2 Scheduled Agent Run

```text
Scheduler
    |
    v
Identify Due Agent
    |
    v
Create Run Record
    |
    v
Queue Job
    |
    v
Worker Executes Agent
    |
    v
Update Run and Health
```

---

### 11.3 Approval Flow

```text
Agent Proposes Sensitive Action
    |
    v
Policy Engine Flags Approval
    |
    v
Approval Record Created
    |
    v
Project Owner Reviews Request
    |
    +--> Reject
    |
    +--> Approve
             |
             v
        Execute Action
             |
             v
        Record Audit Event
```

---

### 11.4 Attachment Saving Flow

```text
Gmail Message
    |
    v
Attachment Retrieved
    |
    v
Type and Size Validation
    |
    v
Policy Check
    |
    v
Save to Google Drive
    |
    v
Record Output Metadata
    |
    v
Google Drive Desktop Syncs Locally
```

---

## 12. Security Assumptions

The initial architecture assumes:

- The Project Owner controls the connected Gmail and Google Drive accounts.
- The local development computer is trusted and kept secure.
- Netlify and Render are configured using separate environment variables.
- OAuth tokens are never exposed to the browser.
- High-risk actions are not automatically executed in the first MVP.
- The LLM is not trusted to authorize actions by itself.
- External content may be malicious and must be treated as untrusted input.
- Notion access is restricted to the designated project page hierarchy.

---

## 13. Risks at the System Boundary

Key risks include:

- Compromised OAuth tokens
- Prompt injection in emails or documents
- Excessive connector permissions
- Sensitive data sent to an LLM provider
- Unsafe or incorrect agent actions
- Malicious attachments
- External API outages
- Duplicate processing
- Accidental exposure of secrets in Git
- User approval fatigue
- Misconfigured cloud services

These risks will be addressed in the detailed security architecture.

---

## 14. Architecture Decisions Required

The system context identifies several decisions that should become ADRs:

- Dashboard hosting on Netlify
- Runtime hosting on Render
- PostgreSQL as the system of record
- Initial authentication provider
- Gmail OAuth scope strategy
- Google Drive folder strategy
- LLM provider abstraction
- Approval policy model
- Local file synchronization approach
- Control plane and execution plane separation

---

## 15. Current Status

- Primary user identified
- Initial external systems identified
- Core system boundary defined
- Major trust boundaries identified
- Initial data flows documented
- Detailed container architecture remains to be defined
