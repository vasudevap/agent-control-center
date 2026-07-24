# Work Order 066: Owner Enrollment and Agent Credentials

**Status:** Accepted - Authorized, blocked on WO-065 completion
**Work Order ID:** WO-066
**Type:** Agent enrollment and trust lifecycle foundation
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-24
**Engineering Specification:** [ES-009](../engineering-specifications/ES-009-agent-visibility-and-lifecycle-mvp.md)
**Governing ADP:** [ADP-006](../implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md)
**Prerequisites:** WO-065 accepted and complete
**Review Record:** To be created during implementation

## 1. Purpose

Implement owner-authenticated enrollment and one-time agent credential
issuance using the ES-009 credential format and verifier model.

## 2. Approved Scope if Accepted

- Implement owner create, list, read, and metadata update for active agents.
- Generate `atl_agent_<credential_lookup_id>.<secret>` credentials at
  enrollment.
- Store only HMAC-SHA256 verifiers using
  `ATLAS_API_AGENT_CREDENTIAL_PEPPER` and key id metadata.
- Return plaintext credentials only at issuance.
- Add owner session, CSRF, idempotency, and audit coverage for state-changing
  lifecycle operations.
- Add readiness checks for required credential pepper settings in
  production-like environments.
- Add service-layer tests for lifecycle defaults, verifier persistence,
  redaction, and owner-only access.

## 3. Expected File Scope

- `apps/api/src/atlas_api/api/agent_registry.py` or replacement ES-009 router
- `apps/api/src/atlas_api/services/agent_registry.py`
- new credential service modules under `apps/api/src/atlas_api/services/`
- `apps/api/src/atlas_api/core/config.py`
- `apps/api/src/atlas_api/core/auth.py`
- `apps/api/src/atlas_api/main.py`
- `apps/api/tests/**`

## 4. Explicitly Out of Scope

Heartbeat ingestion, execution ingestion, rotation, disconnect, reconnect,
archive, frontend enrollment UI, hosted provider secret entry, and reusing
the existing external-product-client HMAC secret are out of scope.

## 5. Acceptance Criteria

- Owner can create a pending agent and receives exactly one plaintext
  credential in the response.
- Read endpoints never return plaintext credentials or credential verifiers.
- New agents are `owner_enrolled`, active-surface visible, and scoped to the
  single owner.
- Production-like readiness fails closed when agent credential pepper settings
  are missing.
- Tests prove no plaintext credential persistence, no plaintext logging, and
  owner-only mutation behavior.

## 6. Verification

```bash
python -m mypy apps/api/src
python -m ruff check apps/api
python -m pytest apps/api
git diff --check
```

## 7. Rollback Expectations

Source rollback cannot recover issued plaintext credentials. If credential
issuance is found unsafe, disable enrollment routes and preserve credential
rows for audit and investigation.

## 8. Stop-and-Ask Triggers

Stop before exposing plaintext credentials after issuance, reusing external
client secrets, changing owner identity provider behavior, recording secret
values in docs/logs/tests, or changing production provider secrets.
