# Human Approvals Architecture and Security Review

**Status:** Review Complete - Approved After Revision
**Date:** 2026-07-13
**Reviewed Artifact:** `docs/architecture/13-human-approvals.md` version 0.1
**Functional Baseline:** `docs/specifications/human-approvals-functional-specification.md` version 1.0
**Review Type:** Architecture and Security Gate
**Disposition:** Approved

---

## 1. Executive Assessment

The Human Approvals architecture is directionally sound and conforms to the
existing Atlas component and trust-boundary model.

The draft correctly:

- Extends the existing Approval Service instead of introducing a duplicate service.
- Preserves Policy Engine authority.
- Treats agent and model output as untrusted.
- Binds approval to an exact proposed action.
- Separates approval decision from execution outcome.
- Requires evidence before approval.
- Preserves append-oriented auditability.
- Avoids new deployment containers and frameworks.
- Defers team, bulk, delegation, and external-channel behavior.

The architecture is not yet ready for approval. Five high-priority findings
affect correctness and security, and five medium-priority findings require
resolution before an Engineering Specification can be considered ready.

No implementation should begin from version 0.1.

---

## 2. Findings

### AR-001 - External execution cannot guarantee absolute at-most-once outcome

**Priority:** High
**Affected sections:** 7.5, 8.8, 13.3, 14.3, 22

The draft states that an approved external action executes at most once. Atlas
can prevent duplicate authorization and duplicate local dispatch, but it cannot
always prove that an external provider did or did not apply an action when a
timeout, connection loss, or provider failure occurs after submission.

Treating at-most-once execution as an absolute guarantee creates a dangerous
recovery condition: retrying may duplicate the action, while refusing to retry
may leave an intended action incomplete.

**Required resolution:**

- Guarantee one terminal approval decision and one authorized action intent.
- Use a stable idempotency identity for dispatch.
- Use provider idempotency where supported.
- Prevent automatic retry when outcome is indeterminate and provider
  idempotency is unavailable.
- Add `OutcomeUnknown` or `Indeterminate` as an execution outcome.
- Require reconciliation or operator investigation before retrying an
  indeterminate external action.
- Never reinterpret an indeterminate execution as an approval failure.

This resolution also requires a corresponding functional-specification update
because execution outcome is user-visible.

### AR-002 - Historical evidence integrity strategy is unresolved

**Priority:** High
**Affected sections:** 10.5, 11.4, 13.4, 21

The draft requires preservation of the context reviewed by the operator but
leaves snapshot, version-reference, and integrity-reference behavior open.
Without a defined strategy, mutable evidence could change after the decision,
making historical review misleading or unverifiable.

Copying all evidence into the approval record would create a different risk by
duplicating sensitive content and weakening retention controls.

**Required resolution:**

Adopt an immutable decision-context manifest containing:

- Approval and action identity.
- Evidence-reference identities.
- Source versions when available.
- Integrity digests for decision-relevant content.
- Capture timestamps.
- Redaction and truncation metadata.
- Sensitivity and retention classifications.

Snapshot only the minimum content required to explain the decision when a
stable versioned source is unavailable. Keep large or sensitive content in its
governed source and preserve a protected reference plus integrity identity.

The exact digest algorithm, storage shape, and retention implementation belong
in the Engineering Specification or a data-design artifact.

### AR-003 - Decision, audit, and continuation consistency is unresolved

**Priority:** High
**Affected sections:** 8.3, 14.4, 15.4, 16, 21

The architecture correctly states that an approved decision must not exist
without recoverable continuation, but it does not choose a consistency pattern.
Independent writes could produce:

- An approved record with no continuation.
- A continuation without a durable decision.
- A decision without required audit evidence.
- Duplicate continuation publication after recovery.

**Required resolution:**

Use one authoritative transaction to record:

- Approval state transition.
- Reviewer and decision reason.
- Durable audit event.
- Durable continuation intent.

Publish or dispatch continuation asynchronously from the durable intent. The
consumer must be idempotent and must revalidate the action before execution.

A transactional-outbox pattern is the recommended default because PostgreSQL
is already the planned system of record. Adoption must be recorded in the
appropriate architecture or ADR process if review determines that it changes
the canonical data or reliability architecture materially.

### AR-004 - Reviewer authorization and step-up requirements are unresolved

**Priority:** High
**Affected sections:** 8.3, 13.2, 13.5, 21

Authenticated identity alone is insufficient for human authorization. The
architecture needs a deny-by-default eligibility model and a clear point at
which reviewer permission is evaluated.

**Required resolution:**

- Evaluate reviewer eligibility at decision time, not only when detail loads.
- Scope eligibility to workspace, environment, action class, and risk where applicable.
- Prevent agents and service identities from acting as human reviewers.
- Record the evaluated reviewer identity and authorization context.
- Require step-up authentication for Critical decisions.
- Require step-up authentication for High-risk external communication,
  deletion, public sharing, financial actions, credential or permission
  changes, and policy exceptions.
