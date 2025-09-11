#!/usr/bin/env python3
"""
Minimal Flask app exposing a single endpoint that retrieves user rows from a SQLite database.
The endpoint expects a numeric user_id in the query string, validates it, and uses a
parameterized SQL query to prevent injection attacks.
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import os

app = Flask(__name__)

# Path to the SQLite database file
DB_PATH = os.getenv("DATABASE_URL", "app.db")

def get_db_connection():
    """
    Create a new database connection with row factory set to sqlite3.Row
    so that query results can be accessed as dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/user", methods=["GET"])
def get_user():
    """
    Retrieve user information for the given user_id.
    Query string parameter: user_id (must be digits only).
    Returns JSON array of matching rows or 400 on invalid input.
    """
    user_id_str = request.args.get("user_id", "")

    # Validate that user_id consists only of digits
    if not user_id_str.isdigit():
        abort(400, description="Invalid user_id: must be a positive integer")

    user_id = int(user_id_str)

    # Use a parameterized query with ? placeholder to avoid SQL injection
    query = "SELECT id, name, email FROM users WHERE id = ?"

    try:
        conn = get_db_connection()
        cursor = conn.execute(query, (user_id,))
        rows = cursor.fetchall()
    except sqlite3.Error:
        # Log the error in real applications; here we return a generic message
        abort(500, description="Database error")
    finally:
        conn.close()

    # Convert sqlite3.Row objects to plain dictionaries
    result = [dict(row) for row in rows]

    return jsonify(result), 200

@app.errorhandler(400)
def bad_request(error):
    """Return a JSON response for 400 Bad Request."""
    response = jsonify({"error": "Bad Request", "message": error.description})
    response.status_code = 400
    return response

@app.errorhandler(500)
def internal_error(error):
    """Return a JSON response for 500 Internal Server Error."""
    response = jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."})
    response.status_code = 500
    return response

if __name__ == "__main__":
    # Run the Flask development server
    app.run(debug=True)