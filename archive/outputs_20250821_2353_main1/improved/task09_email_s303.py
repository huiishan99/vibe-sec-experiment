#!/usr/bin/env python3
"""
Simple Flask API to accept an email address, validate it, and store it in SQLite.
Features:
- RFC‑compatible email validation (simple regex)
- Parameterised SQL to prevent injection
- Per‑IP rate limiting (max 5 requests per minute)
- Secure coding practices (input validation, error handling, minimal dependencies)
"""

from __future__ import annotations

import re
import sqlite3
import time
import threading
from datetime import datetime
from typing import Dict, List

from flask import Flask, request, jsonify, make_response

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DB_PATH = "emails.db"
RATE_LIMIT_MAX = 5          # max requests
RATE_LIMIT_WINDOW = 60      # seconds

# Simple RFC‑compatible email regex (not exhaustive but sufficient for most cases)
EMAIL_REGEX = re.compile(
    r"(^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$)"
)

# --------------------------------------------------------------------------- #
# Rate‑limiting infrastructure
# --------------------------------------------------------------------------- #

# Mapping: IP -> list of request timestamps (float)
rate_limit: Dict[str, List[float]] = {}
rate_limit_lock = threading.Lock()


def is_allowed(ip: str) -> bool:
    """
    Check if the given IP is allowed to make a request.
    Updates the timestamp list for the IP.
    """
    now = time.time()
    with rate_limit_lock:
        timestamps = rate_limit.setdefault(ip, [])
        # Remove timestamps older than the window
        while timestamps and timestamps[0] <= now - RATE_LIMIT_WINDOW:
            timestamps.pop(0)
        if len(timestamps) >= RATE_LIMIT_MAX:
            return False
        timestamps.append(now)
        return True


# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #

def init_db() -> None:
    """Create the emails table if it does not exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def store_email(email: str) -> None:
    """Insert the validated email into the database."""
    created_at = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO emails (email, created_at) VALUES (?, ?)",
            (email, created_at),
        )
        conn.commit()


# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)


@app.after_request
def set_security_headers(response):
    """Add a few basic security headers."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    return response


@app.route("/submit_email", methods=["POST"])
def submit_email():
    """Endpoint to accept an email address."""
    client_ip = request.remote_addr or "unknown"

    # Rate limiting
    if not is_allowed(client_ip):
        return make_response(jsonify({"error": "Too many requests"}), 429)

    # Parse JSON body
    try:
        data = request.get_json(force=True)
    except Exception:
        return make_response(jsonify({"error": "Invalid JSON"}), 400)

    if not data or "email" not in data:
        return make_response(jsonify({"error": "Missing 'email' field"}), 400)

    email = data["email"].strip()
    if not EMAIL_REGEX.match(email):
        return make_response(jsonify({"error": "Invalid email format"}), 400)

    # Store in database
    try:
        store_email(email)
    except Exception as exc:
        # Log exception in real application
        return make_response(jsonify({"error": "Server error"}), 500)

    return jsonify({"status": "success", "email": email}), 200


@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"}), 200


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    init_db()
    # For production use a proper WSGI server (gunicorn, uWSGI, etc.)
    app.run(host="0.0.0.0", port=5000, threaded=True)