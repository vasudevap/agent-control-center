# Security Architecture

> **Legacy broad security baseline.** Reusable controls remain valid. The active
> agent trust boundary and per-agent credential model are governed by ADR-009
> and the Agent Visibility MVP Target Architecture.

## 1. Purpose

This document defines the security architecture for the Agent Control Center.

It establishes the controls required to protect:

- User identity
- Gmail and Google Drive access
- OAuth tokens
- Agent configurations
- Agent actions
- Logs and outputs
- Personal information
- Infrastructure
- Source code
- LLM interactions

The security model is based on least privilege, explicit trust boundaries, human approval, auditability, and secure defaults.

---

## 2. Security Objectives

The platform should:

- Prevent unauthorized access
- Prevent agents from exceeding approved permissions
- Protect credentials and tokens
- Treat LLM output as untrusted
- Prevent unsafe autonomous actions
- Minimize retained personal data
- Preserve complete auditability
- Detect failures and suspicious activity
- Support token revocation and credential rotation
- Isolate development and production environments
- Fail safely when dependencies are unavailable

---

## 3. Security Principles

The following principles apply across the platform:

1. Least privilege
2. Deny by default
3. Human approval for high-risk actions
4. Defense in depth
5. Explicit trust boundaries
6. Data minimization
7. Secure secret storage
8. Strong input and output validation
9. Auditable actions
10. Separation of duties
11. Safe failure
12. Environment isolation

---

## 4. Protected Assets

The main protected assets are:

| Asset                 | Sensitivity    | Protection Requirement                   |
| --------------------- | -------------- | ---------------------------------------- |
| OAuth refresh tokens  | Critical       | Encrypt and restrict access              |
| LLM API keys          | Critical       | Store only in secret configuration       |
| Database credentials  | Critical       | Restrict to backend services             |
| Session tokens        | High           | Secure cookies and short lifetime        |
| Gmail message content | High           | Minimize retention and exposure          |
| Email attachments     | High           | Validate, classify, and restrict         |
| Google Drive files    | High           | Enforce approved folders and scopes      |
| Agent configuration   | Medium to High | Protect from unauthorized change         |
| Governed knowledge    | High           | Validate, version, minimize, and restrict |
| Approval records      | High           | Preserve integrity and reviewer identity |
| Audit logs            | High           | Prevent tampering and redact secrets     |
| User profile data     | High           | Limit collection and access              |
| Source code           | Medium         | Protect repository and dependencies      |

---

## 5. Threat Actors

Potential threat actors include:

### External attacker

May attempt to:

- Steal credentials
- Compromise the dashboard
- Exploit API vulnerabilities
- Gain access to Gmail or Drive
- Trigger agent actions
- Exfiltrate data

### Malicious or compromised external content

Emails, attachments, web pages, or documents may contain:

- Prompt injection
- Malicious links
- Malware
- Misleading instructions
- Social engineering content

Human-supplied knowledge answers and facts are also untrusted input. They may
contain secrets, credentials, protected health information, incorrect business
facts, or content derived from a policy-suppressed source.

### Misconfigured agent

An agent may:

- Use excessive permissions
- Apply incorrect actions
- Process unintended data
- Create excessive costs
- Enter retry loops

### Compromised dependency

A software package, connector, model provider, or hosting dependency may be compromised.

### Authorized user error

The Project Owner may accidentally:

- Approve an unsafe action
- Configure excessive permissions
- expose a token
- deploy insecure settings
- disable a required safeguard

---

## 6. Trust Boundaries

### 6.1 Browser to API

The browser is not trusted to enforce authorization.

Controls:

- HTTPS
- Server-side authentication
- Server-side authorization
- Request validation
- Rate limiting
- Secure cookies
- CSRF protection where applicable

### 6.2 API to Database

Only approved backend services may access the database.

Controls:

- Private connection
- TLS
- Restricted credentials
- Connection pooling
- Query parameterization
- Migration control

### 6.3 API and Scheduler to Queue

Queue messages are treated as untrusted until validated.

Controls:

- Authenticated access
- Message schemas
- Idempotency keys
- Minimal payloads
- No secrets in messages

### 6.4 Workers to External Services

