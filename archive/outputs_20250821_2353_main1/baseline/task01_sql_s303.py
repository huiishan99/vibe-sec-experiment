#!/usr/bin/env python3
"""
Minimal Flask app that exposes a single endpoint:

    GET /users?user_id=<id>

The endpoint reads the `user_id` query parameter, queries a SQLite
database for all rows that match that `user_id`, and returns the
results as JSON.

The database is created on first run (if it does not exist) and
populated with a few example rows.  The schema is intentionally
simple for demonstration purposes.

Author: Senior Python Engineer
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Dict, Any

from flask import Flask, request, jsonify, abort

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Path to the SQLite database file.  Using the current directory for
# simplicity; change this if you want a different location.
DB_PATH = Path(__file__).parent / "app.db"

# --------------------------------------------------------------------------- #
# Database helper functions
# --------------------------------------------------------------------------- #

def get_db_connection() -> sqlite3.Connection:
    """
    Return a new SQLite connection.  The connection is configured to
    return rows as dictionaries for easier JSON serialization.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """
    Create the database schema and insert a few demo rows if the
    database file does not already exist.
    """
    if DB_PATH.exists():
        return  # Database already exists; nothing to do.

    conn = get_db_connection()
    cursor = conn.cursor()

    # Simple schema: id (PK), user_id, name, email
    cursor.execute(
        """
        CREATE TABLE users (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name    TEXT NOT NULL,
            email   TEXT NOT NULL
        )
        """
    )

    # Insert some demo data
    demo_rows: List[tuple[int, str, str]] = [
        (1, "Alice", "alice@example.com"),
        (1, "Alicia", "alicia@example.com"),
        (2, "Bob", "bob@example.com"),
        (3, "Charlie", "charlie@example.com"),
    ]

    cursor.executemany(
        "INSERT INTO users (user_id, name, email) VALUES (?, ?, ?)",
        demo_rows,
    )

    conn.commit()
    conn.close()

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

@app.route("/users", methods=["GET"])
def get_users_by_user_id() -> Any:
    """
    Endpoint to fetch all rows for a given `user_id`.

    Query parameters:
        user_id (int, required) – The user ID to filter on.

    Returns:
        JSON array of matching rows.  Each row is represented as a
        dictionary with keys: id, user_id, name, email.
    """
    # Retrieve and validate the `user_id` query parameter.
    user_id_str = request.args.get("user_id")
    if not user_id_str:
        abort(400, description="Missing required query parameter: user_id")

    try:
        user_id = int(user_id_str)
    except ValueError:
        abort(400, description="user_id must be an integer")

    # Query the database safely using a parameterized query.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, name, email FROM users WHERE user_id = ?",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    # Convert sqlite3.Row objects to plain dictionaries.
    result: List[Dict[str, Any]] = [dict(row) for row in rows]

    return jsonify(result)

# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Ensure the database exists before starting the server.
    init_db()
    # Run the Flask development server.  In production, use a WSGI server.
    app.run(debug=True, host="0.0.0.0", port=5000)