from flask import Flask, request, jsonify
import sqlite3
import re

app = Flask(__name__)

DATABASE = 'users.db'  # Define the database file

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Endpoint to retrieve user data
@app.route('/users')
def get_users():
    """
    Retrieves user data from the database based on user_id provided in the query string.
    
    Validates input, uses parameterized SQL to prevent SQL injection, and returns JSON.
    """
    user_id_str = request.args.get('user_id')

    # Input validation: Check if user_id is provided and is a digit
    if not user_id_str:
        return jsonify({'error': 'user_id is required'}), 400
    
    if not re.match(r'^\d+$', user_id_str):
        return jsonify({'error': 'user_id must be a digit'}), 400

    try:
        user_id = int(user_id_str)
    except ValueError:
        return jsonify({'error': 'Invalid user_id'}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Parameterized SQL query to prevent SQL injection
    try:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': f'Database error: {e}'}), 500

    # Convert rows to a list of dictionaries
    user_list = [dict(row) for row in rows]

    conn.close()

    return jsonify(user_list)

if __name__ == '__main__':
    # Example database setup (for testing)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()

    app.run(debug=True)