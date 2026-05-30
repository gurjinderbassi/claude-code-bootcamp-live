# Bug Fix Notes — module-04/winner/main.py

## HIGH

### 1. Connection leak (all routes)
`get_db()` returns a bare `sqlite3.Connection`. Using it as `with get_db() as conn:` only manages the transaction (commit/rollback via `sqlite3.Connection.__enter__/__exit__`) — it never calls `conn.close()`. Every request leaks a file descriptor.

**Fix:** Convert `get_db()` to a `@contextmanager` that closes the connection in a `finally` block.

```python
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
```

---

## MEDIUM

### 2. Crash on concurrent delete during update (line 127)
In `update_note`, the row existence is checked at line 115, but a concurrent `DELETE` can remove the row before the re-fetch at line 126. `updated` will be `None`, and `row_to_dict(None)` raises `AttributeError` → unhandled 500 instead of a clean 404.

**Fix:** Guard the return value:
```python
if updated is None:
    raise HTTPException(status_code=404, detail="not found")
return row_to_dict(updated)
```

### 3. LIKE wildcard injection (line 93)
`f"%{q}%"` passes the raw `q` string into a LIKE pattern without escaping `%` or `_`. A search for `50%` or `note_1` expands wildcards rather than matching literally.

**Fix:** Escape special characters before building the pattern:
```python
escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
pattern = f"%{escaped}%"
# and add ESCAPE '\\' to the LIKE clause
```

---

## LOW

### 4. Silent WAL pragma failure (line 15)
`PRAGMA journal_mode=WAL` returns the actual mode that was set. The return value is discarded, so if WAL is unavailable (e.g., network filesystem) it silently falls back with no warning.

**Fix:** Check the result:
```python
result = conn.execute("PRAGMA journal_mode=WAL").fetchone()[0]
if result != "wal":
    raise RuntimeError(f"WAL mode unavailable, got: {result}")
```

### 5. No-op PATCH still mutates `updated_at` (lines 119–125)
A `PATCH /notes/{id}` with body `{}` sets `updated_at` to now even though no fields changed, misleading clients that use `updated_at` for cache invalidation or sync.

**Fix:** Short-circuit when both fields are absent:
```python
if payload.title is None and payload.body is None:
    return row_to_dict(row)
```

### 6. No input length limits on `title` / `body`
`NoteCreate` and `NoteUpdate` accept arbitrarily large strings, allowing oversized payloads to be stored without complaint.

**Fix:** Add `max_length` constraints:
```python
from pydantic import BaseModel, Field, field_validator

class NoteCreate(BaseModel):
    title: str = Field(max_length=255)
    body: str = Field(default="", max_length=100_000)
```
