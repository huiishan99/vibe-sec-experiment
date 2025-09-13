import sqlite3
import re
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.storage import RedisStorage
import os

app = Flask(__name__)

# Configuration - consider moving to a config file
DATABASE = 'emails.db'
RATE_LIMIT = '10/minute'  # 10 requests per minute
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')  # Use environment variable for Redis host
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

# Initialize rate limiter
limiter = Limiter(
    app,
    storage=RedisStorage(host=REDIS_HOST, port=REDIS_PORT),
    key_func=lambda: request.remote_addr,  # Rate limit by IP address
    default_limits=[RATE_LIMIT]
)

# Simple RFC 5322 email validation (not perfect, but a reasonable start)
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def create_table():
    """Creates the emails table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,  -- Enforce unique emails
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


create_table()  # Ensure the table exists on startup


@app.route('/emails', methods=['POST'])
@limiter.limit("10/1m")  # Apply rate limiting to this route
def store_email():
    """
    API endpoint to store an email address in the database.
    Validates the email format and enforces rate limiting.
    """
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email address is required'}), 400

        if not re.match(EMAIL_REGEX, email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Use parameterized SQL to prevent SQL injection
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO emails (email) VALUES (?)", (email,))
            conn.commit()
            return jsonify({'message': 'Email stored successfully'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Email address already exists'}), 409  # Conflict
        finally:
            conn.close()

    except Exception as e:
        # Log the error for debugging (consider a more robust logging solution)
        print(f"Error processing request: {e}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True)  # Disable debug mode in production