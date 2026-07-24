# Technology Strategy

> **Legacy broad technology baseline.** Next.js, FastAPI, PostgreSQL, Netlify,
> Render, tests, and migrations remain active. Queue, agent runtime frameworks,
> connector execution, and orchestration are deferred for the active MVP.

## 1. Purpose

This document defines the technology strategy for the Agent Control Center.

It explains:

- Which technologies are selected initially
- Why they are appropriate for the MVP
- Which technologies are intentionally deferred
- How future tools such as LangChain, LangGraph, Temporal, MCP, and OpenTelemetry fit into the architecture
- How technology choices will be evaluated and governed

The objective is to avoid technology-driven design while preserving a clear path to more advanced agentic capabilities.

---

## 2. Technology Strategy Principles

The project will follow these principles:

1. Choose technologies based on requirements, not market popularity.
2. Prefer simple and explicit implementations for the MVP.
3. Minimize framework lock-in.
4. Keep platform contracts independent of agent frameworks.
5. Use managed services where they reduce operational burden.
6. Introduce new infrastructure only when a clear architectural need exists.
7. Document significant choices through Architecture Decision Records.
8. Evaluate security, cost, operability, and learning value together.
9. Preserve portability where practical.
10. Reassess decisions as the platform and use cases mature.

---

## 3. Initial Technology Baseline

| Capability                | Initial Technology                                            |
| ------------------------- | ------------------------------------------------------------- |
| Frontend                  | Next.js and TypeScript                                        |
| Frontend Hosting          | Netlify                                                       |
| Backend API               | FastAPI and Python                                            |
| Backend Hosting           | Render                                                        |
| Database                  | PostgreSQL                                                    |
| Scheduling                | Render Cron Jobs                                              |
| Background Execution      | Render Background Workers                                     |
| Queue                     | PostgreSQL-backed queue initially or Redis-compatible service |
| Agent Runtime             | Plain Python                                                  |
| LLM Integration           | Direct provider SDK                                           |
| Authentication            | Google Identity or equivalent                                 |
| External Authorization    | OAuth 2.0                                                     |
| File Storage              | Google Drive                                                  |
| Documentation             | Markdown and Notion                                           |
| Source Control            | GitHub                                                        |
| Database Migrations       | Alembic                                                       |
| API Validation            | Pydantic                                                      |
| ORM                       | SQLAlchemy                                                    |
| Testing                   | Pytest and frontend test tooling                              |
| Infrastructure Definition | Render and Netlify configuration initially                    |
| Observability             | Structured logs and database metrics initially                |

---

## 4. Frontend Strategy

## 4.1 Next.js

Next.js is the initial frontend framework.

Reasons:

- Strong React ecosystem
- TypeScript support
- Good routing and application structure
- Server and client rendering options
- Mature deployment support
- Suitable for responsive dashboards
- Strong portfolio relevance

The dashboard should remain a presentation and interaction layer.

It should not:

- Store secrets
- Execute agents
- Authorize sensitive actions independently
- Connect directly to Gmail or Google Drive
- contain privileged business logic

## 4.2 TypeScript

TypeScript is required for frontend code.

Benefits:

- Stronger contracts
- Safer refactoring
- Better editor support
- Improved API integration
- Clearer component interfaces

Use strict TypeScript configuration.

## 4.3 UI Component Strategy

A component library should be selected later through an ADR.

Evaluation criteria:

- Accessibility
- Dark-mode support
- Responsive behaviour
- Customization
- Bundle size
- Design quality
- Long-term maintenance

Candidate options may include:

- shadcn/ui
- Radix UI
- Material UI
- Chakra UI

The dashboard should not be tightly coupled to a proprietary visual framework.

---

## 5. Backend Strategy

## 5.1 FastAPI

FastAPI is the initial backend framework.

Reasons:

- Strong Python support
- Async capabilities
- Pydantic integration
- Automatic API documentation
- Clear endpoint definitions
- Good fit with AI and agent libraries
- Strong developer productivity

## 5.2 Python

Python is the primary backend and agent language.

Reasons:

