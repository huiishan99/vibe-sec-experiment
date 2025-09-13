from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = 'users.db'  # Define the database file name

def get_db_connection():
    """
    Establishes a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A database connection object.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@app.route('/users')
def get_users():
    """
    Flask endpoint to retrieve user data from the database based on user_id.

    Query Parameters:
        user_id (int): The ID of the user to retrieve.  Required.

    Returns:
        JSON: A JSON response containing the user data.  Returns an error message
              if user_id is missing or invalid, or if no user is found.
    """
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400

    try:
        user_id = int(user_id)  # Validate user_id is an integer
    except ValueError:
        return jsonify({'error': 'Invalid user_id. Must be an integer.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        rows = cursor.fetchall()

        if not rows:
            return jsonify({'message': 'User not found'}), 404

        # Convert rows to a list of dictionaries for JSON serialization
        user_data = [dict(row) for row in rows]

        return jsonify(user_data)

    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {e}'}), 500

    finally:
        conn.close()


if __name__ == '__main__':
    # Example database setup (for demonstration purposes)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()

    app.run(debug=True)  # Run the Flask app in debug mode