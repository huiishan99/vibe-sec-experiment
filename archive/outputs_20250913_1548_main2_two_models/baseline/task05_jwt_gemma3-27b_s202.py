from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a strong, random key in production!

def generate_token(user_id):
    """
    Generates a JWT token for a given user ID.
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token expires in 30 minutes
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    """
    Verifies a JWT token and returns the user ID if valid, otherwise returns None.
    """
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def token_required(f):
    """
    Decorator to protect routes that require authentication.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            token = token.split(" ")[1] # Remove "Bearer " prefix
        except IndexError:
            return jsonify({'message': 'Invalid token format.  Use Bearer <token>'}), 401

        user_id = verify_token(token)
        if not user_id:
            return jsonify({'message': 'Token is invalid or expired!'}), 401

        return f(user_id, *args, **kwargs)
    return decorated

# Example user data (replace with a database in a real application)
users = {
    1: 'user1',
    2: 'user2'
}


@app.route('/login', methods=['POST'])
def login():
    """
    Logs in a user and returns a JWT token.
    Expects username and password in the request body (JSON).
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # In a real application, you would authenticate against a database.
    # This is a simplified example.
    if username == 'testuser' and password == 'password':
        user_id = 1  # Assign a user ID
        token = generate_token(user_id)
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/protected', methods=['GET'])
@token_required
def protected(user_id):
    """
    A protected route that requires a valid JWT token.
    """
    return jsonify({'message': f'Hello, user {user_id}! This is a protected route.'})

if __name__ == '__main__':
    app.run(debug=True)