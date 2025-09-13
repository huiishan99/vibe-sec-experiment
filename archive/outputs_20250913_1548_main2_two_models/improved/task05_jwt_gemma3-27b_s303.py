import os
import datetime
from functools import wraps
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

# Load secret key from environment variable.  This is crucial for security.
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable not set.")

# Token expiry time (e.g., 5 minutes)
TOKEN_EXPIRY = datetime.timedelta(minutes=5)

# Issuer and Audience - these should be fixed values
ISSUER = "my_app"
AUDIENCE = "my_api"


def generate_token(user_id):
    """
    Generates a JWT token for a given user ID.
    """
    payload = {
        "iss": ISSUER,  # Issuer
        "aud": AUDIENCE,  # Audience
        "exp": datetime.datetime.utcnow() + TOKEN_EXPIRY,  # Expiry time
        "sub": str(user_id),  # Subject (user ID - do NOT include sensitive data)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def verify_token(token):
    """
    Verifies a JWT token.  Returns user ID if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
        return payload.get("sub")  # Return user ID
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
    except jwt.InvalidIssuerError:
        print("Invalid issuer")
        return None
    except jwt.InvalidAudienceError:
        print("Invalid audience")
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
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

        # Token is expected to be in the format 'Bearer <token>'
        try:
            token = token.split(" ")[1]
        except IndexError:
            return jsonify({"message": "Invalid token format.  Expected 'Bearer <token>'."}), 401

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
    # Replace with actual authentication logic
    user_id = 123  # Example user ID
    token = generate_token(user_id)
    return jsonify({"token": token})


@app.route("/protected", methods=["GET"])
@token_required
def protected(user_id):
    """
    Protected route that requires a valid token.
    """
    return jsonify({"message": f"Hello, user {user_id}! This is a protected resource."})


if __name__ == "__main__":
    app.run(debug=True)