# Phase 3 Implementation Decision Register

**Status:** Proposed - Consolidated Planning Review Required
**Owner:** Repository Maintainer
**Date:** 2026-07-17
**Implementation Authorization:** Not Granted

## 1. Purpose

Provide one review surface for the implementation decisions fixed by proposed
WO-019 through WO-026. The detailed Work Orders remain authoritative for scope,
verification, exclusions, and stop conditions.

## 2. Decision Register

| Work Order | Fixed implementation direction | Explicitly deferred |
| --- | --- | --- |
| WO-019 | Single immutable owner subject; provider-neutral verifier; opaque hashed PostgreSQL sessions; strict secure cookie; server-side revocation. | Google OAuth/OIDC integration, frontend login, multi-user/RBAC. |
| WO-020 | Typed deny-by-default authorization; separated actor/channel identity; HMAC-SHA256 external requests; timestamp + persisted nonce replay defense; environment-owned rotating keys. | Multi-client tenancy, PKI, business permissions. |
| WO-021 | `/api/v1`; `{data, meta}` success envelope; stable error envelope; opaque cursor; allowlisted filters; idempotency validation interface; OpenAPI conventions. | Business CRUD, limiter implementation, SDK generation. |
| WO-022 | Deterministic HMAC-signed minimal notifications; exact-body signature; six-state delivery lifecycle; five-attempt bounded retry; fake transport only. | Live delivery/receiver, authoritative webhook state, workflow event production. |
| WO-023 | PostgreSQL queue; `SKIP LOCKED`; opaque lease tokens; bounded retry/dead-letter; typed resource-reference payloads; deterministic idempotency. | Redis/broker, workers, business job types. |
| WO-024 | UTC fixed-interval schedules; transactional occurrence + enqueue; deterministic occurrence key; one overdue trigger per sweep; one-shot command. | Cron/time zones, Render Cron provisioning, agent execution. |
| WO-025 | Standard-library JSON logs; allowlist-first redaction; durable PostgreSQL audit writer; fail-closed material audit; correlation and health conventions. | OpenTelemetry/vendor deployment, dashboards, alert routing. |
| WO-026 | PostgreSQL 18 CI integration smoke across all foundations; synthetic data/fakes; blocker-level security assertions; documentation and Phase 5 handoff. | New capabilities, live providers, production certification, Phase 5 behavior. |

## 3. Sequencing and Parallelism

```text
WO-019 -> WO-020 -> WO-021 -> WO-022 ---+
                         \               +-> WO-025 ---+
WO-018 -----------------> WO-023 --------+             +-> WO-026
                              \-> WO-024 --------------+
```

- WO-019, WO-020, and WO-021 are sequential.
- After WO-021, WO-022 and WO-023 may proceed independently.
- WO-024 waits for WO-023.
- WO-025 waits for WO-021, WO-022, and WO-023, and may run alongside WO-024.
- WO-026 waits for every preceding Phase 3 Work Order.

## 4. Shared Implementation Controls

Every Work Order uses one branch, one implementation PR, PostgreSQL 18 CI where
persistence is involved, deterministic tests/fakes, strict secret scanning,
documentation evidence, and required CI. No implementation agent may choose a
different provider, persistence technology, identity boundary, queue backend,
or deployment topology without stopping for governance review and any required
ADR.

Planning acceptance may occur as one consolidated review. Implementation must
still proceed in dependency order and remain independently reviewable.

## 5. ADR Assessment

No new ADR is required for this package because it applies the accepted
single-owner/single-external-client trust boundary, FastAPI/PostgreSQL/Alembic
stack, PostgreSQL queue direction, provider-neutral authentication foundation,
and Netlify/Render topology.

Stop and propose an ADR before replacing those technologies or boundaries,
adding provider-specific OAuth beyond the approved identity-verifier boundary,
adopting Redis or another broker, introducing a telemetry vendor as an
architectural dependency, or expanding to multi-user/multi-client tenancy.
