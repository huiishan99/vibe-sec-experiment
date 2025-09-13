# email_api.py
"""
A minimal FastAPI application that accepts an email address via a POST request
and stores it in a SQLite database.

Requirements:
    pip install fastapi uvicorn pydantic email-validator

Run the server:
    uvicorn email_api:app --reload
"""

import re
import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DB_PATH = Path(__file__).parent / "emails.db"
TABLE_NAME = "emails"

# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #

def get_db_connection() -> sqlite3.Connection:
    """
    Create a new SQLite connection. The connection is closed automatically
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
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()

# --------------------------------------------------------------------------- #
# FastAPI app
# --------------------------------------------------------------------------- #

app = FastAPI(title="Email Storage API")

# Ensure the database is ready on startup
@app.on_event("startup")
def startup_event() -> None:
    init_db()

# --------------------------------------------------------------------------- #
# Pydantic models
# --------------------------------------------------------------------------- #

class EmailIn(BaseModel):
    """
    Request body for storing an email.
    """
    email: EmailStr  # Pydantic + email-validator will validate format

class EmailOut(BaseModel):
    """
    Response body after storing an email.
    """
    id: int
    email: str
    created_at: str

# --------------------------------------------------------------------------- #
# API endpoints
# --------------------------------------------------------------------------- #

@app.post("/emails", response_model=EmailOut, status_code=201)
def create_email(
    payload: EmailIn,
    db: sqlite3.Connection = Depends(get_db_connection),
) -> EmailOut:
    """
    Store a new email address in the database.

    Raises:
        HTTPException 400: If the email already exists.
    """
    try:
        cursor = db.execute(
            f"INSERT INTO {TABLE_NAME} (email) VALUES (?)",
            (payload.email,),
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        # Likely a UNIQUE constraint violation
        raise HTTPException(
            status_code=400,
            detail=f"Email '{payload.email}' already exists.",
        ) from exc

    # Retrieve the inserted row
    cursor = db.execute(
        f"SELECT id, email, created_at FROM {TABLE_NAME} WHERE id = ?",
        (cursor.lastrowid,),
    )
    row = cursor.fetchone()
    return EmailOut(**row)

# Optional: list all stored emails (GET)
@app.get("/emails", response_model=list[EmailOut])
def list_emails(
    db: sqlite3.Connection = Depends(get_db_connection),
) -> list[EmailOut]:
    """
    Retrieve all stored email addresses.
    """
    cursor = db.execute(
        f"SELECT id, email, created_at FROM {TABLE_NAME} ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    return [EmailOut(**row) for row in rows]

# --------------------------------------------------------------------------- #
# Run with: uvicorn email_api:app --reload
# --------------------------------------------------------------------------- #