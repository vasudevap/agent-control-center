# MVP Release Boundary and Phase Gates

**Status:** Proposed - Phase 7 Planning Update Pending Review
**Owner:** Repository Maintainer
**Created:** 2026-07-18
**Purpose:** Define the crisp MVP boundary, phase gates, success criteria, exit
criteria, deployment path, associated Work Orders, required governing
artifacts, autonomous execution structure, and current completion percentages.

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

| Phase | Stage | MVP boundary | Current % | Associated Work Orders | Governing Artifacts | Deployment posture | Entry gate | Success criteria | Exit criteria |
| ---: | --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| 1 | Architecture Foundation | Pre-MVP | 100% | Architecture docs, ADR baseline, PRD; no numbered WOs required | PRD; architecture baseline; ADR-001 through ADR-005; roadmap; technology strategy; design principles | Documentation only | Project purpose and architecture scope agreed | System context, container, component, security, data, runtime, connector, observability, and technology architecture exist | Architecture baseline accepted and usable for governed execution |
| 2 | Repository Foundation | Pre-MVP | 100% | ES-000 through ES-003; frontend WOs 001-014 partially cover repository/dashboard groundwork | ES-000 through ES-003; governance controls; definition of ready/done; pull-request and review standards; WO-001 through WO-014; relevant design decision records | Local repo and CI | Canonical repo, governance, and frontend foundation path defined | Repository standards, CI, review process, frontend test infrastructure, and initial dashboard design assets exist | Governed branch/PR/CI workflow is usable and source of truth is in Git |
| 3 | Platform Foundation | Pre-MVP | 100% | WO-015 through WO-026 | ES-004; Phase 3 master plan, target architecture, backlog, and decision register; ADP-001; WO-015 through WO-026; WO-026 closeout report | Local and CI backend foundation; no live production operation | Phase 3 engineering spec and accepted WOs | FastAPI foundation, PostgreSQL migrations, auth/session scaffolding, authorization boundary, API contracts, queue, scheduler, webhook fake delivery, logging, audit, and closeout smoke test pass | WO-026 merged, CI green, Phase 3 closeout report complete |
| 4 | Dashboard Productization | Pre-MVP, MVP-enabling | 60% | Existing: WO-001, WO-005, WO-006, WO-009 through WO-014 completed; remaining dashboard/backend-integration WOs TBD | Existing dashboard WOs and implementation reports; likely dashboard productization ES; API-integration and fixture-removal WOs; UI acceptance/review reports; design decision records if the approved experience changes | Netlify preview before production | Phase 3 backend foundation complete | Dashboard routes are integrated with real API contracts, auth/session state, errors, loading states, empty states, and operator flows | Operator can manage agents, runs, approvals, audit/log views, connector settings, and health from the dashboard without fixture-only behavior |
| 5 | Agent Framework and Governance Contracts | Pre-MVP, MVP-enabling | 100% | Accepted WO-027 through WO-035; WO-027 through WO-035 merged | Accepted ES-005; Phase 5 ADR assessment; Phase 5 WO backlog; accepted ADP-002; accepted WO-027 through WO-035; WO-027 through WO-035 implementation reports and closeout report | Render development/staging API with synthetic data only | Phase 3 complete, ES-005 accepted, ADR assessment accepted, and Phase 5 WOs accepted | Generic agent registry/runtime contracts, external approval decision API, manual-handling contract, governed knowledge CRUD, confirmations, volatility, questions/answers, webhooks, `facts_used`, audit, and revalidation contracts exist | Generic contracts are implemented, tested, documented, and merged without Gmail-specific behavior |
| 6 | Gmail Agent MVP Candidate | MVP candidate | 100% | WO-036 through WO-044 completed and merged | Accepted ES-006; Phase 6 ADR assessment; Phase 6 Work Order backlog; ADP-003; ES-006 review record; WO-036 through WO-044 implementation and closeout reports | Fake-provider evidence complete; controlled-account plan prepared; no production authority | Phase 5 contracts complete; ES-006 accepted; Gmail/OAuth scope accepted | Gmail OAuth, eligible-message selection, classification, ask-instead-of-guess, draft/evidence generation, approvals, safe low-risk actions, high-risk approval gates, logs, and audit work end to end | Gmail Agent MVP Candidate closed with fake-provider evidence, controlled-account plan, and explicit release-decision boundary |
| 7 | Operational MVP Release | MVP release | 0% | Proposed WO-045 through WO-052 | Proposed ES-007; Phase 7 ADR assessment; Phase 7 Work Order backlog; ADP-004; proposed ES-007 review; future implementation reports, release candidate report, runbooks, and closeout | Netlify + Render MVP production deployment only after explicit release authority | Phase 6 candidate complete; ES-007 package accepted; release readiness WOs accepted | Normal single-owner use is reliable enough: controlled-account evidence or accepted deferral, dashboard productization, deployment readiness, health/readiness, scheduling, retries, recovery path, monitoring, documented operations, and rollback are in place | MVP is operable for personal use, with CI green, deployment verified, no credential exposure, and accepted residual risk |
| 8 | Advanced Agentic Workflows | Beyond MVP | 0% | TBD | Likely advanced-workflow ES and ADRs; framework evaluation; one or more WOs per workflow; safety and post-MVP risk reviews; implementation and acceptance reports | Incremental post-MVP environments | MVP released and stable | Additional workflow patterns, richer planning/tooling, and optional framework experiments are evaluated against architecture criteria | Advanced workflows add value without weakening MVP safety, audit, or maintainability |
| 9 | Durable Orchestration | Beyond MVP | 0% | TBD | Likely orchestration ADR; durable-workflow ES; Temporal-or-equivalent evaluation; migration and rollback plan; orchestration WOs; durability and recovery evidence | Post-MVP staging before production | Durable workflow needs exceed simple queue/scheduler | Temporal or equivalent orchestration is justified, ADR-approved, implemented, and tested | Long-running/recoverable workflows are durable without unnecessary complexity |
| 10 | Additional Agents | Beyond MVP | 0% | TBD | Likely per-agent PRD addenda or functional specifications; connector-scope ADRs where needed; WOs per agent; policy/safety reviews; rollout, acceptance, and closeout reports | Agent-by-agent rollout | Gmail MVP proves reusable platform contracts | Calendar, documents, shopping, travel, job search, or other agents reuse platform contracts | Each new agent ships behind accepted WOs, safety controls, and operational evidence |
| 11 | Enterprise Features | Beyond MVP | 0% | TBD | Likely enterprise PRD and ES; ADRs for SSO, RBAC, multi-user operation, tenancy, secrets, and networking; governance/security reviews; phased enterprise WOs; support-readiness evidence | Enterprise-ready environments only after separate authority | Multi-user/enterprise requirements are accepted | RBAC, SSO, multi-user governance, stronger secrets, private networking, tenant boundaries, and enterprise audit requirements are designed | Enterprise capabilities meet accepted security, governance, deployment, and support criteria |

