---
name: notes-api-smoke
description: Boot a single-file FastAPI notes app and smoke-test its CRUD endpoints, printing PASS or FAIL per check.
---

## Purpose

Start a single-file FastAPI notes app with `uv run`, exercise its five CRUD endpoints with `curl`, and assert each returns the correct HTTP status code. Also verifies that fetching a non-existent note returns 404. Results are printed as `PASS` or `FAIL` per check so failures are immediately visible in CI or a terminal.

## When to use it

- After writing or modifying a FastAPI notes app to confirm all CRUD endpoints are wired correctly before committing.
- In a CI smoke-test step that needs a fast, dependency-light sanity check against a running server.
- When onboarding to an unfamiliar notes-API repo and wanting to verify the server starts and responds as documented.
- After a refactor (e.g. changing route paths, status codes, or DB layer) to catch regressions without a full test suite.

## Prompt body

```text
Smoke-test a single-file FastAPI notes app.

Inputs (the user must supply these before you begin):
- MODULE_PATH: path to the .py file containing the FastAPI `app` object
  (e.g. ./api/notes.py)
- PORT: local TCP port to bind the server on (e.g. 8000)

Steps:

1. Start the server in the background:
     uv run --with fastapi --with uvicorn \
       uvicorn <module>:app --host 127.0.0.1 --port <PORT> &
   where <module> is the dot-path derived from MODULE_PATH
   (strip leading "./" and ".py", replace "/" with ".").
   Capture the PID. Wait up to 5 seconds for the server to accept
   connections by polling `curl -s -o /dev/null http://127.0.0.1:<PORT>/notes`.

2. Run the following six checks in order. For each, emit exactly one line:
     [PASS] <label>
   or
     [FAIL] <label>  (got HTTP <actual>, expected <expected>)

   Check 1 — POST /notes returns 201
     curl -s -o /dev/null -w "%{http_code}" \
       -X POST http://127.0.0.1:<PORT>/notes \
       -H "Content-Type: application/json" \
       -d '{"title":"smoke","body":"test"}'
     Capture the returned id from the JSON body (re-run with -i or store body).

   Check 2 — GET /notes returns 200
     curl -s -o /dev/null -w "%{http_code}" \
       http://127.0.0.1:<PORT>/notes

   Check 3 — GET /notes/<id> returns 200  (use id from Check 1)
     curl -s -o /dev/null -w "%{http_code}" \
       http://127.0.0.1:<PORT>/notes/<id>

   Check 4 — PATCH /notes/<id> returns 200
     curl -s -o /dev/null -w "%{http_code}" \
       -X PATCH http://127.0.0.1:<PORT>/notes/<id> \
       -H "Content-Type: application/json" \
       -d '{"title":"updated"}'

   Check 5 — DELETE /notes/<id> returns 204
     curl -s -o /dev/null -w "%{http_code}" \
       -X DELETE http://127.0.0.1:<PORT>/notes/<id>

   Check 6 — GET /notes/999 returns 404
     curl -s -o /dev/null -w "%{http_code}" \
       http://127.0.0.1:<PORT>/notes/999

3. Kill the server (kill <PID>; wait for it to exit).

4. Print a final summary line:
     <N>/6 checks passed.
   Exit 0 if all 6 passed, exit 1 otherwise.
```

## Expected inputs

- **MODULE_PATH** — relative or absolute path to the `.py` file that defines the FastAPI `app` object (e.g. `./notes.py`, `api/notes_api.py`).
- **PORT** — integer port number the smoke-test server should bind to (e.g. `8000`). Must be free on the host.

## Expected outputs

- Six labelled result lines printed to stdout, one per check:
  ```
  [PASS] POST /notes → 201
  [PASS] GET /notes → 200
  [PASS] GET /notes/<id> → 200
  [PASS] PATCH /notes/<id> → 200
  [PASS] DELETE /notes/<id> → 204
  [PASS] GET /notes/999 → 404
  ```
- A summary line: `6/6 checks passed.`
- Exit code `0` on full pass, `1` if any check fails.

## Worked example

**Scenario**: verify `module-09/notes_api.py` after a fresh checkout.

```bash
#!/usr/bin/env bash
set -euo pipefail

MODULE_PATH="module-09/notes_api.py"
PORT=8099
# Derive uvicorn module path: strip leading "./" or "/", drop ".py", / → .
MODULE_ID=$(echo "$MODULE_PATH" | sed 's|^\./||; s|\.py$||; s|/|.|g')

PASS=0; FAIL=0

check() {
  local label="$1" expected="$2" actual="$3"
  if [ "$actual" = "$expected" ]; then
    echo "[PASS] $label"
    ((PASS++)) || true
  else
    echo "[FAIL] $label  (got HTTP $actual, expected $expected)"
    ((FAIL++)) || true
  fi
}

# 1. Start server
uv run --with fastapi --with uvicorn \
  uvicorn "$MODULE_ID:app" --host 127.0.0.1 --port "$PORT" \
  > /tmp/notes_smoke_server.log 2>&1 &
SERVER_PID=$!

# Wait for server (up to 5 s)
for i in $(seq 1 10); do
  curl -s -o /dev/null "http://127.0.0.1:$PORT/notes" && break
  sleep 0.5
done

BASE="http://127.0.0.1:$PORT"

# 2. POST /notes → 201; capture id
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "$BASE/notes" \
  -H "Content-Type: application/json" \
  -d '{"title":"smoke","body":"test"}')
CODE=$(echo "$RESPONSE" | tail -1)
NOTE_ID=$(echo "$RESPONSE" | head -1 | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
check "POST /notes → 201" "201" "$CODE"

# 3. GET /notes → 200
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes")
check "GET /notes → 200" "200" "$CODE"

# 4. GET /notes/<id> → 200
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes/$NOTE_ID")
check "GET /notes/$NOTE_ID → 200" "200" "$CODE"

# 5. PATCH /notes/<id> → 200
CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X PATCH "$BASE/notes/$NOTE_ID" \
  -H "Content-Type: application/json" \
  -d '{"title":"updated"}')
check "PATCH /notes/$NOTE_ID → 200" "200" "$CODE"

# 6. DELETE /notes/<id> → 204
CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X DELETE "$BASE/notes/$NOTE_ID")
check "DELETE /notes/$NOTE_ID → 204" "204" "$CODE"

# 7. GET /notes/999 → 404
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes/999")
check "GET /notes/999 → 404" "404" "$CODE"

# Teardown
kill "$SERVER_PID" 2>/dev/null; wait "$SERVER_PID" 2>/dev/null || true

TOTAL=$((PASS + FAIL))
echo "$PASS/$TOTAL checks passed."
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
```

**Expected terminal output** (all passing):

```
[PASS] POST /notes → 201
[PASS] GET /notes → 200
[PASS] GET /notes/1 → 200
[PASS] PATCH /notes/1 → 200
[PASS] DELETE /notes/1 → 204
[PASS] GET /notes/999 → 404
6/6 checks passed.
```
