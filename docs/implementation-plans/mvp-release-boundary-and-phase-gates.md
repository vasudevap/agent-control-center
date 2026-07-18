# MVP Release Boundary and Phase Gates

**Status:** Proposed - Governance Review Required
**Owner:** Repository Maintainer
**Created:** 2026-07-18
**Purpose:** Define the crisp MVP boundary, phase gates, success criteria, exit
criteria, deployment path, associated Work Orders, and current completion
percentages.

---

## 1. MVP Boundary

The project is not at MVP today. It is at a completed Phase 3 platform
foundation.

The crisp MVP boundary is:

| Boundary | Definition |
| --- | --- |
| Pre-MVP foundation | Phases 1-5 establish architecture, repository governance, platform foundation, dashboard surface, and generic agent/governance contracts. |
| MVP candidate | Phase 6 demonstrates the first end-to-end Gmail Agent workflow with controlled data, fake-or-limited production effects, and all required safety controls. |
| MVP release | Phase 7 makes the Gmail Agent usable for normal single-owner personal operation on the approved Netlify/Render deployment path. |
| Beyond MVP | Phases 8-11 expand capability, durability, orchestration, additional agents, and enterprise readiness after the MVP is operable. |

MVP means one real operator can use Atlas to run the first Gmail Agent workflow
end to end, with authentication, scheduling, approvals, auditability, logs,
safe low-risk action execution, high-risk approval gates, and deployment to the
approved hosting path.

## 2. Phase Gate Table

Completion percentages represent progress against each phase's exit criteria,
not lines of code or effort spent.

| Phase | Stage | MVP boundary | Current % | Associated Work Orders | Work orders that capture stage work | Deployment posture | Entry gate | Success criteria | Exit criteria |
| ---: | --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| 1 | Architecture Foundation | Pre-MVP | 100% | Architecture docs, ADR baseline, PRD; no numbered WOs required | Architecture documentation, ADR-001 through ADR-005, PRD, and roadmap; no implementation WO required | Documentation only | Project purpose and architecture scope agreed | System context, container, component, security, data, runtime, connector, observability, and technology architecture exist | Architecture baseline accepted and usable for governed execution |
| 2 | Repository Foundation | Pre-MVP | 100% | ES-000 through ES-003; frontend WOs 001-014 partially cover repository/dashboard groundwork | ES-000, ES-001, ES-002, ES-003, WO-001 through WO-014 | Local repo and CI | Canonical repo, governance, and frontend foundation path defined | Repository standards, CI, review process, frontend test infrastructure, and initial dashboard design assets exist | Governed branch/PR/CI workflow is usable and source of truth is in Git |
| 3 | Platform Foundation | Pre-MVP | 100% | WO-015 through WO-026 | WO-015, WO-016, WO-017, WO-018, WO-019, WO-020, WO-021, WO-022, WO-023, WO-024, WO-025, WO-026 | Local and CI backend foundation; no live production operation | Phase 3 engineering spec and accepted WOs | FastAPI foundation, PostgreSQL migrations, auth/session scaffolding, authorization boundary, API contracts, queue, scheduler, webhook fake delivery, logging, audit, and closeout smoke test pass | WO-026 merged, CI green, Phase 3 closeout report complete |
| 4 | Dashboard Productization | Pre-MVP, MVP-enabling | 60% | Existing: WO-001, WO-005, WO-006, WO-009 through WO-014 completed; remaining dashboard/backend-integration WOs TBD | Completed UI/prototype coverage: WO-001, WO-005, WO-006, WO-009, WO-010, WO-011, WO-012, WO-013, WO-014. Remaining productization WOs TBD for real API integration and fixture removal | Netlify preview before production | Phase 3 backend foundation complete | Dashboard routes are integrated with real API contracts, auth/session state, errors, loading states, empty states, and operator flows | Operator can manage agents, runs, approvals, audit/log views, connector settings, and health from the dashboard without fixture-only behavior |
| 5 | Agent Framework and Governance Contracts | Pre-MVP, MVP-enabling | 0% | TBD, likely WO-027+ | Future WOs starting at WO-027 should capture Phase 5 engineering spec, work-order backlog, generic agent/runtime contracts, approval/manual-handling APIs, governed knowledge APIs, webhooks, audit, and `facts_used` evidence | Render development/staging API with synthetic data only | Phase 3 complete and Phase 5 WOs accepted | Generic agent registry/runtime contracts, external approval decision API, manual-handling contract, governed knowledge CRUD, confirmations, volatility, questions/answers, webhooks, `facts_used`, audit, and revalidation contracts exist | Generic contracts are implemented, tested, documented, and merged without Gmail-specific behavior |
| 6 | Gmail Agent MVP Candidate | MVP candidate | 0% | TBD, after Phase 5 | Future Phase 6 WOs should capture Gmail OAuth, message eligibility, classification, ask-instead-of-guess consumption, draft/evidence generation, approvals, low-risk actions, high-risk approval gates, and Gmail audit evidence | Controlled Gmail test account or limited private beta | Phase 5 contracts complete; Gmail/OAuth scope accepted | Gmail OAuth, eligible-message selection, classification, ask-instead-of-guess, draft/evidence generation, approvals, safe low-risk actions, high-risk approval gates, logs, and audit work end to end | First Gmail Agent workflow can run safely with controlled data and no unresolved safety blocker |
| 7 | Operational MVP Release | MVP release | 0% | TBD | Future release WOs should capture production deployment, environment configuration, health/readiness verification, monitoring, rollback, runbook, recovery, and MVP acceptance evidence | Netlify + Render MVP production deployment | Phase 6 candidate passes safety and usability review | Normal single-owner use is reliable enough: deployment, health/readiness, scheduling, retries, recovery path, monitoring, documented operations, and rollback are in place | MVP is operable for personal use, with CI green, deployment verified, no credential exposure, and accepted residual risk |
| 8 | Advanced Agentic Workflows | Beyond MVP | 0% | TBD | Future post-MVP WOs should capture each advanced workflow, framework evaluation, safety gate, and reusable platform extension independently | Incremental post-MVP environments | MVP released and stable | Additional workflow patterns, richer planning/tooling, and optional framework experiments are evaluated against architecture criteria | Advanced workflows add value without weakening MVP safety, audit, or maintainability |
| 9 | Durable Orchestration | Beyond MVP | 0% | TBD | Future orchestration WOs should capture ADR-backed Temporal or equivalent evaluation, migration path, durable workflow tests, and rollback plan | Post-MVP staging before production | Durable workflow needs exceed simple queue/scheduler | Temporal or equivalent orchestration is justified, ADR-approved, implemented, and tested | Long-running/recoverable workflows are durable without unnecessary complexity |
| 10 | Additional Agents | Beyond MVP | 0% | TBD | Future agent WOs should capture each agent separately, including connector scope, permissions, policies, tests, audit, rollout, and closeout | Agent-by-agent rollout | Gmail MVP proves reusable platform contracts | Calendar, documents, shopping, travel, job search, or other agents reuse platform contracts | Each new agent ships behind accepted WOs, safety controls, and operational evidence |
| 11 | Enterprise Features | Beyond MVP | 0% | TBD | Future enterprise WOs should capture SSO, RBAC, multi-user governance, tenant boundaries, private networking, stronger secrets, audit retention, and support readiness separately | Enterprise-ready environments only after separate authority | Multi-user/enterprise requirements are accepted | RBAC, SSO, multi-user governance, stronger secrets, private networking, tenant boundaries, and enterprise audit requirements are designed | Enterprise capabilities meet accepted security, governance, deployment, and support criteria |

