import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()
DB_PATH = Path("notes.db")


class NoteCreate(BaseModel):
    title: str
    body: str


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.post("/notes", status_code=201, response_model=Note)
def create_note(note: NoteCreate) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (note.title, note.body, now, now),
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()

    return {
        "id": note_id,
        "title": note.title,
        "body": note.body,
        "created_at": now,
        "updated_at": now,
    }


@app.get("/notes", response_model=list[Note])
def list_notes(q: Optional[str] = None) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()

    if q:
        cursor.execute(
            "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY created_at DESC",
            (f"%{q}%", f"%{q}%"),
        )
    else:
        cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="not found")

    return dict(row)


@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="not found")

    now = datetime.now(timezone.utc).isoformat()
    title = note.title if note.title is not None else row["title"]
    body = note.body if note.body is not None else row["body"]

    cursor.execute(
        "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
        (title, body, now, note_id),
    )
    conn.commit()
    conn.close()

    return {
        "id": note_id,
        "title": title,
        "body": body,
        "created_at": row["created_at"],
        "updated_at": now,
    }


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="not found")

    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
