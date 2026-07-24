# Product Requirements Document

> **Status: Superseded for active product work.** This document is retained as
> the product record for the original Atlas execution-platform, Gmail,
> approvals, connectors, knowledge, and external-product-client direction.
> Active requirements are defined in
> [`atlas-agent-visibility-mvp-requirements.md`](./atlas-agent-visibility-mvp-requirements.md)
> under ADR-008 and ADR-009.

## 1. Product Name

Agent Control Center

## 2. Document Purpose

This document defines the product requirements for the Agent Control Center.

It describes:

- The problem being solved
- The intended users
- Product goals
- Functional requirements
- Non-functional requirements
- MVP scope
- Success criteria
- Constraints
- Risks
- Future capabilities

This document is the product-level source of truth for implementation planning.

---

## 3. Product Summary

The Agent Control Center is a centralized platform for creating, registering, scheduling, running, monitoring, governing, and reviewing AI agents.

The platform will provide one place to:

- View all agents
- Activate or pause agents
- Run agents manually
- Schedule recurring runs
- Review run history
- Review logs and outputs
- Approve sensitive actions
- Manage connectors and permissions
- Monitor health, failures, and cost
- Add new agents through a standard registration model

Atlas is consumed through its own dashboard and through one governed external
customer-facing product client. MushingMule is the first example of that external
client. Atlas exposes a general authenticated API and webhook contract and does
not depend on MushingMule-specific product concepts.

The first production use case will be a Gmail Triage Agent.

---

## 4. Product Objectives

The project has three primary objectives.

### 4.1 Productivity Objective

Create a useful personal productivity platform that reduces repetitive manual work.

### 4.2 Learning Objective

Develop practical expertise in:

- Agentic architecture
- AI orchestration
- Tool calling
- Human-in-the-loop workflows
- Security
- OAuth
- Observability
- Agent governance
- LLM integration
- Modern agent frameworks

### 4.3 Professional Objective

Create a portfolio-quality implementation and documentation set that demonstrates Enterprise and AI Solutions Architecture capability.

### 4.4 Platform Client Objective

Serve as the governed backend platform for one external customer-facing control
surface acting for the single human owner and reviewer through authenticated
APIs and webhooks.

---

## 5. Problem Statement

AI agents are often implemented as isolated scripts, prototypes, or automations.

As more agents are created, several problems emerge:

- Agents are difficult to discover
- Schedules are managed separately
- Logs are fragmented
- Failures are hard to diagnose
- Credentials and permissions are inconsistent
- Outputs are stored in different places
- Sensitive actions lack approval controls
- New agents duplicate infrastructure
- There is no unified operational view
- Governance and auditability are weak

The Agent Control Center addresses these problems through a shared control plane and standardized agent contracts.

---

## 6. Primary User

The initial user is the Project Owner.

The Project Owner needs to:

- See every available agent
- Know whether an agent is active or disabled
- Know when an agent last ran
- Know when an agent will run next
- Run an agent immediately
- Pause or disable an agent
- Review errors
- Review logs
- Review outputs
- Approve sensitive actions
- Manage connections
- Understand agent cost and health

The initial release is single-user.

---

## 7. Future Users

Future versions may support:

- Administrators
- Operators
- Reviewers
- Read-only users
- Small teams
- Consulting teams
- Enterprise architecture teams
- Business operations teams

Multi-user support is not part of the first MVP.

---

## 8. User Experience Principles

The interface should be:

- Clear
- Modern
- Responsive
- Accessible
- Consistent
- Easy to scan
- Safe by default
- Suitable for light and dark mode

Important information should be visible without opening multiple screens.

Status, risk, and errors should not rely on colour alone.

---

## 9. Primary User Journeys

## 9.1 View All Agents

The user opens the dashboard and sees:

- Agent name
- Description
- Status
- Health
- Last run
- Next run
- Schedule
- Current issue
- Quick actions

## 9.2 Run an Agent Manually

The user:

