#!/usr/bin/env python3
"""
Minimal Flask app that exposes a single endpoint:
    GET /users?user_id=<id>

The endpoint reads the `user_id` query parameter, queries a SQLite
database for all rows that match that user_id, and returns the results
as JSON.

Requirements:
    pip install flask
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import os

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
# Path to the SQLite database file.  Adjust as needed.
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def get_db_connection():
    """
    Create a new database connection.
    The connection is configured to return rows as dictionaries
    for easier JSON serialization.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query_user_rows(user_id: int):
    """
    Query the database for all rows where `user_id` matches the
    supplied integer.  Returns a list of dictionaries.
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        rows = cursor.fetchall()
        # Convert sqlite3.Row objects to plain dicts
        return [dict(row) for row in rows]
    finally:
        conn.close()

# ----------------------------------------------------------------------
# Flask application
# ----------------------------------------------------------------------
app = Flask(__name__)

@app.route("/users", methods=["GET"])
def get_users():
    """
    Endpoint: GET /users?user_id=<id>

    Parameters:
        user_id (int) – required query parameter

    Returns:
        JSON array of rows matching the user_id.
    """
    # Retrieve the user_id from the query string
    user_id_str = request.args.get("user_id")
    if not user_id_str:
        # Missing parameter – return 400 Bad Request
        abort(400, description="Missing required query parameter: user_id")

    # Validate that user_id is an integer
    try:
        user_id = int(user_id_str)
    except ValueError:
        abort(400, description="user_id must be an integer")

    # Query the database
    rows = query_user_rows(user_id)

    # Return the results as JSON
    return jsonify(rows)

# ----------------------------------------------------------------------
# Run the application
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure the database file exists before starting
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found: {DB_PATH}")

    # Run the Flask development server
    app.run(debug=True)