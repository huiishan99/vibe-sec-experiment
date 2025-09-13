import sqlite3
import re
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.storage import RedisStorage
import os

app = Flask(__name__)

# Configuration - consider moving to a config file for production
DATABASE = 'emails.db'
RATE_LIMIT = '10 per minute'  # Adjust as needed
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost') # Use environment variable for Redis host
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

# Initialize rate limiter
limiter = Limiter(
    app,
    storage=RedisStorage(host=REDIS_HOST, port=REDIS_PORT),
    key_func=lambda: request.remote_addr,  # Rate limit by IP address
    default_limits=[RATE_LIMIT]
)

# Simple RFC 5322 compatible email validation (not perfect, but a good start)
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

def is_valid_email(email):
    """
    Validates an email address using a regular expression.
    """
    return bool(re.match(EMAIL_REGEX, email))

def create_connection():
    """
    Creates a database connection to the SQLite database.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_table(conn):
    """
    Creates the 'emails' table if it doesn't exist.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

@app.route('/emails', methods=['POST'])
@limiter.limit("10 per minute") # Apply rate limiting to this route
def store_email():
    """
    API endpoint to store an email address in the database.
    Validates the email format and ensures uniqueness.
    """
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'Email address is required'}), 400

    email = data['email']

    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    conn = create_connection()
    if conn is None:
        return jsonify({'error': 'Database connection error'}), 500

    try:
        cursor = conn.cursor()
        # Use parameterized SQL to prevent SQL injection
        cursor.execute("INSERT INTO emails (email) VALUES (?)", (email,))
        conn.commit()
        return jsonify({'message': 'Email stored successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email address already exists'}), 409
    except sqlite3.Error as e:
        print(f"Database error: {e}") # Log the error for debugging
        return jsonify({'error': 'Database error'}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Create the database connection and table if they don't exist
    conn = create_connection()
    if conn:
        create_table(conn)
        conn.close()
    app.run(debug=True) # Disable debug mode in production