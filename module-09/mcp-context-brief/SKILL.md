---
name: mcp-context-brief
description: Prepare a one-page context brief for an MCP-connected tool (Jira / Slack / GitHub / Drive) before invoking it, so the agent acts on a focused slice instead of slurping the whole workspace.
---

## Purpose

MCP servers expose large, fuzzy surfaces (every issue, every channel, every doc). Letting an agent free-fetch is slow, expensive, and leaks context to the wrong tool. This skill produces a **bounded brief** — the agent reads only the slice that matches today's task.

The brief is also auditable: after the run, you can see exactly what context was authorised.

## When to use

- Before invoking any MCP-mediated action that touches a system of record (issue trackers, chat, docs, code hosting).
- When the same MCP server is used by multiple agents in a multi-agent run (the brief becomes the shared contract).
- When you want to reproduce an agent's behaviour offline (the brief is a deterministic snapshot).

Skip when: the MCP call is a single deterministic lookup (e.g., "fetch issue PROJ-123") and there is no ambiguity.

## Body

1. **State the task** in one sentence.
2. **List the MCP servers** required and the **minimum scopes** (read-only, read-write, specific repos).
3. **Define the slice**: which projects / channels / repos / time windows are in scope. Use explicit filters, not natural language.
4. **List allowed actions** the agent may invoke. Forbid everything else.
5. **Define stop conditions**: what counts as done, what counts as escalation.
6. **Attach a redaction policy**: which fields are PII / secrets and must not leave the agent's working memory.

Keep the brief under 400 words — if it grows beyond that, the task is too big and should be split.

## Inputs

- The task statement (one sentence).
- The MCP server list with their declared capabilities.
- The user's permission scope (don't widen it).

## Outputs

```text
## MCP context brief — <task name> — <YYYY-MM-DD>

**Task**: <one sentence>

**MCP servers**:
- `<server>` — scope: `<read|write>` — paths: `<glob/filter>`

**Slice**:
- Projects: <list>
- Time window: <start>..<end>
- Filters: <key=value>

**Allowed actions**:
- <verb> <object>
- <verb> <object>

**Forbidden actions**: anything not in "Allowed actions".

**Stop conditions**:
- Done when: <criterion>
- Escalate to human when: <criterion>

**Redaction**: <fields>
```

## Worked example

```text
## MCP context brief — Triage payments-team bug reports — 2026-05-28

**Task**: Cluster the last 7 days of open `payments` bugs and produce a one-paragraph severity summary.

**MCP servers**:
- `jira` — scope: read — paths: project=PAY, issuetype=Bug, status=Open
- `slack` — scope: read — paths: #payments-alerts, last 7 days

**Slice**:
- Projects: PAY
- Time window: 2026-05-21..2026-05-28
- Filters: priority in (P0, P1, P2)

**Allowed actions**:
- jira: search_issues, get_issue
- slack: search_messages, get_thread

**Forbidden actions**: jira.create_issue, jira.transition, slack.post_message.

**Stop conditions**:
- Done when: ≥1 paragraph per severity bucket produced.
- Escalate when: any P0 with no Slack acknowledgement in 24 h.

**Redaction**: customer emails, card BINs.
```

