#!/usr/bin/env python3
"""
Simple Flask API to accept an email address, validate it, and store it in SQLite.
Features:
    * RFC‑compatible email validation (simple regex)
    * Parameterised SQL to prevent injection
    * Rate limiting per IP (5 requests/minute)
    * Secure coding practices (input validation, error handling, secure headers)
"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    g,
    jsonify,
    request,
    Response,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DB_PATH = Path(__file__).parent / "emails.db"
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# Rate limiter: 5 requests per minute per IP
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["5 per minute"],
)

# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #

def get_db() -> sqlite3.Connection:
    """
    Return a SQLite connection stored in Flask's `g` context.
    Each request gets its own connection.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False,
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc: Exception | None = None) -> None:
    """
    Close the database connection after each request.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db() -> None:
    """
    Create the emails table if it does not exist.
    """
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP NOT NULL
        )
        """
    )
    db.commit()

# --------------------------------------------------------------------------- #
# Utility functions
# --------------------------------------------------------------------------- #

def is_valid_email(email: str) -> bool:
    """
    Validate the email address using a simple RFC‑compatible regex.
    """
    return bool(EMAIL_REGEX.fullmatch(email))

# --------------------------------------------------------------------------- #
# API endpoints
# --------------------------------------------------------------------------- #

@app.route("/email", methods=["POST"])
@limiter.limit("5 per minute")  # Override default if needed
def store_email() -> Response:
    """
    Accept a JSON payload with an 'email' field, validate it,
    and store it in the SQLite database.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    email = data.get("email")

    if not email or not isinstance(email, str):
        return jsonify({"error": "Missing or invalid 'email' field"}), 400

    email = email.strip()
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    db = get_db()
    try:
        db.execute(
            "INSERT INTO emails (email, created_at) VALUES (?, ?)",
            (email, datetime.utcnow()),
        )
        db.commit()
    except sqlite3.IntegrityError:
        # Email already exists
        return jsonify({"error": "Email already stored"}), 409
    except Exception:
        # Unexpected database error
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"message": "Email stored successfully"}), 201

# --------------------------------------------------------------------------- #
# Security headers
# --------------------------------------------------------------------------- #

@app.after_request
def set_secure_headers(response: Response) -> Response:
    """
    Add common security headers to every response.
    """
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    return response

# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Initialise database on first run
    init_db()
    # Run the Flask development server (do NOT use in production)
    app.run(host="0.0.0.0", port=5000, debug=False)