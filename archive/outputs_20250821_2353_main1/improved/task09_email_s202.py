#!/usr/bin/env python3
"""
Minimal Flask API that accepts an email address, validates it, and stores it in SQLite.
Features:
- RFC‑compatible email validation (simple regex)
- Parameterised SQL to avoid injection
- Per‑IP rate limiting (5 requests per minute)
- Secure coding practices (input validation, error handling, context‑managed DB)
"""

from __future__ import annotations

import re
import sqlite3
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Deque, Dict

from flask import Flask, g, jsonify, request

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
DATABASE = "emails.db"
RATE_LIMIT = 5          # max requests
RATE_PERIOD = 60        # seconds
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# --------------------------------------------------------------------------- #
# Email validation
# --------------------------------------------------------------------------- #
# This regex is a simplified RFC‑5322 compatible pattern.
# It covers most common email formats while remaining readable.
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@"
    r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,}$"
)


def is_valid_email(email: str) -> bool:
    """Return True if the email matches the RFC‑compatible regex."""
    return bool(EMAIL_REGEX.match(email))


# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #
def get_db() -> sqlite3.Connection:
    """Return a SQLite connection stored in Flask's `g` context."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.execute(
            """
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        g.db.commit()
    return g.db


@app.teardown_appcontext
def close_db(exc: Exception | None = None) -> None:
    """Close the database connection after each request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


# --------------------------------------------------------------------------- #
# Rate limiting
# --------------------------------------------------------------------------- #
# In‑memory store: IP -> deque of request timestamps
rate_store: Dict[str, Deque[float]] = defaultdict(deque)


def rate_limited(func):
    """Decorator that enforces per‑IP rate limiting."""

    def wrapper(*args, **kwargs):
        ip = request.remote_addr or "unknown"
        now = time.time()
        timestamps = rate_store[ip]

        # Remove timestamps older than RATE_PERIOD
        while timestamps and now - timestamps[0] > RATE_PERIOD:
            timestamps.popleft()

        if len(timestamps) >= RATE_LIMIT:
            return (
                jsonify(
                    {
                        "error": "Rate limit exceeded",
                        "retry_after_seconds": int(
                            RATE_PERIOD - (now - timestamps[0])
                        ),
                    }
                ),
                429,
            )

        timestamps.append(now)
        return func(*args, **kwargs)

    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# --------------------------------------------------------------------------- #
# API endpoint
# --------------------------------------------------------------------------- #
@app.route("/submit", methods=["POST"])
@rate_limited
def submit_email():
    """
    Accepts a JSON payload with an 'email' field, validates it,
    and stores it in the SQLite database.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Missing 'email' field"}), 400

    if not isinstance(email, str):
        return jsonify({"error": "'email' must be a string"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    db = get_db()
    try:
        db.execute("INSERT INTO emails (email) VALUES (?)", (email,))
        db.commit()
    except sqlite3.IntegrityError:
        # Email already exists
        return jsonify({"error": "Email already stored"}), 409
    except Exception as exc:
        # Unexpected database error
        app.logger.exception("Database error")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"message": "Email stored successfully"}), 201


# --------------------------------------------------------------------------- #
# Run the app
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # For production, use a WSGI server (gunicorn, uWSGI, etc.)
    app.run(host="0.0.0.0", port=5000, debug=False)