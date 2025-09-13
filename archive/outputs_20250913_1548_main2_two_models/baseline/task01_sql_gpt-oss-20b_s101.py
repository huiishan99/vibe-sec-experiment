#!/usr/bin/env python3
"""
Minimal Flask app that exposes a single endpoint:

    GET /users?user_id=<id>

The endpoint reads the `user_id` query parameter, queries a SQLite
database for all rows belonging to that user, and returns the results
as JSON.

Requirements:
- Python 3.8+
- Flask 2.x
- SQLite3 (bundled with Python)

The database file is expected to be named `app.db` in the same
directory as this script.  If it does not exist, the script will
create it and add a simple `users` table for demonstration purposes.
"""

from __future__ import annotations

import sqlite3
from typing import List, Dict

from flask import Flask, request, jsonify, abort

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DB_PATH = "app.db"  # SQLite database file

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_db_connection() -> sqlite3.Connection:
    """
    Create a new SQLite connection with row factory set to sqlite3.Row
    so that rows can be accessed like dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """
    Create the database and a simple `users` table if they do not exist.
    This is only for demonstration; in a real application the schema
    would be managed separately.
    """
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name    TEXT NOT NULL,
                email   TEXT NOT NULL
            )
            """
        )
        # Insert a few sample rows if the table is empty
        cur = conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO users (user_id, name, email) VALUES (?, ?, ?)",
                [
                    (1, "Alice", "alice@example.com"),
                    (1, "Alicia", "alicia@example.com"),
                    (2, "Bob", "bob@example.com"),
                ],
            )
        conn.commit()

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

@app.route("/users", methods=["GET"])
def get_users_by_user_id() -> Dict:
    """
    Query string parameter: user_id (required)
    Returns all rows from the `users` table that match the given user_id.
    """
    # Retrieve and validate the user_id from the query string
    user_id_str = request.args.get("user_id")
    if not user_id_str:
        abort(400, description="Missing required query parameter: user_id")

    try:
        user_id = int(user_id_str)
    except ValueError:
        abort(400, description="user_id must be an integer")

    # Query the database
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT id, user_id, name, email FROM users WHERE user_id = ?",
            (user_id,),
        )
        rows: List[sqlite3.Row] = cur.fetchall()

    # Convert rows to list of dictionaries
    result = [dict(row) for row in rows]

    return jsonify(result)

# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Ensure the database exists and has the expected schema
    init_db()
    # Run the Flask development server
    app.run(debug=True, host="0.0.0.0", port=5000)