## 3. MVP Success Criteria

MVP succeeds when:

- at least one production Gmail Agent is operable for the single owner;
- the dashboard shows agents, status, runs, logs, outputs, approvals, health,
  and connector state using real backend contracts;
- manual Run Now and scheduled execution both work;
- low-risk Gmail actions execute safely and idempotently;
- high-risk actions require approval before execution;
- ask-instead-of-guess creates governed questions instead of unsafe drafts;
- knowledge facts used by drafts are traceable through `facts_used`;
- clinical/protected-health-information suppression prevents drafts, approvals,
  questions, and learned facts for suppressed content;
- audit records distinguish human, external client, and service actors;
- credentials and secrets are never exposed in logs, APIs, webhooks, or UI;
- Netlify and Render deployment is verified with documented rollback;
- architecture, ADRs, WOs, implementation reports, and status records remain
  synchronized.

## 4. MVP Exit Criteria

The project exits MVP and enters post-MVP expansion only after:

- Phase 7 is complete;
- the Gmail Agent has been used successfully in normal single-owner operation;
- known MVP defects are triaged with no unresolved safety, security, or data
  loss blockers;
- monitoring and manual recovery are sufficient for initial personal use;
- residual risks are accepted and documented;
- Phase 8+ scope is approved through new Engineering Specifications, ADRs, or
  Work Orders as required.

## 5. Immediate Next Governance Step

Create the Phase 5 execution package before implementation:

| Next artifact | Purpose |
| --- | --- |
| Phase 5 Engineering Specification | Define generic agent/governance contracts, API surfaces, validation rules, audit, security, errors, idempotency, retention, and test requirements. |
| Phase 5 Work Order Backlog | Break Phase 5 into accepted WOs, starting at the next available work-order number. |
| Phase 5 ADP, if desired | Authorize uninterrupted execution only after the Phase 5 WOs are drafted, reviewed, accepted, and dependency-ordered. |

Phase 5 must not silently become Gmail-specific implementation. Gmail-specific
execution belongs to Phase 6 after the generic contracts are ready.