- Dominant AI ecosystem
- Strong SDK availability
- Familiarity across agent frameworks
- Good support for automation and integration
- Suitable for FastAPI and background workers

Python code should use:

- Type hints
- Async where justified
- Clear package boundaries
- Static checking
- Automated tests
- Explicit error handling

## 5.3 Pydantic

Pydantic should define:

- API request models
- API response models
- Agent configuration schemas
- Tool schemas
- Connector schemas
- LLM structured outputs
- Queue messages

This supports validation at system boundaries.

## 5.4 SQLAlchemy and Alembic

SQLAlchemy will manage relational persistence.

Alembic will manage schema migrations.

Requirements:

- No ad hoc production schema changes
- Migration history in Git
- Backward-compatible changes where possible
- Explicit rollback planning
- Tests for important migrations

---

## 6. Database Strategy

## 6.1 PostgreSQL

PostgreSQL is the primary system of record.

Reasons:

- Strong transactional consistency
- Relational integrity
- JSONB where limited flexibility is needed
- Mature indexing
- Good hosting support
- Strong ecosystem
- Suitable for runtime state and audit data

PostgreSQL will store:

- Agents
- Versions
- Schedules
- Runs
- Steps
- Approvals
- Connector metadata
- Policies
- Health
- Outputs
- Audit events
- Model invocation metadata

It should not become a default store for large files or unnecessary raw email content.

## 6.2 JSONB Usage

Use JSONB for:

- Agent configuration
- Policy definitions
- Connector configuration
- Structured model metadata
- Extensible output values

Do not use JSONB to avoid proper relational modelling where integrity matters.

---

## 7. Queue Strategy

## 7.1 Initial Option: PostgreSQL-Backed Queue

A PostgreSQL-backed queue is appropriate when:

- Workload is low
- The platform is single-user
- Simplicity is more important than throughput
- Reducing infrastructure is valuable

Benefits:

- Fewer services
- Easier local setup
- Transactional relationship with run records
- Lower MVP complexity

Risks:

- Database contention
- Less specialized queue functionality
- Scaling limitations

## 7.2 Future Option: Redis-Compatible Queue

Redis becomes useful when:

- Worker concurrency grows
- Queue latency matters
- Throughput increases
- More mature background-job libraries are needed
- Queue isolation becomes operationally valuable

The queue decision should be made through an ADR before implementation.

---

## 8. Scheduling Strategy

## 8.1 Render Cron Jobs

Render Cron Jobs are sufficient initially.

Use them to:

- Run the scheduler periodically
- Query due schedules
- Create run records
- Publish jobs

This is simple and inexpensive.

## 8.2 Limitations

Render Cron alone does not provide:

- Durable workflow state
- Long approval waits
- Complex retries
- Rich workflow histories
- Cross-service orchestration

These limitations are acceptable for the MVP.

## 8.3 Future Orchestration

Temporal should be evaluated when durable workflow execution becomes a requirement.

---

## 9. Agent Runtime Strategy

## 9.1 Plain Python First

The first Gmail agent should be implemented using plain Python.

Reasons:

- Clear control flow
- Easier learning
- Easier debugging
- Minimal dependencies
- Stronger understanding of underlying agent patterns
- Avoid framework-driven architecture

Plain Python is appropriate for:

- Fixed workflows
- Classification
- Tool execution
- Policy checks
- Safe low-risk actions
- Draft creation

## 9.2 Runtime Adapter Boundary

The platform should define a runtime adapter interface so future frameworks can be introduced without changing the control plane.

Potential adapters:

- Plain Python
- LangGraph
- Temporal
- External agent service

---

## 10. Direct LLM SDK Strategy

Use a direct model-provider SDK initially.

The LLM Gateway should still abstract:

- Provider
- Model
- Prompt version
- Structured output
- Token usage
- Cost
- Retry
- Timeout
- Validation

This avoids premature dependency on an agent framework while preserving provider abstraction.

---

## 11. LangChain Strategy

LangChain should not be part of the first MVP by default.

Use LangChain when:

- Reusable tool abstractions become repetitive
- Prompt composition becomes complex
- Retrieval pipelines are introduced
- Multiple model providers require common handling
- Existing LangChain integrations materially reduce implementation effort

Do not use LangChain merely to call an LLM or invoke one or two tools.

LangChain should remain behind platform interfaces.

---

## 12. LangGraph Strategy

LangGraph should be evaluated when agents require:

- Branching workflows
- Persistent state
- Checkpoints
- Loops
- Pause and resume
- Human approval
- Multi-stage reasoning
- Long-lived workflow state

Potential use cases:

- Recruiter and job-application agent
- Resume-tailoring workflow
- Multi-step travel-planning workflow
- Email workflow that waits for approval before sending

LangGraph should be introduced through a runtime adapter.

---

## 13. Temporal Strategy

Temporal should be evaluated when the platform requires:

- Durable execution across infrastructure failures
- Workflows lasting hours or days
- Complex retry policies
- Durable timers
- Reliable approval waits
- Cross-service coordination
- Strong execution history
- Mission-critical workflow guarantees

Temporal is an orchestration platform, not an AI reasoning framework.

LangGraph and Temporal may coexist:

- LangGraph manages agent state and reasoning
- Temporal manages durable workflow execution

This combination should only be adopted when justified.

---

## 14. Model Context Protocol Strategy

Model Context Protocol should be evaluated as a standard interface for exposing tools and context to models or agent runtimes.

Potential benefits:

- Standardized tool integration
- Reusable connector exposure
- Reduced provider coupling
- Easier interoperability
- Strong portfolio and learning value

Potential risks:

- Added abstraction
- Security complexity
- Tool discovery concerns
- Ecosystem maturity
- Need for permission controls

MCP should be introduced as an experiment before becoming a core platform dependency.

---

## 15. Multi-Agent Framework Strategy

Frameworks such as CrewAI and AutoGen may be evaluated for learning and experimentation.

Potential use cases:

- Role-based multi-agent collaboration
- Research and review workflows
- Architecture critique
- Content-generation teams
- Complex planning tasks

They should not be introduced into the core platform until:

- A real multi-agent requirement exists
- Failure modes are understood
- Governance is defined
- Cost and observability are available
- Agent responsibilities are explicit

---

## 16. Authentication Strategy

The initial platform should use a trusted identity provider.

Candidate:

- Google Identity

Reasons:

- Existing Google ecosystem
- Single-user initial deployment
- Familiar authentication flow
- Strong security controls

The application remains responsible for:

- Session management
- Authorization
- Role mapping
- Resource access
- Reauthentication for sensitive actions

---

## 17. OAuth Strategy

OAuth 2.0 will be used for Gmail and Google Drive.

Requirements:

- Authorization Code flow
- PKCE where applicable
- Least-privilege scopes
- Secure token storage
- Revocation
- Scope visibility
- Reconnection
- Separate development and production OAuth clients

OAuth implementation should use a mature library rather than custom protocol code.

---

## 18. File Storage Strategy

## 18.1 Google Drive Initially

Google Drive is appropriate initially because:

- It is already part of the user workflow
- It supports folder organization
- It supports local synchronization
- It avoids building direct local filesystem access
- It reduces infrastructure complexity

## 18.2 Future Object Storage

Move to object storage when:

- File volume grows
- Retention controls become more important
- Multiple users are supported
- Storage independence is required
- Signed URLs and lifecycle policies are needed

Potential options may include:

- Amazon S3
- Cloudflare R2
- Google Cloud Storage
- Azure Blob Storage

---

## 19. Local File Access Strategy

The hosted platform should not directly access arbitrary local folders.

Initial bridge:

```text
Google Drive
  |
  v
Google Drive Desktop
  |
  v
Approved Local Folder
```

A dedicated local agent may be considered later.

It would require:

- Explicit folder allowlists
- Secure authentication
- Narrow local API
- No arbitrary command execution
- Local audit logs
- Controlled updates
- User-controlled shutdown

---

## 20. Hosting Strategy

## 20.1 Netlify

Use Netlify for:

- Frontend hosting
- Preview deployments
- CDN
- Static assets
- Next.js dashboard delivery

