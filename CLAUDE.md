# Stack
- Python 3.12 — use only stdlib; no third-party packages
- Node v20.11.0 (available but not primary)
- No package manager or build step; scripts run directly with `python3`

# Conventions
- One script per module — keep all logic in a single `.py` file
- snake_case for all Python identifiers
- Timestamps as `"%Y-%m-%d %H:%M:%S UTC"` using `datetime.now(timezone.utc)`
- Persistence via a local JSON file (e.g. `tasks.json`) in the cwd
- Print user-facing errors to `sys.stderr`; normal output to `stdout`
- Exit codes: 0 = success, 1 = user error (bad args/unknown id), 2 = internal error (corrupt file/disk)
- No docstrings on functions; one-line comments only when the why is non-obvious

# Commands
- Run: `python3 <script>.py <command> [args]`
- Lint: `python3 -m py_compile <script>.py` (syntax check only; no external linter)
- Type-check: `python3 -m mypy <script>.py --strict` (if mypy is available)
- Test: `python3 -m pytest` (if tests exist; no test runner is pre-installed)

# Do-not
- Never add third-party dependencies (pip install) without explicit user approval
- Never split logic across multiple files unless the user asks
- Never use `exit()` — always use `sys.exit(code)` with the correct exit code
- Never catch bare `Exception`; catch the narrowest type that makes sense
- Never mutate `sys.argv` or use `argparse` — the project uses manual `sys.argv` parsing

# Glossary
- **task** — a dict with keys `id` (int), `status` ("pending"|"done"), `created_at` (str), `text` (str)
- **TASKS_FILE** — the constant naming the JSON persistence file (`tasks.json`)
- **cmd_*** — naming convention for top-level command handler functions
