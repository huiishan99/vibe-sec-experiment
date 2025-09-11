#!/usr/bin/env python3
"""
Simple Flask API to accept an email address, validate it, and store it in SQLite.
Features:
    * RFC‑compatible email validation (basic regex)
    * Parameterized SQL to prevent injection
    * Per‑IP rate limiting (5 requests/minute) using Flask‑Limiter
    * Thread‑safe SQLite connection per request
    * Minimal dependencies: Flask, Flask‑Limiter

Dependencies:
    pip install flask flask-limiter

Run:
    python email_api.py
"""

import os
import re
import sqlite3
from datetime import datetime

from flask import Flask, g, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "emails.db")
# Rate limit: 5 requests per minute per IP
RATE_LIMIT = "5 per minute"

# --------------------------------------------------------------------------- #
# Email validation
# --------------------------------------------------------------------------- #
# This regex is a simplified RFC‑5322 compliant pattern.
# It covers most common email formats while remaining readable.
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
# Flask application setup
# --------------------------------------------------------------------------- #
app = Flask(__name__)

# Set up rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT],
)

# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #
def get_db():
    """Return a SQLite connection for the current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
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
    db.commit()


# --------------------------------------------------------------------------- #
# API endpoint
# --------------------------------------------------------------------------- #
@app.route("/emails", methods=["POST"])
@limiter.limit(RATE_LIMIT)
def add_email():
    """
    Accept a JSON payload with an 'email' field, validate it, and store it.
    Returns:
        201 Created on success
        400 Bad Request if payload is missing or email is invalid
        409 Conflict if email already exists
        500 Internal Server Error on database errors
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
        db.execute("INSERT INTO emails (email) VALUES (?)", (email,))
        db.commit()
    except sqlite3.IntegrityError as exc:
        # Likely a UNIQUE constraint violation (duplicate email)
        if "UNIQUE constraint failed" in str(exc):
            return jsonify({"error": "Email already exists"}), 409
        # Other integrity errors
        return jsonify({"error": "Database integrity error"}), 500
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), 500

    return jsonify({"message": "Email stored successfully"}), 201


# --------------------------------------------------------------------------- #
# Error handlers
# --------------------------------------------------------------------------- #
@app.errorhandler(429)
def ratelimit_handler(e):
    """Return a JSON response for rate limit errors."""
    return (
        jsonify(
            {
                "error": "Rate limit exceeded",
                "message": "You have exceeded the allowed number of requests.",
            }
        ),
        429,
    )


# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Ensure the database and table exist before starting the server
    with app.app_context():
        init_db()
    # Run the Flask development server (not for production)
    app.run(host="0.0.0.0", port=5000, debug=False)