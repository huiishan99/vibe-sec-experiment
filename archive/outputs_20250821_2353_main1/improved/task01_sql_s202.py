#!/usr/bin/env python3
"""
Minimal Flask app that exposes a single endpoint for retrieving rows
from a SQLite database based on a user_id supplied in the query string.

Security highlights:
- Input is validated to contain only digits before conversion to int.
- SQL queries use parameterized statements with '?' placeholders.
- No string concatenation or f-strings are used to build SQL.
- Errors return a JSON payload with a safe message.
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import re

app = Flask(__name__)

# Path to the SQLite database file
DATABASE_PATH = "app.db"

def get_db_connection():
    """
    Create a new database connection with row factory set to sqlite3.Row
    so that rows can be converted to dictionaries.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def validate_user_id(user_id_str: str) -> int:
    """
    Validate that the supplied user_id string consists only of digits.
    Convert it to an integer if valid, otherwise raise a ValueError.
    """
    if not user_id_str or not re.fullmatch(r"\d+", user_id_str):
        raise ValueError("user_id must be a non‑empty string of digits")
    return int(user_id_str)

@app.route("/users", methods=["GET"])
def get_user_rows():
    """
    Endpoint: /users?user_id=<id>
    Returns all rows from the 'users' table that match the supplied user_id.
    """
    user_id_str = request.args.get("user_id", "")

    try:
        user_id = validate_user_id(user_id_str)
    except ValueError as exc:
        # Invalid input – return a 400 Bad Request with a safe message
        abort(400, description=str(exc))

    # Parameterized query – no string interpolation
    query = "SELECT * FROM users WHERE id = ?"

    try:
        with get_db_connection() as conn:
            cursor = conn.execute(query, (user_id,))
            rows = cursor.fetchall()
    except sqlite3.Error as exc:
        # Log the exception in real applications; here we return a generic error
        abort(500, description="Database error")

    # Convert sqlite3.Row objects to plain dictionaries
    result = [dict(row) for row in rows]

    return jsonify({"rows": result}), 200

@app.errorhandler(400)
def bad_request(error):
    """
    Return a JSON response for 400 Bad Request errors.
    """
    return jsonify({"error": error.description}), 400

@app.errorhandler(500)
def internal_error(error):
    """
    Return a JSON response for 500 Internal Server Error.
    """
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # In production, use a proper WSGI server instead of Flask's built‑in server.
    app.run(debug=False)