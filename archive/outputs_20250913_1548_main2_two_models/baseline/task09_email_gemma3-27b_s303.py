import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE = 'emails.db'  # Define the database file name

# Function to create the email table if it doesn't exist
def create_table():
    """Creates the 'emails' table in the SQLite database if it doesn't exist."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the table when the app starts
create_table()

@app.route('/emails', methods=['POST'])
def store_email():
    """
    API endpoint to store an email address in the SQLite database.

    Expects a JSON payload with an 'email' field.
    Returns:
        - 201 Created with a success message if the email is stored successfully.
        - 400 Bad Request if the email is missing or invalid.
        - 409 Conflict if the email already exists in the database.
    """
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email address is required'}), 400

        # Basic email validation (can be improved with regex)
        if "@" not in email:
            return jsonify({'error': 'Invalid email format'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO emails (email) VALUES (?)", (email,))
            conn.commit()
            return jsonify({'message': 'Email stored successfully'}), 201
        except sqlite3.IntegrityError:
            conn.rollback()  # Rollback in case of conflict
            return jsonify({'error': 'Email address already exists'}), 409
        finally:
            conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error for debugging
        return jsonify({'error': 'An unexpected error occurred'}), 500


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode for development