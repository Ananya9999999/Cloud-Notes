"""
Cloud Notes App — FastAPI backend
Simple CRUD API for notes, backed by SQLite.
Also serves the static frontend so the whole app runs as ONE process
on ONE port — makes EC2 deployment much simpler.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "notes.db"

app = FastAPI(title="Cloud Notes App")


# ---------- Database setup ----------

def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@app.on_event("startup")
def on_startup():
    init_db()


# ---------- Schemas ----------

class NoteCreate(BaseModel):
    title: str
    content: str = ""


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


# ---------- API routes ----------

@app.get("/api/notes")
def list_notes():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM notes ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


@app.post("/api/notes", status_code=201)
def create_note(note: NoteCreate):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (note.title, note.content, now, now),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return dict(row)


@app.get("/api/notes/{note_id}")
def get_note(note_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return dict(row)


@app.put("/api/notes/{note_id}")
def update_note(note_id: int, note: NoteUpdate):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Note not found")

        title = note.title if note.title is not None else existing["title"]
        content = note.content if note.content is not None else existing["content"]
        now = datetime.utcnow().isoformat()

        conn.execute(
            "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
            (title, content, now, note_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return dict(row)


@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Note not found")
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
    return None


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------- Serve frontend ----------
# Mounted last so it doesn't shadow the /api routes above.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
