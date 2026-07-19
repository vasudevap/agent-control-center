# Work Order 053: Production Environment and Secrets Provisioning

**Status:** Accepted - In Progress
**Work Order ID:** WO-053
**Type:** Production configuration and secret provisioning
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-19
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** ES-008 and ADP-005 accepted
**Review Record:** [WO-053 Implementation Report](../reviews/WO-053-production-environment-and-secrets-provisioning-implementation-report.md)

## 1. Purpose

Configure and verify provider-native environment variables and secrets required
for hosted MVP cutover without exposing secret values.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Secret storage | Use provider-native Netlify, Render, and Google stores |
| Source control | Secret values never enter Git, logs, screenshots, PRs, or chat |
| Runtime readiness | Missing production-critical config fails closed |
| Account boundary | Single-owner Grafley/Atlas MVP deployment only |

## 3. Approved Scope if Accepted

- Inventory and configure required Netlify frontend, Render API, Render
  PostgreSQL, Google OAuth, webhook, owner identity, and external-client
  settings.
- Record only variable names, provider locations, redacted status, and
  validation evidence.
- Verify redacted settings and readiness behavior.
- Document rotation, revocation, and emergency response owners.

## 4. Explicitly Out of Scope

Committing secret values, changing providers, adding a new secrets manager,
creating broad Google scopes, production deployment, public launch, and
multi-user configuration are excluded.

## 5. Verification and Completion

Require provider configuration evidence with values omitted, local redaction
checks, readiness behavior evidence, secret-pattern scans over touched files,
and an implementation report under `docs/reviews/`.

## 6. Rollback Expectations

Rollback must remove or rotate incorrectly configured provider secrets and
preserve audit evidence without exposing values.

## 7. Stop-and-Ask Triggers

Stop before exposing secret values, changing provider topology, provisioning
unapproved accounts, broadening scopes, weakening fail-closed readiness, or
logging credential material.
