from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a strong, random key in production!

def generate_token(user_id):
    """
    Generates a JWT token for a given user ID.

    Args:
        user_id (int): The ID of the user.

    Returns:
        str: The JWT token.
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token expires in 30 minutes
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    """
    Verifies a JWT token.

    Args:
        token (str): The JWT token to verify.

    Returns:
        int: The user ID if the token is valid, None otherwise.
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
    Decorator to protect routes that require a valid token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            token = token.split(" ")[1] # Remove "Bearer " prefix
        except IndexError:
            return jsonify({'message': 'Invalid token format.  Expected "Bearer <token>"'}), 401
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'message': 'Token is invalid or expired!'}), 401

        return f(user_id, *args, **kwargs)
    return decorated

# Example user data (in a real app, this would come from a database)
users = {
    1: {'username': 'user1'},
    2: {'username': 'user2'}
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

    # In a real application, you would authenticate the user against a database.
    # This is a simplified example.
    if username == 'user1' and password == 'password123':
        user_id = 1
        token = generate_token(user_id)
        return jsonify({'token': token})
    elif username == 'user2' and password == 'password456':
        user_id = 2
        token = generate_token(user_id)
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/protected', methods=['GET'])
@token_required
def protected(user_id):
    """
    A protected route that requires a valid token.
    """
    user = users.get(user_id)
    if user:
        return jsonify({'message': f'Hello, {user["username"]}! This is a protected route.', 'user_id': user_id})
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)