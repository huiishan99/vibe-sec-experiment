#!/usr/bin/env python3
"""
Minimal Flask app that exposes a single endpoint for retrieving rows
from a SQLite database based on a user_id supplied in the query string.

Security notes:
- Input is validated to contain only digits.
- The SQL statement uses a parameterized query with a '?' placeholder.
- No string concatenation or f-strings are used to build the SQL.
- Database connections are closed automatically via context managers.
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import re

app = Flask(__name__)

# Regular expression that matches a string consisting solely of digits.
DIGIT_RE = re.compile(r'^\d+$')

# Path to the SQLite database file.
DB_PATH = 'app.db'


def get_db_connection():
    """
    Create a new database connection.
    The connection is returned as a context manager so it will be closed
    automatically when the block exits.
    """
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dictionaries for easier JSON serialization.
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/users', methods=['GET'])
def get_user_rows():
    """
    Endpoint: /users?user_id=<id>
    Returns all rows from the 'users' table that match the supplied user_id.
    """
    user_id_str = request.args.get('user_id', '')

    # Validate that the input consists only of digits.
    if not DIGIT_RE.match(user_id_str):
        # Return a generic error message without revealing internal details.
        abort(400, description="Invalid user_id. Must be a positive integer.")

    # Convert to integer for safety.
    user_id = int(user_id_str)

    # Parameterized query: the '?' placeholder prevents SQL injection.
    query = "SELECT * FROM users WHERE id = ?"

    try:
        with get_db_connection() as conn:
            cursor = conn.execute(query, (user_id,))
            rows = cursor.fetchall()
    except sqlite3.Error as e:
        # Log the error in a real application; here we just return a generic message.
        abort(500, description="Database error.")

    # Convert rows to a list of dictionaries.
    result = [dict(row) for row in rows]

    return jsonify(result), 200


# --------------------------------------------------------------------------- #
# The following block allows the module to be run directly.
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    # In production, use a proper WSGI server instead of Flask's built‑in server.
    app.run(host='0.0.0.0', port=5000, debug=False)