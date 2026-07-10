# Atlas Information Architecture

## Purpose

This document defines the structure of the Atlas user experience.

It answers:

- What screens exist?
- How users navigate?
- What belongs on each screen?
- Which actions are primary?
- Which information belongs together?
- What should never require more than two clicks?

This document intentionally does **not** define visual design.

---

# Product Philosophy

Atlas is an operational platform.

The interface should answer operational questions before configuration questions.

Information comes first.

Configuration comes second.

---

# Navigation Model

Primary Navigation

Overview

Agents

Schedules

Runs

Outputs

Approvals

Connectors

Settings

Future

Costs

Policies

Plugins

Administration

---

# User Journey

```
Login

↓

Overview

↓

Select Agent

↓

Agent Detail

↓

Run

↓

Review Results

↓

Approve (if required)

↓

Review Outputs
```

---

# Screen Hierarchy

Atlas

├── Overview

├── Agents

│

├── Agent Detail

│ ├── Overview

│ ├── Configuration

│ ├── Schedule

│ ├── Runs

│ ├── Outputs

│ ├── Health

│ ├── Policies

│ ├── Connectors

│ └── Version History

│

├── Schedules

│

├── Runs

│ └── Run Detail

│ ├── Timeline

│ ├── Logs

│ ├── Outputs

│ ├── Tool Calls

│ ├── Model Calls

│ └── Retry

│

├── Outputs

│

├── Approvals

│ └── Approval Detail

│

├── Connectors

│ └── Connector Detail

│

└── Settings

---

# Overview Dashboard

Purpose

Answer:

"What is happening right now?"

Primary Information

Platform Health

Active Agents

Running Agents

Upcoming Runs

Pending Approvals

Connector Health

Recent Activity

Issues

Recent Outputs

Recent Failures

Today's Cost

Primary Actions

Run Agent

Approve

View Failed Run

Reconnect Connector

---

# Agent List

Purpose

Answer:

"What agents exist?"

Primary Information

Name

Description

Status

Health

Last Run

Next Run

Owner

Schedule

Actions

Primary Action

Open Agent

Secondary Actions

Run

Pause

Disable

---

# Agent Detail

Purpose

Answer:

"What is this agent doing?"

Primary Sections

Overview

Configuration

Schedule

Runs

Outputs

Health

Permissions

Connectors

Policies

Version

Primary Action

Run Now

---

# Runs

Purpose

Answer:

"What happened?"

Primary Information

Status

Timeline

Duration

Errors

Outputs

Tool Calls

Model Calls

Logs

Retry

---

# Outputs

Purpose

Answer:

"What did the agent produce?"

Information

Summary

Files

Drafts

Reports

Links

Metadata

---

# Approvals

Purpose

Answer:

"What needs my decision?"

Information

Risk

Action

Reason

Context

Approve

Reject

---

# Connectors

Purpose

Answer:

"Can my agents reach external systems?"

Information

Connection

Status

Scopes

Health

Last Success

Reconnect

---

# Settings

Purpose

Configure Atlas.

---

# Mobile Strategy

Desktop

Full navigation.

Dense information.

Tables.

Timeline.

Multiple panels.

Tablet

Reduced navigation.

Two-column layouts.

Mobile

Cards.

Bottom navigation.

Condensed metrics.

Quick Approvals.

Run Agent.

Review Health.

---

# Navigation Principles

One navigation system.

Never nest more than two levels.

Always provide breadcrumbs.

Never open more than one modal at a time.

Primary action always visible.

---

# Success Criteria

The user should answer these questions in under five seconds:

Is everything healthy?

Which agents need me?

What failed?

What runs next?

What requires approval?

Where do I click next?
