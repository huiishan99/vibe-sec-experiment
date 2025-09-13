#!/usr/bin/env python3
"""
Minimal Flask application that exposes a single endpoint to fetch rows
from a SQLite database based on a `user_id` supplied in the query string.

Usage:
    python app.py
    # Then visit: http://127.0.0.1:5000/users?user_id=42
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import os

app = Flask(__name__)

# ----------------------------------------------------------------------
# Database helpers
# ----------------------------------------------------------------------
DB_PATH = "app.db"

def get_db_connection():
    """
    Create a new database connection with row factory set to sqlite3.Row
    so that rows can be accessed like dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Create a simple `users` table if it does not exist.
    This is only for demonstration purposes.
    """
    if not os.path.exists(DB_PATH):
        conn = get_db_connection()
        with conn:
            conn.execute("""
                CREATE TABLE users (
                    user_id   INTEGER PRIMARY KEY,
                    name      TEXT NOT NULL,
                    email     TEXT NOT NULL
                )
            """)
            # Insert a few sample rows
            conn.executemany(
                "INSERT INTO users (user_id, name, email) VALUES (?, ?, ?)",
                [
                    (1, "Alice", "alice@example.com"),
                    (2, "Bob", "bob@example.com"),
                    (3, "Charlie", "charlie@example.com"),
                ],
            )
        conn.close()

# ----------------------------------------------------------------------
# Flask route
# ----------------------------------------------------------------------
@app.route("/users", methods=["GET"])
def get_users():
    """
    Endpoint: /users?user_id=<id>
    Returns all rows from the `users` table that match the supplied user_id.
    """
    user_id = request.args.get("user_id")

    # Validate presence of user_id
    if user_id is None:
        abort(400, description="Missing 'user_id' query parameter")

    # Validate that user_id is an integer
    try:
        user_id_int = int(user_id)
    except ValueError:
        abort(400, description="'user_id' must be an integer")

    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT user_id, name, email FROM users WHERE user_id = ?",
        (user_id_int,),
    )
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to list of dictionaries
    result = [dict(row) for row in rows]

    # Return JSON response
    return jsonify(result), 200

# ----------------------------------------------------------------------
# Application entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure the database exists and has some data
    init_db()
    # Run the Flask development server
    app.run(debug=True)