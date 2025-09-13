#!/usr/bin/env python3
"""
Minimal FastAPI application that accepts an email address via POST /emails,
stores it in a SQLite database, validates the address with a simple RFC‑compatible
regex, and enforces per‑IP rate limiting.

Security notes:
- Uses parameterised SQL to avoid injection.
- Keeps the SQLite connection thread‑safe (`check_same_thread=False`).
- Rate limiting is implemented in memory; for production consider a distributed
  store (Redis, memcached, etc.).
"""

from __future__ import annotations

import re
import sqlite3
import time
from collections import defaultdict
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DB_PATH = "emails.db"
RATE_LIMIT = 5          # max requests
RATE_PERIOD = 60        # seconds

# --------------------------------------------------------------------------- #
# Email validation
# --------------------------------------------------------------------------- #

# A simple RFC‑5322 compatible regex (common subset).
EMAIL_REGEX = re.compile(
    r"(^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@"
    r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,}$)"
)


def is_valid_email(email: str) -> bool:
    """Return True if the email matches the RFC‑compatible regex."""
    return bool(EMAIL_REGEX.match(email))


# --------------------------------------------------------------------------- #
# Rate limiter
# --------------------------------------------------------------------------- #

class RateLimiter:
    """
    Very small in‑memory rate limiter.
    Stores timestamps per IP and prunes old entries on each request.
    """

    def __init__(self, limit: int, period: int):
        self.limit = limit
        self.period = period
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        timestamps = self.requests[ip]

        # Remove timestamps older than the period
        while timestamps and timestamps[0] <= now - self.period:
            timestamps.pop(0)

        if len(timestamps) >= self.limit:
            return False

        timestamps.append(now)
        return True


rate_limiter = RateLimiter(RATE_LIMIT, RATE_PERIOD)

# --------------------------------------------------------------------------- #
# Database helper
# --------------------------------------------------------------------------- #

def get_db_connection() -> sqlite3.Connection:
    """
    Return a thread‑safe SQLite connection.
    The connection is created lazily and reused.
    """
    if not hasattr(get_db_connection, "_conn"):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
        get_db_connection._conn = conn
    return get_db_connection._conn


def store_email(email: str) -> None:
    """Insert the email into the database using a parameterised query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO emails (email) VALUES (?)", (email,))
    conn.commit()


# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="Email Collector API")


class EmailRequest(BaseModel):
    email: str


@app.post("/emails", status_code=status.HTTP_201_CREATED)
async def add_email(request: Request, payload: EmailRequest):
    """
    Accepts a JSON payload with an 'email' field, validates it,
    enforces rate limiting per IP, and stores it in SQLite.
    """
    client_ip = request.client.host

    # Rate limiting
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
        )

    # Email validation
    if not is_valid_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address.",
        )

    # Store email
    try:
        store_email(payload.email)
    except sqlite3.IntegrityError:
        # Duplicate email
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        )
    except Exception as exc:
        # Unexpected database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        ) from exc

    return {"message": "Email stored successfully."}


# --------------------------------------------------------------------------- #
# Run with: uvicorn this_file:app --reload
# --------------------------------------------------------------------------- #