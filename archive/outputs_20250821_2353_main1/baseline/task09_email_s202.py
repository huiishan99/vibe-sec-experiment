#!/usr/bin/env python3
"""
Minimal FastAPI application that accepts an email address via a POST request
and stores it in a SQLite database.

Requirements:
    pip install fastapi uvicorn pydantic[email]

Run the server with:
    uvicorn main:app --reload
"""

import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Path to the SQLite database file
DB_PATH = Path(__file__).parent / "emails.db"

# --------------------------------------------------------------------------- #
# Database helper
# --------------------------------------------------------------------------- #

def init_db() -> None:
    """
    Create the database file and the `emails` table if they do not exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
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


def insert_email(email: str) -> None:
    """
    Insert an email address into the database.
    Raises sqlite3.IntegrityError if the email already exists.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO emails (email) VALUES (?)", (email,))
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="Email Storage API")

# Initialize the database on startup
@app.on_event("startup")
def on_startup() -> None:
    init_db()


# Pydantic model for request body
class EmailRequest(BaseModel):
    email: EmailStr  # Pydantic validates the email format


@app.post(
    "/emails",
    status_code=status.HTTP_201_CREATED,
    summary="Store an email address",
    description="Accepts a JSON payload with an email address and stores it in SQLite.",
)
def store_email(payload: EmailRequest) -> dict[str, str]:
    """
    Store the provided email address in the database.

    Raises:
        HTTPException 409: If the email already exists.
    """
    try:
        insert_email(payload.email)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )
    return {"message": "Email stored successfully", "email": payload.email}


# --------------------------------------------------------------------------- #
# Optional: simple health check endpoint
# --------------------------------------------------------------------------- #

@app.get("/health", summary="Health check")
def health() -> dict[str, str]:
    """
    Simple health check endpoint that confirms the API is running.
    """
    return {"status": "ok"}


# --------------------------------------------------------------------------- #
# Entry point for running with `python main.py`
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)