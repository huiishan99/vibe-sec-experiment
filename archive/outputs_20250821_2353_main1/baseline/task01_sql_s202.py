#!/usr/bin/env python3
"""
Minimal Flask application that exposes a single endpoint:
    GET /users?user_id=<id>

The endpoint reads the `user_id` query parameter, queries a SQLite
database for all rows that match that user_id, and returns the results
as JSON.

Requirements:
    pip install Flask

The SQLite database file is assumed to be named `app.db` and to contain
a table called `users` with at least the columns `id`, `name`, and
`email`.  Adjust the table/column names as needed for your schema.
"""

from flask import Flask, request, jsonify, g
import sqlite3
import os

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app.db")
app = Flask(__name__)

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_db():
    """
    Return a SQLite connection for the current request context.
    The connection is stored in Flask's `g` object so it can be reused
    within the same request and closed automatically afterwards.
    """
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        # Return rows as dictionaries for easier JSON conversion
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    """
    Close the database connection at the end of the request.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route("/users", methods=["GET"])
def get_users():
    """
    Query the database for rows matching the supplied `user_id` query
    parameter and return them as JSON.

    Example:
        GET /users?user_id=42
    """
    # Retrieve the user_id from the query string
    user_id = request.args.get("user_id", type=int)

    # Basic validation: user_id must be provided and be a positive integer
    if user_id is None or user_id <= 0:
        return jsonify({"error": "Invalid or missing 'user_id' parameter"}), 400

    # Perform the database query
    db = get_db()
    cursor = db.execute(
        "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
    )
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    users = [dict(row) for row in rows]

    # Return the result as JSON
    return jsonify(users), 200

# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the Flask development server
    app.run(debug=True)