Workers cross the platform boundary when calling Gmail, Google Drive, and LLM providers.

Controls:

- OAuth scopes
- Credential isolation
- Timeouts
- Rate limits
- Response validation
- Audit logging

### 6.5 LLM Decision to External Action

LLM recommendations must never directly authorize external actions.

Controls:

- Structured output
- Action validation
- Policy evaluation
- Tool allowlists
- Human approval
- Idempotency

### 6.6 Local Development to Production

Development tools must not have uncontrolled access to production.

Controls:

- Separate credentials
- Separate databases
- Separate environment variables
- Explicit deployment process
- No production secrets in local files where avoidable

### 6.7 External Product Client to Knowledge Capability

The Atlas dashboard and the one governed external product client are untrusted
presentation clients. Atlas remains authoritative for knowledge state,
validation, confirmation, provenance, policy, and audit evidence.

Controls:

- Separate external-client authentication from attribution to the one human
  owner
- Deny-by-default authorization by resource and action
- Validated and versioned fact, question, and answer contracts
- Idempotency for state-changing requests
- Prohibited-content rejection before knowledge-store persistence
- Clinical and protected-health-information suppression before retrieval,
  question creation, history-learning input assembly, or persistence
- Minimum-necessary API, webhook, audit, and approval-evidence payloads
- Authenticated webhooks that notify but never authorize
- Authoritative API reconciliation after webhook delivery
- Correlation identities and durable audit provenance

---

## 7. Authentication Architecture

## 7.1 User Authentication

The initial platform should use a trusted identity provider, such as Google Identity.

The authentication flow should:

1. Redirect the user to the identity provider
2. Validate the returned identity token
3. Create an application session
4. Store the session in a secure HTTP-only cookie
5. Expire the session after a defined period
6. Require reauthentication for sensitive actions

## 7.2 Session Controls

Sessions should use:

- HTTP-only cookies
- Secure flag
- SameSite protection
- Rotation after authentication
- Idle timeout
- Absolute timeout
- Server-side invalidation
- Logout support

Avoid storing sensitive tokens in browser local storage.

## 7.3 Initial User Restriction

The first production release should allow only the Project Owner's approved identity.

Future multi-user access should require explicit role and tenant design.

---

## 8. Authorization Architecture

## 8.1 Role-Based Authorization

Initial roles:

- Owner
- Administrator
- Operator
- Reviewer
- Read Only

The MVP may enable only the Owner role but should preserve the role model.

## 8.2 Policy-Based Authorization

Authorization decisions should consider:

- User role
- Resource ownership
- Agent
- Connector
- Action type
- Risk level
- Environment
- Approval status

## 8.3 Deny by Default

Any action without an explicit permission or policy outcome should be denied.

---

## 9. Agent Authorization

Each agent must declare:

- Required connectors
- Required permissions
- Allowed tools
- Risk level
- Approval policy
- Data access scope

Example:

```json
{
  "agent_id": "gmail-triage",
  "allowed_tools": [
    "gmail.read_message",
    "gmail.apply_label",
    "gmail.archive_message",
    "gmail.create_draft"
  ],
  "denied_tools": ["gmail.delete_message", "gmail.send_message"]
}
```

An agent must not receive a general-purpose connector client with unrestricted access.

---

## 10. OAuth Security

## 10.1 Scope Strategy

Use the least powerful scopes that satisfy the approved use case.

The Gmail implementation should begin with read and modification capabilities required for:

- Reading selected messages
- Applying labels
- Archiving
- Creating drafts

Sending and deletion should not be enabled until separately approved.

## 10.2 Token Storage

OAuth refresh tokens should:

- Never be stored in source code
- Never be exposed to the browser
- Never be included in logs
- Be encrypted before database storage
- Be accessible only to approved connector services

## 10.3 Token Lifecycle

The platform should support:

- Token refresh
- Token expiry detection
- Revocation
- Reauthorization
- Scope changes
- Connection health monitoring

## 10.4 Connector Display

The dashboard should display:

- Connected account
- Connection status
- Granted scopes
- Last successful use
- Reconnect action
- Revoke action

It should never display secret token values.

---

## 11. Secret Management

Secrets include:

