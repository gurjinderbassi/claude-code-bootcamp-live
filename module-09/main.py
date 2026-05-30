import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

DB_FILE = "notes.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    result = conn.execute("PRAGMA journal_mode=WAL").fetchone()[0]
    if result != "wal":
        raise RuntimeError(f"WAL mode unavailable, got: {result}")
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                body       TEXT    NOT NULL DEFAULT '',
                created_at TEXT    NOT NULL,
                updated_at TEXT    NOT NULL
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


# ---------- schemas ----------

class NoteCreate(BaseModel):
    title: str = Field(max_length=255)
    body: str = Field(default="", max_length=100_000)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    body: Optional[str] = Field(default=None, max_length=100_000)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("title must not be blank")
        return v


# ---------- routes ----------

@app.post("/notes", status_code=201)
def create_note(payload: NoteCreate) -> dict:
    now = utcnow()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (payload.title, payload.body, now, now),
        )
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


@app.get("/notes")
def list_notes(q: Optional[str] = Query(default=None)) -> list[dict]:
    with get_db() as conn:
        if q:
            escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            pattern = f"%{escaped}%"
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ESCAPE '\\' ORDER BY id",
                (pattern, pattern),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM notes ORDER BY id").fetchall()
    return [row_to_dict(r) for r in rows]


@app.get("/notes/{note_id}")
def get_note(note_id: int) -> dict:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    return row_to_dict(row)


@app.patch("/notes/{note_id}")
def update_note(note_id: int, payload: NoteUpdate) -> dict:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="not found")
        if payload.title is None and payload.body is None:
            return row_to_dict(row)
        note = row_to_dict(row)
        new_title = payload.title if payload.title is not None else note["title"]
        new_body = payload.body if payload.body is not None else note["body"]
        now = utcnow()
        conn.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
            (new_title, new_body, now, note_id),
        )
        updated = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if updated is None:
            raise HTTPException(status_code=404, detail="not found")
    return row_to_dict(updated)


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    with get_db() as conn:
        row = conn.execute("SELECT id FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="not found")
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