## 3. Autonomous Execution Artifact Model

The phase gate table should remain the release-control view. It should not try
to carry every work-order dependency directly, because that makes the table
wide, brittle, and hard for multiple agents to execute from.

Use the following artifact model for autonomous delivery:

| Artifact type | Role in execution | Automation rule |
| --- | --- | --- |
| PRD or PRD addendum | Defines the product outcome, user value, and MVP or post-MVP boundary | Required before a new product capability phase begins |
| Architecture baseline | Defines the accepted system, container, component, data, security, runtime, connector, observability, and deployment boundaries | Required before ES drafting when architecture already exists; update only through accepted governance |
| ADR | Records a significant architecture, security, data, framework, runtime, deployment, or integration decision | ADRs decide; they do not collect or own WOs. A WO may depend on one or more accepted ADRs |
| ES | Converts accepted product and architecture authority into an engineering scope, exclusions, interfaces, validation, and rollback expectations | Required before implementation WOs for a major capability |
| ADP | Sequences accepted WOs into an autonomous execution program, including dependency gates, parallel lanes, validation, PR/CI rules, and stop-and-ask triggers | Required before uninterrupted multi-WO execution |
| WO | Authorizes one bounded implementation change with file scope, prerequisites, acceptance criteria, validation, rollback, and stop-and-ask triggers | The smallest unit an implementation agent should execute |
| Review or acceptance record | Records readiness, implementation evidence, validation, risks, and closure | Required to close ES, WO, ADP, MVP candidate, and release phases |
| Runbook or release plan | Defines deployment, health checks, rollback, operations, monitoring, credential handling, and incident/recovery steps | Required before MVP production release and any live integration |
| Risk, privacy, or security review | Records accepted residual risk and safety/privacy findings | Required when live credentials, external provider data, user data, or production effects enter scope |