- OAuth client secrets
- OAuth refresh tokens
- LLM API keys
- Database credentials
- Queue credentials
- Session secrets
- Encryption keys
- Webhook secrets

### Local development

Use `.env` files excluded from Git.

### Render

Use protected environment variables.

### Netlify

Expose only frontend-safe values.

### Future state

Use a dedicated secrets manager or cloud key-management service.

### Required controls

- No secret logging
- Secret rotation
- Revocation
- Restricted service access
- Environment separation
- Secret scanning in Git

---

## 12. Encryption

## 12.1 In Transit

Use TLS for:

- Browser to dashboard
- Dashboard to API
- API to database
- Services to queue
- Workers to Gmail
- Workers to Google Drive
- Workers to LLM providers
- Provisioner to Notion

## 12.2 At Rest

Require encryption for:

- PostgreSQL
- OAuth token fields
- Render disks where used
- Google Drive content
- Local development devices

## 12.3 Application-Level Encryption

Sensitive credential values stored in PostgreSQL should be encrypted at the application layer.

The encryption key must be stored separately from encrypted values.

---

## 13. LLM Security

## 13.1 Trust Model

LLM output is untrusted input.

The model may:

- Produce incorrect output
- Ignore instructions
- Follow malicious email content
- Generate unsafe actions
- Produce malformed JSON
- Hallucinate recipients or file paths

## 13.2 Prompt Injection Controls

Controls should include:

- Separate system instructions from external content
- Clearly mark email content as untrusted data
- Do not allow email text to redefine agent policy
- Restrict available tools
- Validate all proposed actions
- Require human approval for sensitive actions
- Minimize external content passed to the model
- Record prompt version and model metadata

## 13.3 Structured Output

Use schema-constrained responses.

Example:

```json
{
  "category": "subscription",
  "confidence": 0.96,
  "recommended_action": "archive",
  "requires_approval": false
}
```

Reject output that does not match the schema.

## 13.4 Model Access Controls

The LLM must not directly receive:

- OAuth tokens
- Database credentials
- Raw secret values
- Unnecessary personal information
- Full mailbox history unless explicitly required

## 13.5 Cost and Abuse Controls

- Maximum model calls per run
- Token budget
- Timeout
- Retry limit
- Model allowlist
- Cost threshold
- Circuit breaker

---

## 14. Tool Security

Every tool must declare:

- Tool ID
- Input schema
- Output schema
- Required permission
- Connector dependency
- Risk level
- Idempotency behavior
- Timeout
- Audit requirements

Example:

```json
{
  "tool_id": "gmail.archive_message",
  "required_permission": "gmail.modify",
  "risk_level": "low",
  "requires_approval": false,
  "idempotent": true
}
```

Agents may use only explicitly assigned tools.

---

## 15. Human Approval Security

Approval is required for actions such as:

- Sending email
- Deleting email
- Forwarding email
- Unsubscribing
- Sharing a file externally
- Modifying sensitive calendar events
- Publishing content
- Executing an unfamiliar action

Approval records should include:

- Proposed action
- Exact destination
- Relevant content preview
- Risk level
- Reason
- Agent
- Run
- Request timestamp
- Expiry timestamp
- Reviewer
- Decision timestamp
- Execution result

Approval must not be reusable for a different action.

### 15.1 Draft-Support Knowledge Security

Governed knowledge used by a draft remains untrusted until Atlas validates it
against schema, policy, sensitivity, provenance, confirmation, and freshness
requirements. Knowledge questions and answers are not approvals and cannot
authorize an action or use approval Request clarification state.

Controls:

- Facts are versioned and approval evidence references the exact revisions used
- The decision-context manifest binds the approved draft to those revisions
- Changed, deleted, or stale facts fail closed when they invalidate a draft
- An invalidated draft is regenerated and receives a new approval request
- Answers may create or update facts only after validation
- History-derived candidates require an approved send with a confirmed `Sent`
  outcome and preserved source provenance
- `Failed` and `Indeterminate` outcomes are never learning sources
- Secrets, credentials, protected health information, and content derived from
  a clinically suppressed message are rejected before persistence
- Rejected prohibited values are absent from logs, webhooks, audit payloads,
  approval evidence, and retained knowledge content

---

## 16. Input Validation

