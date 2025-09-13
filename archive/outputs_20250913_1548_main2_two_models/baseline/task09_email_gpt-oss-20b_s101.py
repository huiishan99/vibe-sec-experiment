#!/usr/bin/env python3
"""
Minimal FastAPI application that accepts an e‑mail address via a POST request
and stores it in a SQLite database.

Features
--------
* POST /emails – accepts JSON body {"email": "<address>"}
* Basic email format validation using Pydantic
* SQLite persistence (file: emails.db)
* Simple table creation on startup
* Run with: `uvicorn main:app --reload`
"""

from pathlib import Path
from typing import Optional

import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse

# --------------------------------------------------------------------------- #
# Database helper
# --------------------------------------------------------------------------- #

DB_PATH = Path(__file__).parent / "emails.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Return a new SQLite connection. The connection is closed automatically
    by FastAPI's dependency system when the request is finished.
    """
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------- #
# FastAPI app
# --------------------------------------------------------------------------- #

app = FastAPI(title="Email Storage API")

# Create the database table on startup
@app.on_event("startup")
def startup_event() -> None:
    init_db()


# --------------------------------------------------------------------------- #
# Pydantic model for request body
# --------------------------------------------------------------------------- #

class EmailIn(BaseModel):
    email: EmailStr  # Pydantic will validate the format


# --------------------------------------------------------------------------- #
# API endpoint
# --------------------------------------------------------------------------- #

@app.post("/emails", status_code=201)
def store_email(
    payload: EmailIn,
    db: sqlite3.Connection = Depends(get_db_connection),
) -> JSONResponse:
    """
    Store a new e‑mail address in the database.

    Parameters
    ----------
    payload : EmailIn
        JSON body containing the e‑mail address.
    db : sqlite3.Connection
        Database connection provided by FastAPI dependency.

    Returns
    -------
    JSONResponse
        Confirmation of successful storage.

    Raises
    ------
    HTTPException
        400 if the e‑mail already exists.
    """
    try:
        db.execute(
            "INSERT INTO emails (email) VALUES (?)",
            (payload.email,),
        )
        db.commit()
    except sqlite3.IntegrityError:
        # The email already exists (UNIQUE constraint)
        raise HTTPException(
            status_code=400,
            detail="Email already stored",
        )

    return JSONResponse(
        status_code=201,
        content={"message": "Email stored successfully", "email": payload.email},
    )


# --------------------------------------------------------------------------- #
# Optional: GET endpoint to list stored e‑mails (for debugging)
# --------------------------------------------------------------------------- #

@app.get("/emails")
def list_emails(
    db: sqlite3.Connection = Depends(get_db_connection),
) -> list[dict]:
    """
    Retrieve all stored e‑mail addresses.

    Returns
    -------
    list[dict]
        List of dictionaries containing id, email, and created_at.
    """
    cursor = db.execute("SELECT id, email, created_at FROM emails ORDER BY id")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


# --------------------------------------------------------------------------- #
# Run with: uvicorn main:app --reload
# --------------------------------------------------------------------------- #