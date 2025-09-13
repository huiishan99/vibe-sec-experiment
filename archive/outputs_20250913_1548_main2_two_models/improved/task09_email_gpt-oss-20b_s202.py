#!/usr/bin/env python3
"""
Minimal Flask API to accept an email address, validate it, and store it in SQLite.
Features:
    * RFC‑compatible email validation (simple regex)
    * Parameterised SQL to prevent injection
    * Per‑IP rate limiting (default: 5 requests per minute)
    * Secure coding practices (input validation, error handling, unique constraint)
"""

from __future__ import annotations

import re
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, request, g

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# SQLite database file (created in the same directory as this script)
DB_PATH = Path(__file__).parent / "emails.db"

# Rate‑limiting configuration
RATE_LIMIT = 5          # max requests
RATE_PERIOD = 60        # per seconds

# Email validation regex (RFC‑5322 compliant for most common cases)
EMAIL_REGEX = re.compile(
    r"(^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$)"
)

# --------------------------------------------------------------------------- #
# Helper classes
# --------------------------------------------------------------------------- #

class RateLimiter:
    """
    Simple in‑memory rate limiter keyed by client IP.
    Stores timestamps of recent requests and enforces a limit per period.
    """
    def __init__(self, limit: int, period: int) -> None:
        self.limit = limit
        self.period = period
        self.requests: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def is_allowed(self, ip: str) -> bool:
        """Return True if the IP is allowed to make a request."""
        now = time.time()
        window_start = now - self.period

        with self.lock:
            timestamps = self.requests.get(ip, [])

            # Remove timestamps outside the window
            timestamps = [ts for ts in timestamps if ts > window_start]
            if len(timestamps) >= self.limit:
                # Too many requests
                self.requests[ip] = timestamps
                return False

            # Record this request
            timestamps.append(now)
            self.requests[ip] = timestamps
            return True

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)
rate_limiter = RateLimiter(RATE_LIMIT, RATE_PERIOD)

# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #

def get_db() -> sqlite3.Connection:
    """
    Return a SQLite connection for the current request context.
    The connection is stored in Flask's `g` object to be reused.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            isolation_level=None,  # autocommit mode
        )
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exc: Exception | None = None) -> None:
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db() -> None:
    """Create the emails table if it does not exist."""
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

# --------------------------------------------------------------------------- #
# Utility functions
# --------------------------------------------------------------------------- #

def is_valid_email(email: str) -> bool:
    """Return True if the email matches the RFC‑compatible regex."""
    return bool(EMAIL_REGEX.match(email))

# --------------------------------------------------------------------------- #
# API endpoint
# --------------------------------------------------------------------------- #

@app.route("/submit", methods=["POST"])
def submit_email() -> tuple[dict, int]:
    """
    Accept a JSON payload with an 'email' field, validate it,
    enforce rate limiting, and store it in the database.
    """
    client_ip = request.remote_addr or "unknown"

    # Rate limiting
    if not rate_limiter.is_allowed(client_ip):
        return jsonify({"error": "Too many requests"}), 429

    # Parse JSON body
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    email = data.get("email")
    if not email or not isinstance(email, str):
        return jsonify({"error": "Missing or invalid 'email' field"}), 400

    email = email.strip()
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    # Store in database
    db = get_db()
    try:
        db.execute("INSERT INTO emails (email) VALUES (?)", (email,))
    except sqlite3.IntegrityError:
        # Email already exists
        return jsonify({"message": "Email already stored"}), 200
    except Exception as exc:
        # Unexpected database error
        app.logger.exception("Database error while inserting email")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"message": "Email stored successfully"}), 201

# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Ensure the database is initialized before starting the server
    init_db()
    # Run the Flask development server (not for production)
    app.run(host="0.0.0.0", port=5000, debug=False)