The ADP is the correct place to group WOs for autonomous execution. Dependent
WOs belong in serialized ADP waves. Independent WOs belong in parallel ADP
lanes. ADRs remain decision gates that WOs cite as prerequisites.

## 4. Required Artifact Register by Phase

This table is a best-effort artifact register based on the current state of the
repository. Future phases may add, split, or retire artifacts when their
specific scope is drafted.

| Phase | Stage | Required governing artifacts | Decision gates | Execution package | Parallelization posture |
| ---: | --- | --- | --- | --- | --- |
| 1 | Architecture Foundation | PRD; architecture baseline; ADR-001 through ADR-005; architecture README; roadmap; technology strategy; design principles | Accepted architecture and ADR baseline | No ADP required; documentation foundation is complete | Complete; no active parallel implementation |
| 2 | Repository Foundation | ES-000 through ES-003; governance README; Definition of Ready; Definition of Done; PR/review process; branching and release management; WO-001 through WO-014; design decision records; implementation reports | ADR-001 for frontend testing; ADR-002 for approval decision integrity | Individual frontend/governance WOs | Complete; no active parallel implementation |
| 3 | Platform Foundation | ES-004; Phase 3 master plan; target architecture; decision register; phase backlog; ADP-001; WO-015 through WO-026; implementation reports; Phase 3 closeout | ADR-003, ADR-004, ADR-005 accepted before backend platform work | ADP-001 completed Phase 3 dependency sequence | Complete; Phase 3 was mostly serial with limited dependency-ready parallelism |
| 4 | Dashboard Productization | Dashboard productization ES or ES addendum; dashboard API-integration WOs; fixture-removal plan; UI acceptance records; accessibility/responsive evidence; implementation reports; closeout | ADR only if operator experience, auth, data, or decision semantics change | Future dashboard ADP or ADP lane after API contracts freeze | Can run partly in parallel with Phase 5 after API contracts and auth/session interface are stable |
| 5 | Agent Framework and Governance Contracts | Accepted ES-005; Phase 5 ADR assessment; Phase 5 WO backlog; WO-027 through WO-035; ADP-002; contract tests; implementation reports; closeout report | ADR-002 through ADR-005 were sufficient; no unresolved Phase 5 ADR trigger remains | ADP-002 completed and merged WO-027 through WO-035 | Complete; Phase 5 used dependency-ready parallel lanes and serial closeout |
| 6 | Gmail Agent MVP Candidate | Accepted ES-006; Phase 6 ADR assessment; Phase 6 WO backlog; WO-036 through WO-044; ADP-003; ES-006 review record; WO-036 through WO-044 implementation and closeout reports | Gmail OAuth scopes `gmail.modify` and `drive.file`, provider data handling, production-effect limits, and clinical/PHI suppression policy accepted for bounded implementation | ADP-003 completed and merged WO-036 through WO-044 | Complete; Phase 6 used dependency-ready lanes with serial draft/approval/send and closeout gates |
| 7 | Operational MVP Release | Proposed ES-007; Phase 7 ADR assessment; WO-045 through WO-052; ADP-004; release-management plan; environment configuration record; secrets/credential handling checklist; operational readiness review; monitoring plan; runbooks; rollback plan; MVP release candidate report; MVP acceptance and residual-risk record | Production deployment authority, environment count, controlled-account boundary, rollback owner, monitoring threshold, and residual risk accepted | Proposed ADP-004 only after ES-007 and Phase 7 WOs are accepted | Mostly serial near release; controlled-account evidence, documentation, monitoring, and dashboard polish can run in parallel before final validation |
| 8 | Advanced Agentic Workflows | PRD addendum; advanced-workflow ES; framework evaluation; ADR if LangChain, LangGraph, Temporal, or equivalent becomes justified; workflow WOs; safety review; acceptance records | Framework adoption and workflow-risk decisions accepted | Post-MVP ADP per workflow family | Parallel by workflow family if shared contracts are stable |
| 9 | Durable Orchestration | Orchestration ADR; durable-workflow ES; migration plan; rollback plan; queue/scheduler compatibility review; durability tests; orchestration WOs; recovery evidence | Durable orchestration need and chosen runtime accepted | Orchestration ADP with migration gates | Mostly serial for architecture and migration; tests and documentation can parallelize after interface freeze |
| 10 | Additional Agents | Per-agent PRD addendum or functional spec; connector-scope ADR assessment; per-agent ES; per-agent WOs; safety/privacy reviews; rollout and closeout reports | Connector permissions, data handling, and action-risk boundaries accepted per agent | Agent-family ADPs after reusable platform contracts prove stable | High parallel potential across independent agents once shared framework and policy contracts are stable |
| 11 | Enterprise Features | Enterprise PRD; enterprise ES; ADRs for SSO, RBAC, multi-user operation, tenancy, secrets, networking, and support model; security/governance reviews; enterprise WOs; support readiness evidence | Enterprise identity, tenancy, authorization, support, and deployment boundaries accepted | Enterprise readiness ADP split by capability domain | Parallel only after enterprise architecture boundaries are accepted; identity/tenancy/security remain serial gates |