## 20.2 Render

Use Render for:

- FastAPI
- Workers
- Scheduler
- PostgreSQL
- Queue service where selected

## 20.3 Hosting Reassessment Triggers

Reassess hosting when:

- Cost becomes inefficient
- Private networking is required
- Compliance requirements increase
- Multi-region support is needed
- Service limits are reached
- Operational complexity justifies consolidation
- Enterprise identity or network integration is required

---

## 21. Docker Strategy

Docker should be introduced early enough to ensure reproducible local and hosted environments.

Use Docker for:

- Backend
- Workers
- Scheduler
- Local PostgreSQL
- Local queue
- Integration testing

Benefits:

- Consistent environments
- Easier onboarding
- Reduced deployment drift
- Better CI/CD support

Do not containerize the project merely for appearance. Use it where it improves repeatability.

---

## 22. Monorepo Strategy

The project should remain a monorepo initially.

Suggested top-level areas:

```text
backend/
dashboard/
agents/
notion/
docs/
infrastructure/
scripts/
tests/
```

Benefits:

- Shared versioning
- Easier Codex context
- Unified architecture documentation
- Coordinated releases
- Simpler portfolio presentation

A multi-repository strategy is unnecessary at this stage.

---

## 23. Notion Provisioner Strategy

The Notion provisioner should use the official Notion SDK.

Recommended language:

- TypeScript

Reasons:

- Strong official SDK support
- Existing repository frontend language
- Good schema handling
- Good Codex support

The provisioner should:

- Read Markdown and YAML
- Create pages and databases
- Maintain a manifest
- Support dry run
- Be idempotent
- Avoid deletion by default
- Record unsupported manual steps

---

## 24. Documentation Strategy

The repository is the technical source of truth.

Use:

- Markdown for architecture and specifications
- Mermaid for diagrams
- ADRs for decisions
- Notion for project operations and learning
- Git history for change tracking

Documentation should be updated in the same change as implementation where practical.

---

## 25. Testing Strategy

### Backend

- Pytest
- Contract tests
- Integration tests
- API tests
- Connector mocks and sandboxes

### Frontend

- Component tests
- Accessibility tests
- API integration tests
- Responsive testing
- End-to-end tests later

### Infrastructure

- Configuration validation
- Deployment smoke tests
- Migration tests
- Secret scanning

### Agent testing

- Prompt regression
- Structured output validation
- Tool contract testing
- Policy testing
- Replay and idempotency testing
- Failure simulation

---

## 26. Observability Technology Strategy

### MVP

Use:

- Structured JSON logs
- Render logs
- PostgreSQL run history
- Health endpoints
- Cost and token metadata
- Correlation IDs

### Future

Evaluate:

- OpenTelemetry
- Central log platform
- Metrics backend
- Trace backend
- LangSmith
- Error-monitoring platform

OpenTelemetry should become the standard instrumentation layer when multiple services require end-to-end tracing.

---

## 27. Security Tooling Strategy

Initial tooling should include:

- Dependency scanning
- Secret scanning
- Static analysis
- Automated tests
- Package version locking
- GitHub security features where available

Future tooling may include:

- Container scanning
- Software bill of materials
- Dynamic application security testing
- Infrastructure policy checks
- Vulnerability management

---

## 28. Technology Evaluation Criteria

Each significant technology should be evaluated against:

| Criterion       | Description                             |
| --------------- | --------------------------------------- |
| Functional Fit  | Does it satisfy the requirement?        |
| Security        | Does it support required controls?      |
| Reliability     | Can it recover and operate predictably? |
| Operability     | Can it be monitored and maintained?     |
| Complexity      | Does it add justified complexity?       |
| Cost            | Is cost predictable and proportionate?  |
| Portability     | Can it be replaced if necessary?        |
| Ecosystem       | Is documentation and support strong?    |
| Learning Value  | Does it support project learning goals? |
| Portfolio Value | Does it demonstrate relevant skills?    |
| Maturity        | Is it stable enough for the use case?   |

---

## 29. Architecture Decision Record Process

Create an ADR when:

