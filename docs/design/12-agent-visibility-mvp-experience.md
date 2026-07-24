# Atlas Agent Visibility MVP Experience

**Status:** Active Product Design Baseline
**Version:** 1.0
**Date:** 2026-07-23
**Governing Decisions:** `ADR-008`, `ADR-009`, and `DDR-003`

## 1. Experience promise

Atlas helps an owner understand which external agents are known, trusted,
connected, healthy, failing, or no longer connected to Atlas.

The interface must be precise about the limits of that knowledge. Atlas can
show an authenticated last contact and reported execution; it cannot prove
that an external process is running, correct, or stopped.

## 2. Navigation

| Destination | Primary question |
| --- | --- |
| Overview | What needs my attention now? |
| Agents | Which agents are enrolled and what is their current relationship with Atlas? |
| Executions | What work have agents reported and what failed? |
| Alerts | Which operational conditions require attention? |
| Activity | What materially changed in Atlas? |

## 3. Overview

Overview contains:

- agents by observed connection health;
- open alerts by severity;
- recent failed executions;
- agents waiting for first connection;
- agents that became late, offline, disconnected, or recovered;
- a clear `Enroll agent` action.

It contains no schedule, approval, connector, policy, artifact, or
Atlas-dispatched work panel.

## 4. Agents

The Agents inventory shows:

- observed connection health;
- agent name and description;
- lifecycle status;
- reported health;
- environment;
- version/build;
- last contact;
- open-alert count.

Primary filters are lifecycle, observed health, reported health, environment,
and alerts. Search includes name, slug, tag, version, and environment.

## 5. Enrollment

Enrollment is an owner flow:

1. Enter identity and monitoring metadata.
2. Review what Atlas will and will not manage.
3. Create the registration.
4. Copy the one-time agent ID, API URL, credential, and configuration example.
5. Confirm that Atlas cannot recover the credential.
6. Wait for first connection or leave and return later.

The pending state explains:

- no authenticated heartbeat has been accepted;
- the external agent must be configured and running;
- Atlas will not initiate the connection.

## 6. Agent Detail

The header shows agent name, environment, lifecycle, observed connection, and
reported health without combining them into one badge.

Sections:

- At a glance
- Connection
- Executions
- Alerts
- Activity
- Integration

The Integration section shows agent ID, API base URL, contract version,
monitoring mode, and a redacted credential status. It never shows the existing
credential.

Owner actions:

- Rotate credential
- Disconnect
- Reconnect when disconnected
- Archive

There is no pause, resume, run, cancel, schedule, connector, policy, tool,
approval, or prompt control.

## 7. Executions

Executions are read-only reported records.

The inventory shows:

- outcome;
- agent;
- external execution identity;
- trigger label;
- start and completion;
- duration;
- version/build;
- normalized error code.

Detail shows the bounded summary and Atlas receipt history. It states that
Atlas did not dispatch or execute the work.

## 8. Alerts

Alerts distinguish:

- condition severity;
- open, acknowledged, and resolved state;
- source condition;
- first and last seen;
- affected agent;
- evidence such as last accepted heartbeat or failed execution count.

Acknowledgment means the owner has seen an alert. It does not mean the
condition is fixed.

## 9. Activity

Activity is a read-only material timeline containing:

- enrollment and first connection;
- credential issue, rotation, expiry, and revocation;
- health transitions;
- execution terminal outcomes;
- alert open, acknowledge, and resolve;
- disconnect, reconnect, and archive.

Routine page reads are not shown as material activity.

## 10. Critical content rules

- Use `reported` when a value came from the agent.
- Use `observed` or `last accepted` when Atlas verified receipt.
- Never say `stopped` after disconnect.
- Say `Disconnected from Atlas. The external runtime may still be running.`
- Never claim Atlas executed a reported execution.
- Never imply a credential can be recovered.
- Do not use synthetic operational data in normal production states.

## 11. Required states

Every active surface specifies:

- loading;
- empty;
- first-use;
- error;
- stale evaluation;
- pending connection;
- online;
- late;
- offline;
- disconnected;
- archived;
- partial data;
- permission denied.

## 12. Accessibility and responsive behavior

Existing Atlas design-system, theme, focus, status-icon, table, mobile-card,
and reduced-motion rules remain active.

Status must never depend on color alone. Credential copy and destructive
lifecycle confirmations must be keyboard accessible and announce outcomes.

## 13. Deferred screens

Approvals, Connectors, Policies, Artifacts, Knowledge, Settings, scheduling,
and Atlas-initiated Runs retain historical design evidence only. Reintroduction
requires a new or reactivated product and design decision.