## 5. Autonomous Delivery Wave Plan

ADPs should schedule WOs by dependency wave, not by document type. Each WO in a
future ADP should declare `depends_on`, `blocked_by`, `parallel_safe_with`,
file/domain boundaries, validation commands, evidence requirements, and
stop-and-ask triggers.

| Wave | Phase focus | Dependency gate | Parallel lanes | Serial follow-up | Autonomy boundary |
| --- | --- | --- | --- | --- | --- |
| Wave 0 | Phase 5 planning | ES-005 accepted; ADR assessment complete; no unresolved architecture decision | Completed Phase 5 artifact drafting and acceptance | ES-005, WO-027 through WO-035, and ADP-002 were accepted before code | Complete |
| Wave 1 | Generic contracts | Accepted Phase 5 WOs and ADP-002 | Completed WO-027 agent runtime/registry, WO-029 governed knowledge facts, and WO-031 approval/manual-handling | Completed WO-028 run lifecycle, WO-030 knowledge Q&A, WO-033 events, WO-034 dashboard compatibility, WO-032 facts-used, and WO-035 closeout | Complete; no Gmail-specific behavior or live provider calls were introduced |
| Wave 2 | Dashboard integration | Stable backend API/auth/session contracts from Phase 5 | Real API integration; loading/error/empty states; dashboard audit/approval views; fixture-removal evidence | Operator acceptance and dashboard productization closeout | No production deployment authority unless Phase 7 release plan grants it |
| Wave 3 | Gmail MVP candidate | Phase 5 contracts merged; ES-006, exact Google scopes, ADP-003, and Gmail WOs accepted; Gmail credentials boundary approved | Gmail connector/OAuth scaffold; message eligibility/classification; suppression guardrail; low-risk actions; ask-instead-of-guess; safety/privacy tests | Draft/evidence generation, approval/send continuation, operational reconciliation, controlled-account verification, and safety acceptance follow by dependency | Must stop before live credentials or real account effects unless explicitly authorized |
| Wave 4 | Operational MVP release | Phase 6 candidate completed; ES-007, release plan, and runbooks accepted | Controlled-account evidence, monitoring, rollback docs, deployment verification, final dashboard polish, residual-risk review | Release candidate validation, production cutover decision, and MVP acceptance | Live production deployment requires explicit release authority |
| Wave 5 | Post-MVP expansion | MVP accepted and stable | Independent agents, workflow families, documentation, and tests | Shared platform migrations, durable orchestration, or enterprise identity gates | Do not add frameworks, multi-user behavior, or enterprise controls without ADR/ES authority |

