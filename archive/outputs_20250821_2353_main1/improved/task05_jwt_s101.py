#!/usr/bin/env python3
"""
Minimal Flask application demonstrating JWT‑based authentication.

Features
--------
* HS256 signing with a strong, randomly generated secret if not supplied.
* Short token lifetime (5 minutes) to reduce risk of token theft.
* Issuer and audience validation on every request.
* No sensitive data (e.g. passwords) stored in the JWT payload.
* Simple in‑memory user store for demonstration purposes.

Security notes
--------------
* In production, store the secret in a secure vault or environment variable.
* Use HTTPS to protect the token in transit.
* Consider rotating the secret periodically.
"""

import os
import secrets
import datetime
from functools import wraps

from flask import Flask, request, jsonify, abort
import jwt  # PyJWT

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Load configuration from environment variables
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    # Generate a strong random secret if none is provided
    JWT_SECRET = secrets.token_urlsafe(32)
    print("[WARNING] JWT_SECRET not set; generated a random secret. "
          "This will change on each restart, invalidating existing tokens.")

JWT_ISSUER = os.getenv("JWT_ISSUER", "myapp")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "myapp_users")
TOKEN_EXPIRY_MINUTES = 5  # Short expiry for security

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# --------------------------------------------------------------------------- #
# Dummy user store
# --------------------------------------------------------------------------- #
# In a real application, replace this with a database lookup.
USERS = {
    "alice": {"id": 1, "password": "wonderland"},
    "bob": {"id": 2, "password": "builder"},
}

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def create_token(user_id: int) -> str:
    """
    Create a signed JWT for the given user ID.

    The payload contains only non‑sensitive claims:
        - sub: subject (user ID)
        - iss: issuer
        - aud: audience
        - exp: expiration time
    """
    now = datetime.datetime.utcnow()
    payload = {
        "sub": user_id,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=TOKEN_EXPIRY_MINUTES),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # PyJWT 2.x returns a string; 1.x returns bytes
    return token if isinstance(token, str) else token.decode("utf-8")

def verify_token(token: str) -> dict:
    """
    Verify the JWT and return its payload.

    Raises jwt.PyJWTError on failure.
    """
    options = {"require": ["exp", "iss", "aud", "sub"]}  # enforce presence
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=["HS256"],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        options=options,
    )
    return payload

def jwt_required(f):
    """
    Decorator that enforces a valid JWT in the Authorization header.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            abort(401, description="Missing or malformed Authorization header")
        token = auth.split(" ", 1)[1]
        try:
            payload = verify_token(token)
        except jwt.PyJWTError as exc:
            abort(401, description=f"Invalid token: {exc}")
        # Attach payload to request context for downstream use
        request.jwt_payload = payload
        return f(*args, **kwargs)
    return wrapper

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT.

    Expected JSON body:
        {
            "username": "<username>",
            "password": "<password>"
        }
    """
    data = request.get_json()
    if not data:
        abort(400, description="Missing JSON body")

    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        abort(400, description="username and password required")

    user = USERS.get(username)
    if not user or user["password"] != password:
        abort(401, description="Invalid credentials")

    token = create_token(user["id"])
    return jsonify({"access_token": token}), 200

@app.route("/protected", methods=["GET"])
@jwt_required
def protected():
    """
    Example protected endpoint that requires a valid JWT.
    """
    user_id = request.jwt_payload["sub"]
    return jsonify({"message": f"Hello, user {user_id}!"}), 200

# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # In production, use a WSGI server (gunicorn, uWSGI, etc.) and HTTPS.
    app.run(debug=True, host="0.0.0.0", port=5000)