- Allow future separation-of-duties rules without changing approval identity.

The exact identity provider, role model, permission model, and reauthentication
mechanism remain separate specifications.

### AR-005 - Audit failure behavior needs a durable boundary

**Priority:** High
**Affected sections:** 15.4, 16, 21

The phrase `required audit evidence cannot be produced` does not distinguish
durable audit recording from downstream log export or observability delivery.
Failing every decision because an external telemetry destination is unavailable
would reduce availability without improving decision integrity.

**Required resolution:**

- A decision fails closed if its durable local audit event cannot be recorded
  in the authoritative transaction.
- A downstream telemetry, analytics, or export failure does not reverse or
  reject a durably recorded decision.
- Downstream delivery failure creates retryable operational state, metrics, and
  alerts.
- Audit export retries must not duplicate logical audit events.

### AR-006 - Clarification provenance and trust are underspecified

**Priority:** Medium
**Affected sections:** 8.5, 10.6, 21

Clarification becomes approval evidence, but the draft does not define which
sources may provide it or how its provenance is trusted.

**Required resolution:**

- The initial capability accepts clarification only through Atlas from an
  authenticated human actor or a trusted internal system actor.
- Every response records actor type, actor identity, timestamp, source, and
  evidence references.
- Clarification content is untrusted and follows the same validation,
  rendering, sensitivity, and audit controls as other evidence.
- External email, chat, or notification replies are not accepted as approval
  clarification in the initial capability.
- Material changes to action, target, or proposed content require a new approval
  instead of clarification.

### AR-007 - Expiry requires an authoritative time and race rule

**Priority:** Medium
**Affected sections:** 8.6, 15.5, 18

The draft states that time must be authoritative but does not explicitly define
the acceptance rule at the expiry boundary.

**Required resolution:**

- The control-plane service time is authoritative for decision acceptance.
- Browser time is presentation-only.
- A decision is valid only if accepted before the canonical expiry instant.
- No grace period applies to authorization.
- Clock anomalies and unavailable authoritative time fail closed.
- Near-expiry interface thresholds do not alter the canonical decision window.

### AR-008 - Retention and deletion boundaries need classification

**Priority:** Medium
**Affected sections:** 10, 11.4, 13.4, 16, 21

Approval history requires durable accountability, while evidence and
clarification may contain sensitive content subject to shorter retention.
Treating all approval data as one retention unit would either lose audit value
or retain excessive sensitive data.

**Required resolution:**

Classify retention independently for:

- Approval identity and terminal decision metadata.
- Audit events.
- Decision-context manifest.
- Decision reasons.
- Evidence content.
- Clarification content.
- Execution-result content.

Retain durable decision metadata and integrity references according to audit
policy. Apply source-specific and sensitivity-specific retention to content.
When content expires, history must state that retained evidence content is no
longer available while preserving decision provenance and integrity metadata.

Exact durations require later product, privacy, legal, and security decisions.

### AR-009 - Untrusted evidence needs explicit content-isolation controls

**Priority:** Medium
**Affected sections:** 7.1, 11, 13.4

The draft treats model output as untrusted but does not fully specify the UI and
service treatment of malicious evidence. Email, HTML, documents, and generated
content may contain prompt injection, active content, deceptive formatting, or
unsafe links.

**Required resolution:**

- Normalize and validate evidence metadata at ingestion boundaries.
- Render previews as inert content using allowlisted formats.
- Never execute scripts, active document content, remote embeds, or provider UI.
- Make external links explicit and safe to inspect.
- Visually distinguish source evidence, agent rationale, policy context, and
  operator-authored content.
- Do not send evidence to a model merely because the operator opened it.
- Treat model-generated summaries as untrusted derived evidence with source links.
- Preserve redaction before logs, analytics, and audit export.

### AR-010 - Approval-flood and queue-starvation controls are absent

**Priority:** Medium
**Affected sections:** 4, 17, 19

An unhealthy or manipulated agent could create excessive approval requests,
overload the operator, hide urgent requests, or consume storage and
notification capacity.

**Required resolution:**

- Monitor request volume by agent, action class, policy, and environment.
- Detect repeated materially identical requests.
- Apply bounded creation or notification controls without silently authorizing actions.
- Preserve Critical and near-expiry visibility during backlog conditions.
- Alert on abnormal approval volume and repeated evidence-incomplete requests.
- Permit emergency agent pause or disable through the existing governed control path.
- Do not automatically merge approvals whose exact action bindings differ.

The detailed rate, deduplication, and suppression policies belong in later
specifications.

---

## 3. Security Threat Review

