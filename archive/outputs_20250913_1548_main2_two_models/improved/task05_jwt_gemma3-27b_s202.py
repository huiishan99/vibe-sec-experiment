import os
import datetime
from functools import wraps
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

# Load secret key from environment variable.  This is crucial for security.
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise EnvironmentError("JWT_SECRET_KEY must be set in the environment.")

# Token configuration
TOKEN_EXPIRY = datetime.timedelta(minutes=30)  # Short expiry for security
ISSUER = "my-app"
AUDIENCE = "my-app-client"


def generate_token(user_id):
    """
    Generates a JWT token for a given user ID.

    Args:
        user_id (int): The ID of the user.

    Returns:
        str: The JWT token.  Returns None if token generation fails.
    """
    try:
        payload = {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "exp": datetime.datetime.utcnow() + TOKEN_EXPIRY,
            "sub": str(user_id),  # Store only the user ID as the subject.  No sensitive data.
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    except Exception as e:
        print(f"Error generating token: {e}")  # Log the error for debugging
        return None


def verify_token(token):
    """
    Verifies a JWT token.

    Args:
        token (str): The JWT token to verify.

    Returns:
        int: The user ID if the token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=["HS256"], issuer=ISSUER, audience=AUDIENCE
        )
        return int(payload["sub"])  # Return user ID from subject
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None


def token_required(f):
    """
    Decorator to protect routes that require a valid token.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        # Token is expected in the format 'Bearer <token>'
        try:
            token = token.split(" ")[1]
        except IndexError:
            return jsonify({"message": "Invalid token format.  Use 'Bearer <token>'"}), 401

        user_id = verify_token(token)
        if not user_id:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(user_id, *args, **kwargs)

    return decorated


@app.route("/login", methods=["POST"])
def login():
    """
    Simulates user login and returns a JWT token.
    In a real application, this would authenticate against a database.
    """
    # In a real application, you would authenticate the user here.
    # For this example, we'll just assume the user is valid.
    user_id = 123  # Replace with actual user ID after authentication

    token = generate_token(user_id)
    if token:
        return jsonify({"token": token})
    else:
        return jsonify({"message": "Failed to generate token"}), 500


@app.route("/protected", methods=["GET"])
@token_required
def protected(user_id):
    """
    A protected route that requires a valid token.
    """
    return jsonify({"message": f"Hello, user {user_id}! This is a protected resource."})


if __name__ == "__main__":
    app.run(debug=True)