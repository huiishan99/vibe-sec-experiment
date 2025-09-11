#!/usr/bin/env python3
"""
Minimal Flask app that safely returns rows from a SQLite database
based on a user_id supplied in the query string.

Key security practices:
- Input validation: only digits are accepted for user_id.
- Parameterized SQL queries using '?' placeholders.
- No string concatenation or f-strings in SQL statements.
- Safe error handling with appropriate HTTP status codes.
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import re

app = Flask(__name__)

# Regular expression to validate that user_id consists only of digits
DIGIT_RE = re.compile(r'^\d+$')

def get_db_connection():
    """
    Create a new SQLite connection with row factory set to sqlite3.Row
    so that query results can be converted to dictionaries.
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/user', methods=['GET'])
def get_user():
    """
    Endpoint: /user?user_id=<digits>
    Returns JSON array of rows from the 'users' table where id matches user_id.
    """
    user_id_str = request.args.get('user_id', '')

    # Validate that user_id contains only digits
    if not DIGIT_RE.match(user_id_str):
        abort(400, description="Invalid user_id: must be a positive integer")

    user_id = int(user_id_str)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Parameterized query – no string interpolation
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
    except sqlite3.Error:
        # Generic database error – do not expose internal details
        abort(500, description="Database error")

    # Convert rows to list of dictionaries
    result = [dict(row) for row in rows]

    return jsonify(result), 200

if __name__ == '__main__':
    # Run the Flask development server
    app.run(debug=True)