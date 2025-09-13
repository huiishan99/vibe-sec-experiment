#!/usr/bin/env python3
"""
Flask endpoint that safely retrieves rows from a SQLite database
based on a user_id supplied in the query string.

Key security measures:
- Input validation: only accept numeric user_id values.
- Parameterized SQL: use '?' placeholders, never string interpolation.
- sqlite3.Row: return rows as dictionaries for easy JSON serialization.
- Proper error handling: return 400 for bad input, 500 for DB errors.
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import re

app = Flask(__name__)

# Path to the SQLite database file
DB_PATH = "database.db"

def get_db_connection():
    """
    Create a new database connection.
    Using row_factory to return rows as dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/users", methods=["GET"])
def get_user_rows():
    """
    GET /users?user_id=<digits>
    Returns all rows for the specified user_id.
    """
    # Retrieve the raw query string value
    raw_user_id = request.args.get("user_id", "")

    # Validate that the user_id consists only of digits
    if not raw_user_id.isdigit():
        # Reject non‑numeric input with a 400 Bad Request
        return jsonify({"error": "Invalid user_id: must be numeric"}), 400

    # Safe conversion to integer
    user_id = int(raw_user_id)

    # Parameterized query – no string interpolation
    sql = "SELECT * FROM users WHERE user_id = ?"

    try:
        conn = get_db_connection()
        cur = conn.execute(sql, (user_id,))
        rows = cur.fetchall()
        # Convert sqlite3.Row objects to plain dicts
        result = [dict(row) for row in rows]
        return jsonify(result), 200
    except sqlite3.Error as e:
        # Log the error in a real application; here we return a generic message
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    # Run the Flask development server
    app.run(debug=True)