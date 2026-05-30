# notes-api-smoke — hook-fired record

## Setup

| Artifact | Path |
|---|---|
| Claude Code hook definition | `module-09/.claude/hooks.json` |
| Shared smoke runner | `module-09/.claude/smoke-gate.sh` |
| Git pre-commit hook | `.git/hooks/pre-commit` |

**Bug injected** (`module-09/main.py`, `list_notes`):
```python
raise HTTPException(status_code=500, detail="injected bug")  # BUG
```

**Commands run:**
```bash
git add module-09/main.py
git commit -m "test: trigger hook (should be blocked)"
```

## Blocked-commit terminal output (real, unedited)

```
=== notes-api-smoke pre-commit gate ===
[PASS] POST /notes → 201
[FAIL] GET /notes → 200  (got HTTP 500, expected 200)
[PASS] GET /notes/2 → 200
[PASS] PATCH /notes/2 → 200
[PASS] DELETE /notes/2 → 204
[PASS] GET /notes/999 → 404
5/6 checks passed.

COMMIT BLOCKED — fix the failing endpoint(s) and try again.
exit:1
```

The commit did not complete. `git commit` exited 1.

## How the hook is wired

`module-09/.claude/hooks.json` defines a Claude Code `PreToolUse` hook that intercepts any `Bash` tool call containing `git commit` and delegates to `smoke-gate.sh`. The same script is called by `.git/hooks/pre-commit`, which is what fired here (git hooks are session-independent and fire for every `git commit` regardless of how it is invoked).

## After revert

Bug removed; `module-09/main.py` restored to its original state.
