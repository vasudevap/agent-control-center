# Work Order 047: Environment Configuration and Secrets Readiness

**Status:** Implemented - Pending PR Review
**Work Order ID:** WO-047
**Type:** Configuration and security readiness
**Implementation Authorization:** Granted under ADP-004 on 2026-07-18
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)
**Governing Plan:** [Phase 7 Work Order Backlog](../implementation-plans/phase-7-work-order-backlog.md)
**Prerequisites:** ES-007 accepted, WO-036 and WO-044 completed
**Review Record:** [WO-047 Implementation Report](../reviews/WO-047-environment-configuration-and-secrets-readiness-implementation-report.md)

## 1. Purpose

Define and verify required environment variables, OAuth client setup,
provider-native secret storage, redaction, revocation, rotation, and
fail-closed configuration behavior before release.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Secret storage | Provider-native stores unless an ADR changes this |
| Token visibility | Token values never appear in logs, APIs, webhooks, fixtures, or audit payloads |
| Startup behavior | Missing required configuration fails closed |
| OAuth scopes | Keep accepted `gmail.modify` and `drive.file` posture |

## 3. Approved Scope if Accepted

- Inventory required API, web, database, OAuth, webhook, scheduler, and owner
  configuration values.
- Document local, CI, development/staging, and production environment
  expectations.
- Verify missing or unsafe production-critical configuration fails closed.
- Verify logs and structured errors redact secrets and token values.
- Document OAuth client setup, redirect URI expectations, rotation, revocation,
  and emergency credential response.
- Add automated checks where practical for secret leakage and unsafe defaults.

## 4. Explicitly Out of Scope

Creating real production secrets, committing secret values, adding a new
secrets manager, changing OAuth scope posture, provisioning live provider
resources, and production deployment are excluded unless separately accepted.

## 5. Verification and Completion

Require settings tests, redaction tests, token/secret scans over touched files,
startup failure evidence for missing required configuration, documentation
review, and an implementation report under `docs/reviews/`.

## 6. Rollback Expectations

Rollback must not leave secret values, OAuth tokens, or unsafe configuration in
source, fixtures, logs, or documentation. If a test credential is created under
separate authority, rollback must revoke or rotate it.

## 7. Stop-and-Ask Triggers

Stop before handling real secret values, using live credentials, introducing a
new secret store, broadening Google scopes, disabling fail-closed startup,
logging token material, or changing the environment model without ADR review.
