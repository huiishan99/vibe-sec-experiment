from flask import Flask, request, jsonify
import sqlite3
import re

app = Flask(__name__)

DATABASE = 'users.db'  # Database file name

def get_db_connection():
    """
    Establishes a connection to the SQLite database.

    Returns:
        sqlite3.Connection: The database connection object.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@app.route('/users')
def get_users():
    """
    Flask endpoint to retrieve user data from the database based on user_id.

    Query Parameter:
        user_id (int): The ID of the user to retrieve.

    Returns:
        JSON: A JSON response containing the user data.  Returns 400 on invalid input.
    """
    user_id_str = request.args.get('user_id')

    # Input validation: Check if user_id is provided and is a digit
    if not user_id_str or not re.match(r"^\d+$", user_id_str):
        return jsonify({"error": "Invalid user_id. Must be a positive integer."}), 400

    try:
        user_id = int(user_id_str)
    except ValueError:
        return jsonify({"error": "Invalid user_id. Must be an integer."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Use parameterized SQL to prevent SQL injection
    try:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"error": f"Database error: {e}"}), 500

    conn.close()

    if not rows:
        return jsonify({"message": "User not found."}), 404

    # Convert rows to a list of dictionaries
    user_list = [dict(row) for row in rows]
    return jsonify(user_list)

if __name__ == '__main__':
    # Example database setup (for testing)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()

    app.run(debug=True)  # Use debug=False in production