## 6. Issues, Unknowns, and TBD Decisions

The artifact set above is a best-effort planning view. The following items may
change the phase sequence, scope, or governing artifacts when they are decided:

- whether remaining Phase 4 dashboard productization is absorbed into Phase 7
  MVP-critical dashboard readiness or remains a separately governed lane;
- the MVP definition of acceptable Gmail risk, test coverage, data handling,
  and production-effect limits;
- controlled-account execution authorization and whether any deferral is
  acceptable before MVP release;
- whether Google Drive is an MVP dependency or should be deferred;
- the exact clinical/protected-health-information suppression policy and its
  validation thresholds;
- the minimum MVP observability stack beyond Render logs, health checks, and
  lightweight owner alerts;
- whether plain Python/direct SDK contracts remain sufficient or a workflow
  framework becomes justified under the framework-adoption policy;
- production environment count, deployment approvals, rollback ownership, and
  the exact point at which the maintainer release decision is required;
- the maximum number of parallel implementation agents that should be active on
  the same branch family without increasing review and merge risk;
- the exact WO dependency fields and naming convention to preserve during
  ADP-004 execution;
- measurable acceptance criteria for normal single-owner use; and
- the intentionally speculative Phase 8-11 artifacts, which must be revised
  when those phases are entered.

## 7. MVP Success Criteria

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

## 8. MVP Exit Criteria

The project exits MVP and enters post-MVP expansion only after:

- Phase 7 is complete;
- the Gmail Agent has been used successfully in normal single-owner operation;
- known MVP defects are triaged with no unresolved safety, security, or data
  loss blockers;
- monitoring and manual recovery are sufficient for initial personal use;
- residual risks are accepted and documented;
- Phase 8+ scope is approved through new Engineering Specifications, ADRs, or
  Work Orders as required.

## 9. Immediate Next Governance Step

Review and accept, revise, or reject the Phase 7 execution package before
release-readiness implementation begins. The recommended sequence is ES first,
WOs second, ADP third, review record fourth:

| Order | Next artifact | Purpose | Autonomy effect |
| ---: | --- | --- | --- |
| 1 | Phase 7 Engineering Specification | Proposed as ES-007; defines operational MVP release readiness, acceptance criteria, exclusions, validation, rollback, and stop-and-ask triggers | Allows Work Orders to be reviewed against stable release-readiness scope |
| 2 | Phase 7 ADR assessment | Proposed; records that existing ADRs appear sufficient if Phase 7 stays on the accepted Netlify/Render, single-owner, no-new-framework path | Prevents implementation from making deployment, secrets, monitoring, OAuth, or release decisions silently |
| 3 | Phase 7 Work Order Backlog | Proposed; breaks Phase 7 into WO-045 through WO-052 with explicit dependencies and parallel-safety guidance | Creates independently executable units after acceptance |
| 4 | ADP-004: Phase 7 Operational MVP Release | Proposed and blocked pending acceptance; groups WOs into dependency waves and parallel lanes with validation, PR/CI, merge, evidence, and stop-and-ask rules | Authorizes uninterrupted execution only after ES-007, WOs, and ADP-004 are accepted |
| 5 | ES-007 Review Record | Proposed; records maintainer acceptance, requested revisions, or rejection | Converts the proposed package into accepted implementation authority only if the maintainer approves |

Phase 7 must not silently become production cutover. Production deployment,
personal mailbox use, and MVP acceptance require explicit release authority.
