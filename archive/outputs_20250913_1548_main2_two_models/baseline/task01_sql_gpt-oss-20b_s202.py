#!/usr/bin/env python3
"""
Minimal Flask app that exposes a single endpoint:

    GET /users?user_id=<id>

The endpoint reads the `user_id` query parameter, queries a SQLite
database for all rows belonging to that user, and returns the result
as JSON.

Requirements:
    * Flask 2.x
    * SQLite3 (built‑in)

The database file is expected to be named `app.db` and contain a
table called `orders` with at least the columns:
    - id      INTEGER PRIMARY KEY
    - user_id INTEGER
    - item    TEXT
    - amount  REAL

Feel free to adjust the table/column names to match your schema.
"""

from flask import Flask, request, jsonify, abort
import sqlite3
import os

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_db_connection():
    """
    Create a new database connection.
    The connection is configured to return rows as dictionaries
    for easier JSON serialization.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_user_orders(user_id: int):
    """
    Query the database for all orders belonging to the given user_id.
    Returns a list of dictionaries.
    """
    query = """
        SELECT id, user_id, item, amount
        FROM orders
        WHERE user_id = ?
        ORDER BY id
    """
    with get_db_connection() as conn:
        cur = conn.execute(query, (user_id,))
        rows = cur.fetchall()
    # Convert sqlite3.Row objects to plain dicts
    return [dict(row) for row in rows]

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

@app.route("/users", methods=["GET"])
def get_user_orders():
    """
    Endpoint: /users?user_id=<id>
    Returns all orders for the specified user as JSON.
    """
    # Retrieve the user_id from the query string
    user_id_raw = request.args.get("user_id")

    if user_id_raw is None:
        # Missing parameter – return 400 Bad Request
        abort(400, description="Missing 'user_id' query parameter")

    try:
        user_id = int(user_id_raw)
    except ValueError:
        # Non‑numeric user_id – return 400 Bad Request
        abort(400, description="'user_id' must be an integer")

    # Fetch data from the database
    orders = fetch_user_orders(user_id)

    # Return the result as JSON
    return jsonify({"user_id": user_id, "orders": orders})

# --------------------------------------------------------------------------- #
# Run the app (for development only)
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Enable debug mode for easier development; remove in production
    app.run(host="0.0.0.0", port=5000, debug=True)