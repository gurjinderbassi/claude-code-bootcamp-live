# MCP context brief

Task:   Open one GitHub issue reporting the notes-api-smoke result for module-09/main.py
Server: github (MCP) — github/github-mcp-server
Scope:  gurjinderbassi/claude-code-bootcamp-live only — no other repos touched
Action: create_issue — exactly one issue created, no deletes, no branch writes
Stop:   immediately after the issue URL is returned (or dry-run logged if server absent)

---

# MCP run record

**Date:** 2026-05-30  
**Mode:** DRY-RUN — no GitHub MCP server is configured in `~/.claude/settings.json`  
**Skill result used:** output from `module-09/invocation.md` (6/6 PASS)

## Why dry-run

`ToolSearch` returned no `mcp__github__*` tools. `~/.claude/settings.json` is `{}` and
`.claude/settings.json` does not exist. `gh` CLI is also absent. No live call is possible
without a server; the exact call that would have been made is recorded below.

## Tool call that WOULD be made

If the GitHub MCP server were configured (e.g. as server name `github`), Claude Code
would invoke:

**Tool:** `mcp__github__create_issue`

**Input (JSON):**
```json
{
  "owner": "gurjinderbassi",
  "repo": "claude-code-bootcamp-live",
  "title": "notes-api-smoke: PASS on 2026-05-30",
  "body": "## notes-api-smoke results\n\n**Target:** `module-09/main.py` via `module-09.main:app`  \n**Port:** 8099  \n**Runner:** `python3 -m uvicorn`  \n**Date:** 2026-05-30  \n**Skill:** `module-09/notes-api-smoke/SKILL.md`\n\n### Output\n\n```\n[PASS] POST /notes → 201\n[PASS] GET /notes → 200\n[PASS] GET /notes/1 → 200\n[PASS] PATCH /notes/1 → 200\n[PASS] DELETE /notes/1 → 204\n[PASS] GET /notes/999 → 404\n6/6 checks passed.\n```\n\n*Opened automatically by the `notes-api-smoke` skill (module-09).*"
}
```

**Expected response shape:**
```json
{
  "number": 1,
  "html_url": "https://github.com/gurjinderbassi/claude-code-bootcamp-live/issues/1",
  "state": "open",
  "title": "notes-api-smoke: PASS on 2026-05-30"
}
```

## How to make this live

Add the GitHub MCP server to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm",
               "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
               "ghcr.io/github/github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"
      }
    }
  }
}
```

Then re-run this task. Claude Code will call `mcp__github__create_issue` with the JSON
above and append the live issue URL here.

---

# Live run — 2026-05-30

**Mode:** LIVE — GitHub MCP server active (`mcp__github__issue_write`)  
**Authenticated as:** gurjinderbassi  

## Tool call made

**Tool:** `mcp__github__issue_write`

**Input (JSON):**
```json
{
  "method": "create",
  "owner": "gurjinderbassi",
  "repo": "claude-code-bootcamp-live",
  "title": "notes-api-smoke: PASS on 2026-05-30",
  "body": "## notes-api-smoke results\n\n**Target:** `module-09/main.py` via `module-09.main:app`\n**Port:** 8099\n**Runner:** `python3 -m uvicorn`\n**Date:** 2026-05-30\n**Skill:** `module-09/notes-api-smoke/SKILL.md`\n\n### Output\n\n```\n[PASS] POST /notes → 201\n[PASS] GET /notes → 200\n[PASS] GET /notes/1 → 200\n[PASS] PATCH /notes/1 → 200\n[PASS] DELETE /notes/1 → 204\n[PASS] GET /notes/999 → 404\n6/6 checks passed.\n```\n\n*Opened automatically by the `mcp-run` skill (module-09).*"
}
```

## Response

```json
{
  "id": "4555194094",
  "url": "https://github.com/gurjinderbassi/claude-code-bootcamp-live/issues/1"
}
```

**Issue URL:** https://github.com/gurjinderbassi/claude-code-bootcamp-live/issues/1