| Threat | Required architectural control |
| --- | --- |
| Approval substitution | Exact action, target, content, agent, and run binding |
| Replay | Terminal-state enforcement, concurrency identity, idempotent decision handling |
| Duplicate external action | Stable dispatch identity, provider idempotency, indeterminate-outcome handling |
| Stale reviewer screen | Expected revision and canonical-state conflict response |
| Unauthorized reviewer | Decision-time authorization and deny-by-default scope |
| Reviewer session compromise | Risk-based step-up authentication and complete audit provenance |
| Evidence mutation | Immutable decision-context manifest and integrity identities |
| Malicious evidence | Inert rendering, validation, redaction, and source separation |
| Prompt injection | Treat evidence and model summaries as untrusted; no automatic model use |
| Audit tampering | Authoritative durable audit event in the decision transaction |
| Audit-export outage | Durable retry without reversing a committed decision |
| Approval flooding | Volume metrics, anomaly alerts, bounded creation and notification |
| Expiry race | Authoritative service time and no post-expiry grace |
| Sensitive-data leakage | Minimum queue content, governed references, independent retention |
| Confused deputy | Policy revalidation and runtime action-identity verification |

No reviewed threat requires a new deployment container. The existing service
boundaries can enforce the required controls if the detailed decisions are
adopted.

---

## 4. Recommended Resolutions to Architecture Questions

| Question | Recommended resolution |
| --- | --- |
| Evidence history | Immutable decision-context manifest with version and integrity references; minimum snapshots only |
| Concurrency identity | Monotonic approval revision required by every decision attempt |
| Decision and continuation consistency | Authoritative transaction plus durable outbox or equivalent recoverable intent |
| At-most-once continuation | Stable dispatch identity, idempotent consumer, connector idempotency, indeterminate outcome when uncertain |
| Clarification provenance | Authenticated Atlas human or trusted internal actor only in initial capability |
| Reauthentication | Critical always; High for external communication, destructive, public-sharing, financial, credential, permission, and policy-exception actions |
| Reviewer eligibility | Deny by default; evaluate workspace, environment, action, and risk scope at decision time |
| Audit failure | Durable local audit failure blocks decision; downstream export failure retries asynchronously |
| Retention | Separate durable metadata and integrity retention from sensitive content retention |
| Notifications | Deferred; notifications deep-link to Atlas and cannot record decisions |

---

## 5. Required Specification Changes

The architecture specification must be revised to:

1. Replace absolute at-most-once execution language with duplicate-prevention and indeterminate-outcome handling.
2. Add `OutcomeUnknown` or `Indeterminate` to execution outcomes.
3. Adopt the immutable decision-context manifest.
4. Define the authoritative transaction and durable continuation-intent boundary.
5. Define decision-time reviewer authorization and risk-based step-up requirements.
6. Distinguish durable audit recording from downstream audit export.
7. Define clarification provenance and changed-action behavior.
8. Define service-authoritative expiry acceptance.
9. Add independent retention classifications.
10. Add explicit untrusted-evidence isolation.
11. Add approval-flood observability and protective controls.

The Functional Specification must be revised to expose an indeterminate
execution outcome and its operator recovery experience.

---

## 6. Review Disposition

**Changes required.**

The architecture is compatible with Atlas and requires no new container or
framework. It is conditionally approved in direction, but version 0.1 is not
approved as an implementation basis.

Architecture approval may be granted after:

1. The recommendations in Section 4 are accepted or replaced by approved alternatives.
2. The Functional Specification includes an indeterminate execution outcome.
3. The Architecture Specification incorporates all required changes in Section 5.
4. Security confirms reviewer authorization, step-up, evidence isolation, and audit-failure boundaries.
5. Any material data or reliability pattern change follows the ADR process.

---

## 7. Recommended Next Step

Conduct a focused Architecture Decision Review of the ten recommendations in
Section 4. After approval, revise the Functional and Architecture
Specifications and perform a final conformance review.

Do not create an Engineering Specification or implementation Work Order until
the Architecture Specification is approved.

---

## 8. Final Conformance Review

The approved recommendations were incorporated into Human Approvals Functional
Specification version 1.1, Human Approvals Architecture version 1.0, and
ADR-002.

Final review confirms that all ten findings are resolved at the architecture
boundary: external uncertainty is explicit; evidence integrity is preserved;
decision, audit, and continuation are coordinated; reviewer eligibility and
step-up rules are defined; audit failure boundaries are safe; clarification
provenance is restricted; service time governs expiry; retention is classified;
untrusted evidence is isolated; and approval flooding is observable.

Detailed mechanisms delegated to the Engineering Specification do not block
architecture approval.

**Final disposition:** Human Approvals Architecture version 1.0 is approved as
the basis for an Engineering Specification. It does not authorize
implementation.
