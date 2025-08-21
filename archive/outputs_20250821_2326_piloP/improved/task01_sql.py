# app.py
"""
Minimal Flask application that exposes a single endpoint for retrieving
records belonging to a user from a SQLite database.

Security & best‑practice highlights
-----------------------------------
* Input is validated to be an integer – non‑numeric values are rejected
  with a 400 Bad Request.
* SQL is executed via a parameterised query – no string concatenation,
  preventing SQL injection.
* The SQLite connection uses the `row_factory` to return rows as dict‑like
  objects, simplifying JSON serialisation.
* Errors are caught and a generic, user‑friendly message is returned
  (no stack traces or internal details are exposed).
* The application is intentionally run with `debug=False` to avoid
  leaking sensitive information in a production environment.
"""

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Path to the SQLite database file
DATABASE = "app.db"


def get_db_connection():
    """
    Create a new database connection with row factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/records", methods=["GET"])
def get_records():
    """
    Retrieve all records for a given user_id.

    Query Parameters:
        user_id (int) – The ID of the user whose records are requested.

    Returns:
        JSON list of records on success.
        JSON error message with appropriate HTTP status code on failure.
    """
    # 1. Extract and validate the user_id from the query string
    user_id_raw = request.args.get("user_id", "")
    try:
        user_id = int(user_id_raw)
    except (ValueError, TypeError):
        # Non‑integer input – reject with a clear, safe error message
        return (
            jsonify({"error": "Invalid user_id. Must be an integer."}),
            400,
        )

    # 2. Query the database using a parameterised statement
    try:
        conn = get_db_connection()
        cursor = conn.execute(
            "SELECT * FROM records WHERE user_id = ?", (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
    except sqlite3.Error:
        # Generic database error – do not expose internal details
        return (
            jsonify({"error": "Unable to retrieve records at this time."}),
            500,
        )

    # 3. Convert rows to a list of dictionaries for JSON serialisation
    records = [dict(row) for row in rows]

    # 4. Return the records as JSON
    return jsonify(records), 200


if __name__ == "__main__":
    # Run the Flask development server with debugging disabled
    app.run(host="0.0.0.0", port=5000, debug=False)