1. Selects an agent
2. Clicks Run Now
3. Confirms configuration if required
4. Watches the run status
5. Reviews the final output

## 9.3 Schedule an Agent

The user:

1. Selects an agent
2. Opens schedule settings
3. Selects frequency and time zone
4. Saves the schedule
5. Sees the calculated next-run time

## 9.4 Pause or Disable an Agent

The user:

1. Opens the agent
2. Selects Pause or Disable
3. Confirms the action
4. Sees the updated state

## 9.5 Review a Failed Run

The user:

1. Opens the failed agent
2. Opens the failed run
3. Reviews the timeline
4. Reviews the error
5. Reviews affected outputs
6. Retries or dismisses the issue

## 9.6 Review an Approval

The user:

1. Opens the Approvals screen
2. Reviews the exact proposed action
3. Reviews risk and context
4. Approves or rejects it
5. Sees the final execution result

## 9.7 Manage a Connector

The user:

1. Opens Connectors
2. Selects Gmail or Google Drive
3. Connects or reconnects the service
4. Reviews granted permissions
5. Tests connection health
6. Revokes access when required

---

## 10. MVP Scope

The MVP includes:

- Responsive dashboard
- User authentication
- Agent Registry
- Agent status management
- Manual Run Now
- Basic scheduling
- Run history
- Run details
- Structured logs
- Output metadata
- Approval queue
- Governed external platform API for one product client
- External-client authentication
- Outbound platform webhooks
- Connector management
- Gmail OAuth
- Google Drive integration
- Gmail Triage Agent
- Basic health monitoring
- Light and dark mode
- Deployment to Netlify and Render

---

## 11. MVP Exclusions

The MVP does not include:

- Multi-tenant SaaS
- Billing
- Public plugin marketplace
- Native desktop application
- Native mobile application
- Automatic high-risk outbound actions
- Enterprise SSO
- Complex multi-agent collaboration
- Temporal
- Full LangGraph workflow support
- Arbitrary local filesystem access
- LinkedIn publishing automation
- Advanced analytics
- Multiple external product clients

---

## 12. Functional Requirements

## 12.1 Authentication

The system shall:

- Authenticate the Project Owner
- Restrict access to approved identities
- Support logout
- Expire sessions
- Require reauthentication for sensitive actions where configured

---

## 12.2 Agent Registry

The system shall:

- Register agents
- Assign unique agent IDs
- Store agent metadata
- Store agent version
- Store status
- Store risk classification
- Store required connectors
- Store allowed tools
- Store configuration schema
- Display registered agents automatically

---

## 12.3 Agent Status Management

The user shall be able to:

- Activate an agent
- Pause an agent
- Disable an agent
- View agent health
- View current issues

The system shall prevent disabled agents from starting new runs.

---

## 12.4 Manual Execution

The user shall be able to run an active agent manually.

The system shall:

- Create a run record
- Queue the run
- Track status
- Prevent accidental duplicate execution
- Display the result

---

## 12.5 Scheduling

The user shall be able to:

- Create a recurring schedule
- Create a one-time schedule
- Pause a schedule
- Resume a schedule
- Modify a schedule
- View next-run time

The system shall:

- Store time zones
- calculate next-run time
- Prevent invalid schedules
- Prevent duplicate scheduled runs

---

## 12.6 Run Management

The system shall record:

- Run ID
- Agent
- Trigger type
- Start time
- End time
- Status
- Duration
- Retry count
- Error summary
- Output summary
- Cost estimate

---

## 12.7 Run States

Supported run states shall include:

- Pending
- Queued
- Running
- Waiting for Approval
- Succeeded
- Partially Succeeded
- Failed
- Cancelled
- Timed Out

---

## 12.8 Logs

The system shall:

- Record structured logs
- Associate logs with runs
- Filter logs by severity
- Display a run timeline
- Redact sensitive values
- Support correlation IDs

---

## 12.9 Outputs

The system shall:

