# Work Order 036: Gmail OAuth, Scopes, and Connector Boundary

**Status:** Completed - Merged
**Work Order ID:** WO-036
**Type:** Backend connector and credential boundary
**Implementation Authorization:** Granted under ADP-003 on 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing Plan:** [Phase 6 Work Order Backlog](../implementation-plans/phase-6-work-order-backlog.md)
**Architecture Authority:** [Connector Framework](../architecture/10-connector-framework.md), [Security Architecture](../architecture/07-security-architecture.md)
**Prerequisites:** ES-006 accepted; Phase 5 closeout complete
**Review Record:** [WO-036 Implementation Report](../reviews/WO-036-gmail-oauth-scopes-and-connector-boundary-implementation-report.md)

## 1. Purpose

Implement the Gmail and Drive connector foundation required for the Gmail Agent
MVP Candidate, including exact OAuth scope enforcement, credential references,
fake-provider contracts, connector health, revocation, and audit behavior.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Gmail candidate scope | `https://www.googleapis.com/auth/gmail.modify` |
| Drive candidate scope | `https://www.googleapis.com/auth/drive.file` |
| Rejected Gmail scope | `https://mail.google.com/` because it includes immediate permanent delete authority |
| Token handling | Store only encrypted credential references through the connector boundary; never expose token values |
| Provider tests | Use fake Gmail and Drive providers for automated tests |
| Live credentials | Not authorized by this Work Order |

## 3. Approved Scope if Accepted

- Gmail and Drive connector type registration.
- OAuth connection initiation, callback validation, scope verification, health,
  reconnect, and revoke contracts.
- Credential reference persistence through the approved credential boundary.
- Fake Gmail and Drive provider clients that support later Work Orders without
  network calls.
- Connector operation allowlists mapped to accepted scopes.
- Audit events for connect, reconnect, revoke, health check, denied scope,
  credential access, and connector operation attempts.

## 4. Explicitly Out of Scope

Real Gmail credentials, live provider calls, personal mailbox access, production
OAuth consent configuration, message retrieval, classification, drafting,
sending, labels, archive, attachment saving, knowledge behavior, dashboard
productization, and broad credential-vault infrastructure are excluded.

## 5. Verification and Completion

Require unit and fake-provider integration tests for OAuth state validation,
accepted-scope matching, rejected broad scopes, token redaction, credential
reference persistence, health, reconnect, revoke, denied operation behavior,
audit metadata minimization, `ruff`, `mypy`, migration checks if schema changes,
secret scan, and CI.

## 6. Rollback Expectations

Connector registration and credential-reference migrations must be reversible
where practical. If credential reference rows are created during local testing,
rollback must revoke fake credentials and leave no token material in persisted
fixtures or logs.

## 7. Stop-and-Ask Triggers

Stop before requesting a broader Google scope, storing token values outside the
credential boundary, using live credentials, calling Google APIs, adding
permanent delete authority, changing single-owner assumptions, or weakening
audit/redaction controls.