Validate all:

- API requests
- Query parameters
- Agent configuration
- Schedule expressions
- File names
- File paths
- URLs
- Email addresses
- Attachment size
- MIME type
- LLM output
- Connector responses
- Queue messages
- Knowledge facts and fact revisions
- Knowledge questions and answers

Do not rely only on frontend validation.

---

## 17. File and Attachment Security

Attachments may be malicious or sensitive.

Controls:

- File size limits
- MIME-type validation
- Extension validation
- Safe file naming
- No automatic execution
- Approved destination folders
- Malware scanning when feasible
- Restricted inline preview
- Quarantine option
- Retention classification
- Audit trail

Files should not be written directly to arbitrary local paths from a cloud worker.

---

## 18. API Security

The Backend API should implement:

- Authentication by default
- Authorization by resource and action
- Request validation
- Rate limiting
- CORS restrictions
- Secure headers
- Payload size limits
- Timeout controls
- Idempotency keys
- Error normalization
- No stack traces in production responses
- Correlation IDs
- Audit logging

---

## 19. Database Security

Controls should include:

- Private network access
- TLS
- Strong credentials
- Separate service accounts where practical
- Parameterized queries
- Migration control
- Automated backups
- Restore testing
- Encryption for sensitive fields
- Data retention policies
- Least-privilege database roles

The database should not retain unnecessary full email content.

---

## 20. Queue Security

Queue controls:

- Authenticated access
- Private connectivity
- Minimal message payloads
- No credentials
- No full email bodies
- Schema validation
- Message expiry
- Retry limits
- Dead-letter handling
- Duplicate detection

---

## 21. Logging Security

Logs must not contain:

- Access tokens
- Refresh tokens
- Passwords
- API keys
- Full email bodies by default
- Sensitive attachment contents
- Database connection strings
- Session cookies

Logs should include:

- Correlation ID
- Run ID
- Agent ID
- Component
- Event type
- Severity
- Timestamp
- Error category
- Redacted resource reference

---

## 22. Audit Security

Audit records should be append-only where practical.

Material audit events include:

- Login
- Logout
- Connector creation
- Connector revocation
- Permission change
- Agent activation
- Agent disablement
- Schedule change
- Run initiation
- Approval decision
- External action
- Credential rotation
- Policy change
- Knowledge fact creation, revision, confirmation, and deletion
- Knowledge question creation and answer validation outcome

Audit records should preserve:

- Actor
- Action
- Resource
- Time
- Result
- Correlation ID
- Policy decision
- Approval reference

---

## 23. Data Classification

Initial classifications:

| Classification | Examples                                                   |
| -------------- | ---------------------------------------------------------- |
| Public         | Published project documentation                            |
| Internal       | Agent configuration and technical metadata                 |
| Confidential   | Email metadata, logs, outputs                              |
| Restricted     | OAuth tokens, private email content, sensitive attachments |

Governed business facts, questions, answers, and provenance are Confidential
by default. A classification label never permits prohibited knowledge content:
secrets, credentials, protected health information, and clinically suppressed
source content must be rejected rather than stored as Restricted knowledge.

Security controls should increase with classification.

---

## 24. Data Minimization

The platform should:

- Retrieve only eligible messages
- Process only required fields
- Avoid storing full message bodies
- Avoid retaining prompts indefinitely
- Store references instead of content where possible
- Redact personal data from logs
- Apply retention rules to outputs

---

## 25. Retention and Deletion

Retention should be configurable for:

- Operational logs
- Audit events
- LLM traces
- Email metadata
- Classification outputs
- Saved attachments
- Failed jobs
- Approval records
- Knowledge facts and immutable revisions
- Knowledge questions and answers

Deletion must:

- Respect audit requirements
- Avoid deleting source Gmail content unless explicitly approved
- Be recorded
- Require stronger authorization for sensitive data

---

## 26. Environment Security

Development and production must use separate:

- Databases
- OAuth clients
- API keys
- environment variables
- deployment services
- test accounts where practical

Production data should not be copied into development without sanitization.

---

## 27. Source-Code Security

Controls:

- `.env` excluded from Git
- Secret scanning
- Dependency scanning
- Pull-request review
- Branch protection later
- Locked dependency versions
- Automated security updates
- Minimal package use
- No credentials in examples

