#!/usr/bin/env python3
"""
Minimal Flask app that exposes a single endpoint:

    GET /records?user_id=<id>

The endpoint reads the `user_id` query parameter, looks up all rows in the
`records` table of a SQLite database, and returns them as JSON.

Requirements
------------
* Python 3.8+
* Flask 2.x
* SQLite database file named `data.db` in the same directory.
  The database must contain a table named `records` with at least a
  column called `user_id`.  Example schema:

      CREATE TABLE records (
          id      INTEGER PRIMARY KEY,
          user_id INTEGER NOT NULL,
          data    TEXT
      );

Running
-------
    python3 app.py

The server will listen on http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import os

app = Flask(__name__)

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

def get_db_connection():
    """
    Create a new database connection and set row_factory to sqlite3.Row
    so that rows can be converted to dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/records", methods=["GET"])
def fetch_records():
    """
    Endpoint to fetch all records for a given user_id.

    Query Parameters:
        user_id (int) – required

    Returns:
        200 OK with JSON array of records
        400 Bad Request if user_id is missing or invalid
        404 Not Found if no records exist for the user
        500 Internal Server Error on unexpected failures
    """
    # Retrieve and validate the user_id query parameter
    user_id = request.args.get("user_id", type=int)
    if user_id is None:
        abort(400, description="Missing or invalid 'user_id' query parameter")

    try:
        conn = get_db_connection()
        cursor = conn.execute(
            "SELECT * FROM records WHERE user_id = ?", (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        # Log the error in a real application
        abort(500, description=f"Database error: {e}")

    if not rows:
        abort(404, description=f"No records found for user_id {user_id}")

    # Convert rows to list of dictionaries
    records = [dict(row) for row in rows]
    return jsonify(records), 200

# --------------------------------------------------------------------------- #
# If this file is executed directly, start the Flask development server.
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # In production, use a proper WSGI server instead.
    app.run(debug=True)