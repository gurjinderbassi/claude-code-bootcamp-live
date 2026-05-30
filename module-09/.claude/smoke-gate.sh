#!/usr/bin/env bash
# Smoke-tests module-09/main.py on PORT (default 8099).
# Exits 0 if all 6 checks pass, 1 if any fail.
set -uo pipefail

PORT=${PORT:-8099}
MODULE_ID="module-09.main"

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

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

python3 -m uvicorn "$MODULE_ID:app" --host 127.0.0.1 --port "$PORT" \
  > /tmp/notes_smoke_gate.log 2>&1 &
SERVER_PID=$!

for i in $(seq 1 10); do
  curl -s -o /dev/null "http://127.0.0.1:$PORT/notes" 2>/dev/null && break
  sleep 0.5
done

BASE="http://127.0.0.1:$PORT"

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "$BASE/notes" \
  -H "Content-Type: application/json" \
  -d '{"title":"hook-smoke","body":"test"}')
CODE=$(echo "$RESPONSE" | tail -1)
NOTE_ID=$(echo "$RESPONSE" | head -1 \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "0")
check "POST /notes → 201" "201" "$CODE"

CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes")
check "GET /notes → 200" "200" "$CODE"

CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes/$NOTE_ID")
check "GET /notes/$NOTE_ID → 200" "200" "$CODE"

CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X PATCH "$BASE/notes/$NOTE_ID" \
  -H "Content-Type: application/json" \
  -d '{"title":"updated"}')
check "PATCH /notes/$NOTE_ID → 200" "200" "$CODE"

CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X DELETE "$BASE/notes/$NOTE_ID")
check "DELETE /notes/$NOTE_ID → 204" "204" "$CODE"

CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes/999")
check "GET /notes/999 → 404" "404" "$CODE"

kill "$SERVER_PID" 2>/dev/null; wait "$SERVER_PID" 2>/dev/null || true

TOTAL=$((PASS + FAIL))
echo "$PASS/$TOTAL checks passed."
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