- A new framework is introduced
- A hosting decision is made
- A system of record is selected
- A security model changes
- A connector scope changes
- A new data store is introduced
- A major abstraction is added
- A technology is rejected after evaluation

Each ADR should include:

- Context
- Decision drivers
- Considered options
- Decision
- Consequences
- Risks
- Revisit triggers

---

## 30. Initial ADR Candidates

Initial ADRs should include:

1. Use Netlify for the dashboard
2. Use Render for backend services
3. Use PostgreSQL as the runtime system of record
4. Use a monorepo
5. Use plain Python for the first agent
6. Do not introduce LangChain in the first MVP
7. Introduce LangGraph only for stateful workflows
8. Require human approval for high-risk actions
9. Use Google Drive as the initial file-storage bridge
10. Separate the control plane and execution plane
11. Use an agent registry for discovery
12. Use direct provider SDKs through an LLM Gateway

---

## 31. Technology Adoption Phases

### Phase 1: Foundation

Use:

- Markdown
- Notion
- GitHub
- TypeScript
- Python
- PostgreSQL
- FastAPI
- Next.js

### Phase 2: MVP Platform

Add:

- Netlify
- Render
- Scheduler
- Workers
- Gmail OAuth
- Google Drive
- Direct LLM SDK

### Phase 3: Operational Maturity

Add as needed:

- Redis
- Docker
- OpenTelemetry
- Central monitoring
- Object storage
- Stronger secrets management

### Phase 4: Advanced Agentic Workflows

Evaluate:

- LangChain
- LangGraph
- MCP
- LangSmith

### Phase 5: Durable Enterprise Orchestration

Evaluate:

- Temporal
- Enterprise identity
- Multi-user RBAC
- Private networking
- Managed secrets
- Advanced compliance controls

---

## 32. Technology Risks

Key risks include:

- Framework lock-in
- Introducing too many tools too early
- Excessive infrastructure cost
- Underestimating OAuth complexity
- Fragile provider integrations
- Poor library maintenance
- Inconsistent observability
- Hidden data-retention behaviour
- Dependency vulnerabilities
- Architecture becoming driven by tutorials rather than requirements

---

## 33. Reassessment Triggers

Technology decisions should be reassessed when:

- Scale changes materially
- Multiple users are introduced
- Reliability requirements increase
- Security requirements change
- Costs become disproportionate
- Vendor capabilities change
- A framework no longer satisfies requirements
- Operational support becomes difficult
- New regulations apply
- A better standard emerges

---

## 34. Learning Strategy

Technology adoption should include:

1. Understand the underlying architectural problem
2. Build a minimal version without a framework where practical
3. Evaluate the framework
4. Implement a small experiment
5. Compare complexity and benefits
6. Record the decision in an ADR
7. Document lessons in Notion
8. Convert useful lessons into LinkedIn content

This approach ensures that tools are learned through applied architecture rather than isolated tutorials.

---

## 35. Current Technology Decisions

The following are currently accepted as the initial direction:

- Next.js for the dashboard
- TypeScript for frontend and Notion provisioning
- FastAPI and Python for backend and agents
- PostgreSQL for runtime data
- Netlify for frontend hosting
- Render for backend services
- Google Drive for initial file storage
- Plain Python for the first agent
- Direct LLM provider SDK through a gateway
- Markdown and Notion for documentation and learning

All other major technologies remain subject to evaluation and ADR approval.

---

## 36. Open Decisions

The following require further analysis:

- UI component library
- PostgreSQL queue versus Redis
- Authentication library
- OAuth library
- Initial LLM provider and model
- Prompt-management approach
- Docker adoption timing
- CI/CD tooling
- Error-monitoring provider
- OpenTelemetry backend
- LangSmith adoption
- MCP experiment scope
- LangGraph implementation point
- Temporal implementation point
- Object-storage provider

---

## 37. Current Status

- Initial technology baseline defined
- Framework adoption strategy established
- Hosting strategy documented
- Learning and evaluation process defined
- Initial ADR candidates identified
- Detailed technology evaluations and ADRs remain to be created
