# main.py
"""
A minimal FastAPI application that accepts an email address via a POST request
and stores it in a SQLite database.

Requirements:
    pip install fastapi uvicorn email-validator

Run the server with:
    uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import sqlite3
from contextlib import contextmanager
import os

# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #

DB_PATH = "emails.db"

def init_db() -> None:
    """Create the emails table if it does not exist."""
    with sqlite3.connect(DB_PATH) as conn:
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

@contextmanager
def get_db_connection():
    """Context manager that yields a SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

# --------------------------------------------------------------------------- #
# FastAPI app
# --------------------------------------------------------------------------- #

app = FastAPI(title="Email Storage API")

# Initialise the database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# --------------------------------------------------------------------------- #
# Pydantic models
# --------------------------------------------------------------------------- #

class EmailIn(BaseModel):
    """Request body for storing an email."""
    email: EmailStr  # Pydantic + email-validator will validate format

class EmailOut(BaseModel):
    """Response body after storing an email."""
    id: int
    email: EmailStr
    created_at: str

# --------------------------------------------------------------------------- #
# API endpoints
# --------------------------------------------------------------------------- #

@app.post("/emails", response_model=EmailOut, status_code=201)
def create_email(email_in: EmailIn, db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Store a new email address in the database.

    Raises:
        HTTPException 409: If the email already exists.
    """
    try:
        cursor = db.execute(
            "INSERT INTO emails (email) VALUES (?)",
            (email_in.email,),
        )
        db.commit()
        email_id = cursor.lastrowid
        cursor = db.execute(
            "SELECT id, email, created_at FROM emails WHERE id = ?",
            (email_id,),
        )
        row = cursor.fetchone()
        return EmailOut(id=row[0], email=row[1], created_at=row[2])
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")

@app.get("/emails", response_model=list[EmailOut])
def list_emails(db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Retrieve all stored email addresses.
    """
    cursor = db.execute("SELECT id, email, created_at FROM emails ORDER BY created_at DESC")
    rows = cursor.fetchall()
    return [EmailOut(id=r[0], email=r[1], created_at=r[2]) for r in rows]

# --------------------------------------------------------------------------- #
# Run with: uvicorn main:app --reload
# --------------------------------------------------------------------------- #