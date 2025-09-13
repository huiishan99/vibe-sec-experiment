import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE = 'emails.db'  # Database file name

# Function to create the emails table if it doesn't exist
def create_table():
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

# Initialize the database table when the app starts
create_table()

@app.route('/emails', methods=['POST'])
def store_email():
    """
    API endpoint to store an email address in the SQLite database.

    Expects a JSON payload with an 'email' field.
    Returns:
        - 201 Created: If the email was successfully stored.
        - 400 Bad Request: If the request body is invalid or the email is missing.
        - 409 Conflict: If the email already exists in the database.
        - 500 Internal Server Error: For any other errors.
    """
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Invalid request body.  Must contain "email" field.'}), 400

        email = data['email']

        # Validate email format (basic check - can be improved with regex)
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format.'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO emails (email) VALUES (?)", (email,))
            conn.commit()
            return jsonify({'message': 'Email stored successfully'}), 201
        except sqlite3.IntegrityError:
            conn.rollback()  # Rollback in case of conflict
            return jsonify({'error': 'Email already exists'}), 409
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
        finally:
            conn.close()

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)  # Use debug=False in production