- Record output metadata
- Associate outputs with runs
- Display output type
- Display output status
- Link to stored files where applicable
- Apply access controls
- Avoid unsafe inline rendering

---

## 12.10 Approvals

The system shall:

- Create approval requests
- Display exact proposed actions
- Display risk level
- Display destination or recipient
- Allow approval
- Allow rejection
- Expire approvals
- Prevent duplicate execution
- Record reviewer and decision time

---

## 12.11 Connector Management

The system shall:

- Register connector types
- Create connection instances
- Support OAuth
- Display connection status
- Display granted scopes
- Test connector health
- Support reconnection
- Support revocation
- Prevent agents from accessing unapproved connectors

---

## 12.12 Gmail Agent

The Gmail Triage Agent shall initially support:

- Retrieve eligible messages
- Read sender
- Read subject
- Read selected message content
- Classify email
- Identify clinical content and protected health information classifications
- Apply labels
- Archive approved low-risk categories
- Create draft replies
- Retrieve attachments
- Save approved attachments to Google Drive
- Record all actions
- Route sensitive actions to approvals
- Suppress automatic drafting for inbound messages classified as clinical or
  as containing protected health information
- Route suppressed clinical or protected health information messages to a hold
  or manual-handling outcome without creating an approvable send

---

## 12.13 Email Categories

Initial email categories shall include:

- Family
- Friends
- Work
- Recruiters
- Shopping
- Subscriptions
- Receipts
- Travel
- Personal Administration
- Needs Reply
- Review Required
- Unknown
- Clinical
- Protected Health Information

Categories should be configurable later.

Clinical and Protected Health Information are safety classifications, not
ordinary routing categories. If either applies to an inbound message, the
Policy Engine shall suppress automatic drafting and shall route the message to
a hold or manual-handling outcome. The Gmail agent shall not create a draft,
send proposal, or approval request for that message. Human approval shall not
override this rule.

---

## 12.14 Safe Automatic Actions

The system may automatically perform approved low-risk actions such as:

- Apply a label
- Mark classification
- Archive approved newsletters
- Save an approved attachment
- Create a draft
- Generate a summary

---

## 12.15 High-Risk Actions

The system shall require approval before:

- Sending an email
- Deleting an email
- Forwarding an email
- Unsubscribing
- Sharing files externally
- Performing an unfamiliar or unsupported action

---

## 12.16 Health Monitoring

The system shall display:

- Agent health
- Connector health
- Last successful run
- Last failed run
- Consecutive failures
- Current issue
- Platform health

---

## 12.17 Notifications

The MVP shall support dashboard notifications for:

- Agent failures
- Pending approvals
- Connector expiry
- Missed scheduled runs
- Repeated failures

---

## 12.18 Settings

The user shall be able to configure:

- Time zone
- Theme
- Notification preferences
- Default scheduling behaviour
- Retention preferences where supported

---

## 12.19 External Product Client Access

Atlas shall expose a governed platform contract to one authenticated external
product client acting for the single human owner and reviewer.

The contract shall allow the external product client to:

- Read the pending-approval queue.
- Read the governed evidence required to decide an approval.
- Read agent status.
- Read run status.
- Submit one approve or reject decision through the Approval Service boundary.
- Receive an approval-pending webhook event.
- Receive send-outcome webhook events, including explicit indeterminate outcomes
  where Atlas cannot establish whether an approved send completed.
- Receive a `message.held_for_manual_handling` webhook event when the Policy
  Engine suppresses a clinical or protected-health-information message.

Atlas shall:

- Authenticate the external product client separately from the first-party
  dashboard session.
- Attribute an external approval decision to the single human reviewer as well
  as the authenticated external client and decision channel.
- Apply the same approval state, evidence, expiry, concurrency, reauthentication,
  idempotency, continuation, and audit controls used by the Atlas dashboard.
- Expose only the minimum evidence required for the governed operation.
- Treat webhooks as authenticated notifications rather than authorization or an
  authoritative substitute for API reconciliation.