---

## 28. Infrastructure Security

Render and Netlify configurations should use:

- Restricted administrative access
- MFA
- Environment separation
- Protected environment variables
- Private database connectivity
- Limited service permissions
- Deployment logs
- Backup configuration
- Explicit production deployment controls

---

## 29. Security Monitoring

Monitor for:

- Repeated failed logins
- Connector authorization failures
- Excessive model usage
- Unexpected tool calls
- High failure rates
- Duplicate runs
- Repeated approval requests
- Token refresh failures
- Unusual outbound actions
- Large attachment downloads
- Policy denials
- Rejected knowledge inputs by reason category without the prohibited value
- Stale volatile facts and overdue re-confirmation
- Repeated invalid or unauthorized knowledge mutations

---

## 30. Incident Response

The initial incident process should include:

1. Detect the issue
2. Disable affected agent
3. Pause schedules
4. Revoke affected connector
5. Rotate credentials
6. Preserve logs
7. Assess affected data
8. Restore service safely
9. Document the incident
10. Create corrective actions

The dashboard should support emergency agent disablement.

---

## 31. Threat Model Summary

| Threat                        | Primary Controls                         |
| ----------------------------- | ---------------------------------------- |
| Stolen OAuth token            | Encryption, revocation, least privilege  |
| Prompt injection              | Tool restrictions, validation, approvals |
| Unsafe email send             | Human approval, policy enforcement       |
| Secret leak in Git            | `.gitignore`, scanning, rotation         |
| Malicious attachment          | Validation, quarantine, no execution     |
| Unauthorized dashboard access | Identity provider, secure sessions       |
| Duplicate agent action        | Idempotency, state validation            |
| Excessive model cost          | Budgets, quotas, monitoring              |
| Compromised dependency        | Scanning, version control, minimization  |
| Log exposure                  | Redaction, access control, retention     |
| Prohibited knowledge retained | Pre-persistence validation, rejection, audit minimization |
| Stale fact used in a draft    | Revision binding, freshness checks, fail-closed revalidation |
| Answer treated as authority   | Separate lifecycle, validation, non-authorizing contract |

---

## 32. Security Testing

### Unit tests

- Authorization decisions
- Policy decisions
- Input schemas
- State transitions
- Redaction
- Encryption helpers

### Integration tests

- OAuth callback
- Token refresh
- Connector revocation
- Session expiry
- Approval workflow
- Secret retrieval

### Security tests

- Authentication bypass attempts
- Authorization failures
- Prompt injection scenarios
- Invalid tool requests
- Malformed LLM responses
- Oversized attachments
- Duplicate execution attempts
- Secret leakage scans
- Prohibited knowledge-content rejection
- Clinical-suppression ordering
- Knowledge authorization and human-attribution failures
- Stale or changed fact revalidation
- Webhook replay, duplication, and reconciliation behavior

---

## 33. Production Security Checklist

Before production:

- MFA enabled on hosting and source-control accounts
- Production secrets configured
- Development secrets removed
- OAuth scopes reviewed
- Connector revocation tested
- HTTPS enforced
- Database private
- Queue private
- Token encryption implemented
- Logs redacted
- Approval controls tested
- Rate limits enabled
- Backups enabled
- Restore process documented
- Security tests passed
- Incident procedure documented
- Emergency disable control available

---

## 34. Open Security Decisions

The following decisions require ADRs:

- Authentication provider
- Session storage design
- OAuth token encryption method
- Key rotation strategy
- Log retention period
- Audit immutability approach
- Malware-scanning service
- Prompt-injection detection strategy
- Model-data retention policy
- Production secrets manager
- Security monitoring provider
- Reauthentication requirements

---

## 35. Current Status

- Core security principles defined
- Protected assets identified
- Trust boundaries documented
- OAuth and secret controls outlined
- LLM and tool security model defined
- Human approval requirements defined
- Draft-support knowledge trust boundary and high-level controls defined
- Detailed threat modelling and control implementation remain to be completed
- Knowledge authentication, validation, retention, detection, and recovery
  details remain mandatory Phase 3 and Phase 5 Engineering Specification work
