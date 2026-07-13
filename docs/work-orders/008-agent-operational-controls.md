# Work Order 008 - Agent Operational Controls

**ID:** AGENT-CONTROLS-008
**Status:** Frontend Prototype Authorized
**Authorized by:** Product owner direction in the Atlas design review
**Depends on:** Work Order 007 - Agent Details

## Objective

Add governed `Run Now`, `Pause Agent`, and `Resume Agent` controls to the Agent Details experience while preserving the separation between the Atlas control plane and execution plane.

## Product Decisions

- `Run Now` is the primary Agent Details action.
- `Pause Agent` stops future scheduled starts; it does not terminate an active run.
- A paused agent may still be run manually when policy and permissions allow.
- `Stop Current Run` is a separate higher-risk capability and is out of scope.
- Agents with a run already active or queued cannot create an accidental duplicate manual run.

## Authorized Frontend Scope

- Header actions for run, pause, and resume.
- Confirmation dialogs that explain scope and consequences.
- Visible duplicate-run prevention for running and queued states.
- Prototype-only local feedback for design review.
- Explicit disclosure that no runtime or schedule mutation is performed.
- Component tests for the interaction contract.

## Required Runtime Integration

The controls must not be connected to production behavior until the implementation provides:

- Authenticated and authorized mutation endpoints.
- Role and permission enforcement.
- Policy evaluation before manual execution.
- Agent, connector, configuration, environment, and budget validation.
- Idempotency and concurrency protection.
- Persistent run creation and queue publication.
- Append-only audit events with actor, action, reason, timestamp, and correlation ID.
- Structured errors and observable state transitions.
- Approval routing for actions classified as high risk.

## Out of Scope

- Real agent execution or queue integration.
- Persistent schedule changes.
- Stop or cancel current run.
- Approval and rejection mutations.
- Production RBAC implementation.

## Acceptance Criteria

- `Run Now` is visible as the primary action.
- `Pause Agent` is visible as a secondary action and changes to `Resume Agent` in the prototype state.
- Confirmation language distinguishes pausing schedules from stopping an active run.
- Running and queued agents cannot initiate another manual run.
- The interface does not imply that a backend mutation occurred.
- The implementation remains consistent with the approved Atlas visual system.

## Closure Conditions

Frontend prototype completion does not close the operational capability. Final closure requires a follow-on engineering specification and implementation work order for the runtime API, policy, authorization, audit, queue, and persistence integration.