- Remain the sole system of record for platform state, approvals, execution
  outcomes, and audit evidence.
- Keep the contract generic and independent of MushingMule.
- Identify a held message through a governed source reference and include only
  the reason category and minimum metadata required to route it to the human.
- Exclude message content and other sensitive evidence unless a later approved
  contract establishes that the field is necessary and permitted.
- Record the hold reason, policy or classification provenance, authenticated
  external client, external delivery channel, correlation identity, and event
  timestamp in audit evidence.
- Ensure a held-message event contains no draft, creates no approval request,
  confers no authorization, and cannot override or bypass suppression.
- Require the external product client to present the event as `Needs manual
  handling`, not as an approval.

This requirement does not introduce additional human reviewers, roles, tenants,
multi-tenant isolation, billing, marketplace behavior, or multiple external
product clients. Those capabilities require separate future product and
architecture decisions.

---

## 12.20 R8 Draft-Support Knowledge and Ask-Instead-of-Guess

R8 is one requirement with two sequenced parts. Part A establishes the generic
platform and external-client contract in Phases 3 and 5. Part B establishes the
Gmail agent behavior that consumes that contract in Phase 6. Neither part
authorizes implementation independently or together.

### Part A: External API and Platform Scope

Atlas shall provide a governed knowledge store for business facts used during
drafting, such as hours, services, pricing, and policies. Atlas remains the
authoritative system of record for this capability. The one authenticated
external product client acting for the single human owner shall be able to:

- Create, read, update, and delete a fact.
- Confirm a fact.
- Mark a fact as volatile and read its `last_confirmed_at` value.
- Find stale volatile facts that require re-confirmation.
- Read an ask-instead-of-guess question and submit an answer for the one human
  owner.
- Reconcile question and answer state through the authenticated API after
  receiving an authenticated webhook notification.

Questions and answers are first-class records. They are not approvals, confer
no authorization, and are distinct from approve or reject decisions and from
the existing approval Request clarification lifecycle.

Facts used by a draft fit within the existing approval evidence contract. The
evidence payload shall add a typed `facts_used` collection rather than add a new
top-level approval or decision field. Each entry shall bind the displayed fact
to the exact fact revision used by the draft and include minimum necessary
confirmation and volatility context. The decision-context manifest shall retain
the version or integrity reference required to show what the human reviewed. A
changed, deleted, or stale fact that invalidates the draft shall fail
revalidation and require a regenerated draft and new approval request.

The external-client contract shall use deny-by-default authorization, validated
inputs and outputs, correlation identities, idempotency where state changes,
and durable audit provenance. Atlas shall never store secrets, credentials, or
protected health information in the knowledge store. A message suppressed as
clinical or protected-health-information content, and any content derived from
that message, shall be excluded before knowledge retrieval, question creation,
history learning, or fact persistence.

### Part B: Gmail Agent Scope

The Gmail agent shall:

- Emit an ask-instead-of-guess question when a required fact is missing instead
  of producing a generic draft.
- Treat the answer as untrusted input, validate it against policy and
  sensitivity rules, and persist the resulting business fact only when the
  knowledge-store rules permit it.
- Derive candidate facts only from past approved sends with a confirmed `Sent`
  outcome, with source provenance and policy validation.
- Apply the clinical and protected-health-information filter before any
  history-learning input is assembled, so a suppressed message or its content
  can never become a learning source.
- Avoid creating a draft, approval, knowledge question, or learned fact for a
  suppressed clinical or protected-health-information message.

Part A is sequenced across Phase 3 platform foundations and Phase 5 governed
knowledge, evidence, question, answer, and webhook contracts. Part B is
sequenced to Phase 6. R8 does not introduce additional human reviewers, users,
roles, tenants, multiple external product clients, or client-specific product
concepts.

---

## 13. Non-Functional Requirements

## 13.1 Security

The system must:

- Use least privilege
- Deny unauthorized actions by default
- Encrypt sensitive credentials
- Protect OAuth tokens
- Validate all external input
- Validate all LLM output
- Prevent secrets from entering logs
- Require approval for high-risk actions
- Maintain audit records
- Authenticate and scope an external product client separately from the
  first-party dashboard
- Preserve external-client and human attribution for approval decisions

---

## 13.2 Availability

The MVP should be available for normal personal use.

Formal high-availability targets are not required initially.

The system should fail safely when external services are unavailable.

---

## 13.3 Reliability

The system should:

- Prevent duplicate actions
- Support retries
- Detect partial success
- Preserve run history
- Support manual recovery
- Use idempotency controls

---

## 13.4 Performance

Initial targets:

- Dashboard pages should load within approximately two seconds under normal conditions
- API responses should normally complete within one second, excluding long-running work
- Agent runs should execute asynchronously
- Long operations must not block the dashboard

---

## 13.5 Scalability

The MVP shall support:

- One user
- Multiple registered agents
- Low to moderate run volume
- Independent worker scaling later

The architecture should not block future multi-user support.

---

## 13.6 Accessibility

The dashboard should:

- Support keyboard navigation
- Provide visible focus states
- Use accessible labels
- Meet reasonable contrast standards
- Avoid colour-only status indicators
- Support responsive text sizing

---

## 13.7 Responsiveness

The dashboard shall support:

- Desktop
- Tablet
- Mobile browser

Desktop is the primary design target.

---

## 13.8 Maintainability

The implementation should:

- Use typed interfaces
- Use modular components
- Follow documented contracts
- Include tests
- Avoid duplicated business logic
- Keep architecture documentation current

---

## 13.9 Observability

The system shall provide:

- Structured logs
- Correlation IDs
- Run history
- Health status
- Error categorization
- Model usage
- Cost estimates
- Connector status

---

## 13.10 Privacy

The platform should:

- Minimize stored email content
- Avoid retaining full prompts by default
- Restrict access to stored attachments
- Support configurable retention
- Avoid sending unnecessary personal data to LLM providers

---

## 14. Data Requirements

The platform shall maintain data for:

- Users
- Roles
- Agents
- Agent versions
- Schedules
- Runs
- Run steps
- Approvals
- Connectors
- Credential references
- Tools
- Policies
- Outputs
- Logs
- Audit events
- Health
- Model invocation metadata
- Notifications

PostgreSQL is the runtime system of record.

---

## 15. Integration Requirements

Initial integrations:

- Google Identity
- One governed external product client, initially MushingMule
- Gmail API
- Google Drive API
- LLM provider API
- Notion API
- GitHub
- Netlify
- Render

All external integrations must use defined connector or gateway boundaries.

---

## 16. Security Requirements

The system shall:

- Use secure authentication
- Use server-side authorization
- Protect session tokens
- Use least-privilege OAuth scopes
- Encrypt stored refresh tokens
- Support token revocation
- Redact logs
- Validate files
- Treat external content as untrusted
- Treat LLM output as untrusted
- Maintain append-oriented audit records
- Support emergency agent disablement

---

## 17. Operational Requirements

The platform shall support:

- Health checks
- Manual retry
- Agent disablement
- Schedule pause
- Connector reconnection
- Error inspection
- Deployment version visibility
- Database backups
- Controlled migrations
- Environment separation

---

## 18. Success Metrics

MVP success metrics include:

- At least one production Gmail agent
- All agents visible in the dashboard
- Manual Run Now works
- Scheduled execution works
- Agent status is visible
- Logs are accessible
- Outputs are accessible
- Approvals work
- Gmail classification is usable
- Low-risk actions execute safely
- High-risk actions require approval
- No credentials are exposed
- At least one LinkedIn article is published
- Architecture and implementation remain synchronized

---

## 19. Learning Metrics

The project should produce:

- Architecture documents
- ADRs
- Technology evaluations
- Build logs
- Learning journal entries
- Framework experiments
- Security reviews
- Published professional content

