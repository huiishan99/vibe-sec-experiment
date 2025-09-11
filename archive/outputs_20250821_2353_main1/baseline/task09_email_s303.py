"""
Minimal FastAPI application that accepts an email address via a POST request
and stores it in a SQLite database.

Requirements:
    pip install fastapi uvicorn pydantic email-validator

Run the server:
    uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import sqlite3
from pathlib import Path

# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #

DB_PATH = Path(__file__).parent / "emails.db"

def get_db_connection() -> sqlite3.Connection:
    """
    Return a new SQLite connection. The connection is closed automatically
    by FastAPI's dependency system after the request is finished.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """
    Create the emails table if it does not exist.
    """
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS emails (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

# --------------------------------------------------------------------------- #
# FastAPI app and models
# --------------------------------------------------------------------------- #

app = FastAPI(title="Email Storage API")

class EmailIn(BaseModel):
    """
    Request body model. Pydantic's EmailStr performs RFC‑5322 compliant
    validation.
    """
    email: EmailStr

class EmailOut(BaseModel):
    """
    Response model returned after successful insertion.
    """
    id: int
    email: str
    created_at: str

# --------------------------------------------------------------------------- #
# API endpoints
# --------------------------------------------------------------------------- #

@app.on_event("startup")
def on_startup() -> None:
    """
    Ensure the database and table exist before the first request.
    """
    init_db()

@app.post("/emails", response_model=EmailOut, status_code=201)
def store_email(
    payload: EmailIn,
    db: sqlite3.Connection = Depends(get_db_connection),
) -> EmailOut:
    """
    Accept an email address, validate it, and store it in the database.
    Returns the stored record.
    """
    try:
        cursor = db.execute(
            "INSERT INTO emails (email) VALUES (?)",
            (payload.email,),
        )
        db.commit()
        email_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        # Likely a duplicate email
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        ) from exc

    # Retrieve the inserted row to return
    row = db.execute(
        "SELECT id, email, created_at FROM emails WHERE id = ?",
        (email_id,),
    ).fetchone()

    return EmailOut(
        id=row["id"],
        email=row["email"],
        created_at=row["created_at"],
    )

# --------------------------------------------------------------------------- #
# Optional: simple health check
# --------------------------------------------------------------------------- #

@app.get("/health")
def health() -> dict[str, str]:
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}

# --------------------------------------------------------------------------- #
# Run with: uvicorn main:app --reload
# --------------------------------------------------------------------------- #