# Production Readiness Review — `module-04/winner/main.py`

**Date:** 2026-05-30

---

## 1. Security
**Would it hold up?** No — the API has zero authentication, zero rate-limiting, and no input size enforcement beyond Pydantic field lengths, so any anonymous caller can create, delete, or search all notes.
**Biggest risk:** Unauthenticated write/delete access; a single `DELETE /notes/{id}` loop wipes the entire dataset.
**Smallest next step:** Add a static `Authorization: Bearer <token>` check as a FastAPI dependency on all mutating routes (10 lines, no extra deps).

---

## 2. Observability
**Would it hold up?** No — the app emits no structured logs, no request IDs, no error metrics, and no health endpoint beyond what uvicorn prints to stderr by default.
**Biggest risk:** A silent `sqlite3.OperationalError` (disk full, locked DB) will surface only as a 500 with no trace context, making on-call diagnosis a blind grep through uvicorn stdout.
**Smallest next step:** Add a `GET /healthz` route that does a `SELECT 1` and returns `{"status":"ok"}` — gives load-balancers and uptime monitors something concrete to probe.

---

## 3. Deployment
**Would it hold up?** No — `DB_FILE = "notes.db"` is a hardcoded relative path with no env-var override, and the README tells you to run `uvicorn main:app --reload` (dev mode, single worker, no port binding).
**Biggest risk:** Multi-worker or multi-instance deploys (e.g. `--workers 4`) will race on the same SQLite file; SQLite WAL handles concurrent reads but not multi-process writes at scale.
**Smallest next step:** Read `DB_FILE` from `os.environ.get("DB_FILE", "notes.db")` so the path can be injected at deploy time without touching code.

---

## 4. Runbooks
**Would it hold up?** No — the README is three lines; there is no documented startup sequence, no description of failure modes, no instructions for inspecting or recovering a corrupt DB, and no mention of required environment.
**Biggest risk:** On-call engineer faces an incident with no playbook — time-to-restore is entirely dependent on reading the source under pressure.
**Smallest next step:** Add a `## Troubleshooting` section to the README with three entries: WAL mode failure, disk-full, and how to take a hot backup with `sqlite3 notes.db ".backup notes.db.bak"`.

---

## 5. Rollback
**Would it hold up?** No — there is no migration system, no schema versioning, and no documented procedure to roll back to a previous binary while keeping the DB intact.
**Biggest risk:** A schema-altering deploy (new column, renamed table) cannot be undone without manual SQL; running the old binary against the new schema silently produces wrong results.
**Smallest next step:** Add a `schema_version` table with one row and assert it on startup — forces an explicit version bump before any schema change and gives rollback scripts a target.

---

## Verdict

**NO-GO.** No auth, no health endpoint, hardcoded DB path, and zero runbook coverage make this unsafe for production this week.