---

## 20. Portfolio Deliverables

Portfolio assets should include:

- System context diagram
- Container diagram
- Component diagram
- Security architecture
- Data model
- Agent lifecycle
- Working dashboard
- Gmail Agent demo
- Approval-flow demo
- Architecture Decision Records
- LinkedIn article series
- Public repository documentation where appropriate

---

## 21. Constraints

Current constraints include:

- Single primary user
- Limited budget
- Netlify and Render hosting familiarity
- Personal Gmail data sensitivity
- Local Mac development environment
- Incremental learning approach
- Avoiding unnecessary enterprise infrastructure
- Limited initial operational support capacity

---

## 22. Dependencies

The MVP depends on:

- Google OAuth configuration
- Gmail API availability
- Google Drive API availability
- LLM provider availability
- Render services
- Netlify
- PostgreSQL
- GitHub
- Notion API for project provisioning

---

## 23. Major Risks

Key risks include:

- Overengineering before delivering value
- Excessive OAuth permissions
- Unsafe model-driven actions
- Prompt injection
- Duplicate execution
- Sensitive data leakage
- Framework lock-in
- Uncontrolled model cost
- Poor error recovery
- Incomplete auditability
- Excessive documentation without implementation progress

---

## 24. Risk Mitigations

Mitigations include:

- Plain Python first
- Least-privilege OAuth
- Human approval
- Tool allowlists
- Structured output validation
- Idempotency
- Cost budgets
- Incremental delivery
- ADRs
- Security reviews
- Observability
- MVP scope discipline

---

## 25. Delivery Milestones

### Milestone 1: Architecture Foundation

- Project charter
- Architecture baseline
- Repository standards
- PRD
- ADR process
- Roadmap

### Milestone 2: Notion Provisioning

- Workspace specification
- Provisioning tool
- Databases
- Seed records
- Synchronization

### Milestone 3: Platform Foundation

- Backend
- Database
- Authentication
- Governed external platform API foundation
- External-client authentication boundary
- Outbound webhook delivery foundation
- Initial deployment
- Health endpoints

### Milestone 4: Agent Operations

- Agent Registry
- Run management
- Scheduling
- Workers
- Logs
- Outputs

### Milestone 5: Governance

- Connectors
- Policies
- Approvals
- External pending-approval and evidence access
- External approve or reject decision channel
- Approval-pending and send-outcome webhooks
- Held-for-manual-handling non-approval webhook contract
- Audit events
- Security controls

### Milestone 6: Gmail Agent

- Gmail OAuth
- Classification
- Labels
- Archive
- Drafts
- Attachments
- Drive storage

### Milestone 7: Operational MVP

- Dashboard polish
- Error handling
- Monitoring
- Production deployment
- Documentation
- Demo

---

## 26. Future Capabilities

Potential future capabilities include:

- Calendar Agent
- Recruiter Agent
- Resume Agent
- Shopping Agent
- Document Filing Agent
- Travel Agent
- Finance and Receipt Agent
- LangGraph workflows
- Temporal orchestration
- MCP tools
- Multi-user RBAC
- Agent templates
- Plugin marketplace
- Model routing
- Advanced cost management
- Local desktop bridge
- Mobile application
- Multi-product platform for multiple external product clients

---

## 27. Open Product Decisions

The following decisions remain open:

- Authentication implementation
- Queue implementation
- Initial LLM provider
- UI component library
- Gmail message-selection rules
- Classification confidence thresholds
- Approval expiry rules
- Log retention
- Output retention
- Initial notification approach
- Exact MVP deployment tiers

These decisions should be resolved through analysis and ADRs.

---

## 28. Acceptance of This Document

This PRD becomes the basis for:

- ROADMAP.md
- Product backlog
- Notion workspace structure
- User stories
- Acceptance criteria
- Codex implementation prompts
- MVP scope decisions

Changes to the product scope should update this document.
