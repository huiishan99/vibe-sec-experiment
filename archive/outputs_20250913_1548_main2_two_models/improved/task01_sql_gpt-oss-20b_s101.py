#!/usr/bin/env python3
"""
Minimal Flask app that exposes a single endpoint for retrieving rows
from a SQLite database based on a user_id supplied in the query string.

Security notes:
- Input is validated to contain only digits before conversion to int.
- SQL is executed with parameterized queries using '?' placeholders.
- No string concatenation or f-strings are used to build the SQL.
- Errors are caught and a generic 400 response is returned for invalid input.
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import os

app = Flask(__name__)

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

def get_db_connection():
    """
    Create a new database connection. The connection is closed automatically
    when the context manager exits.
    """
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dictionaries for easier JSON serialization
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/users", methods=["GET"])
def get_user_rows():
    """
    Endpoint: /users?user_id=<digits>
    Returns all rows from the 'users' table that match the given user_id.
    """
    # Retrieve the raw query string value
    raw_user_id = request.args.get("user_id", "")

    # Reject non‑digit input
    if not raw_user_id.isdigit():
        # 400 Bad Request with a safe error message
        abort(400, description="Invalid user_id. Must be a positive integer.")

    # Safe conversion to int
    user_id = int(raw_user_id)

    # Parameterized SQL query
    sql = "SELECT * FROM users WHERE id = ?"

    try:
        with get_db_connection() as conn:
            cursor = conn.execute(sql, (user_id,))
            rows = cursor.fetchall()
    except sqlite3.Error as e:
        # Log the error in a real application; here we return a generic message
        abort(400, description="Database error.")

    # Convert rows to list of dictionaries
    result = [dict(row) for row in rows]

    return jsonify(result), 200

# Custom error handler for 400 responses to return JSON
@app.errorhandler(400)
def bad_request(error):
    response = jsonify({"error": error.description or "Bad Request"})
    response.status_code = 400
    return response

if __name__ == "__main__":
    # Ensure the database file exists; create a simple table for demo purposes
    if not os.path.exists(DB_PATH):
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            """)
            conn.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')")
            conn.execute("INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com')")
            conn.commit()

    # Run the Flask development server
    app.run(debug=True)