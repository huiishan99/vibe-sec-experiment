#!/usr/bin/env python3
"""
Minimal Flask application demonstrating secure JWT‑based authentication.

Features
--------
* HS256 signing with a secret loaded from the environment.
* Short token lifetime (15 minutes).
* Validation of issuer and audience claims.
* No sensitive data stored in the token payload.
* Simple in‑memory user store (for demo purposes only).

Security notes
--------------
* Never hard‑code the JWT secret – it must come from an environment variable.
* The secret must be a strong random string (e.g. 32+ bytes).
* The token payload contains only the user identifier (`sub`) and standard
  claims (`iat`, `exp`, `iss`, `aud`). No passwords or other secrets are
  included.
* The token is transmitted via the `Authorization: Bearer <token>` header.
"""

import os
import datetime
from functools import wraps

from flask import Flask, request, jsonify, abort
import jwt  # PyJWT
from werkzeug.security import generate_password_hash, check_password_hash

# --------------------------------------------------------------------------- #
# Configuration – all secrets and identifiers must be supplied via env vars
# --------------------------------------------------------------------------- #
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ISSUER = os.getenv("JWT_ISSUER")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE")

# Verify that required environment variables are present
if not all([JWT_SECRET, JWT_ISSUER, JWT_AUDIENCE]):
    missing = [name for name, val in
               [("JWT_SECRET", JWT_SECRET),
                ("JWT_ISSUER", JWT_ISSUER),
                ("JWT_AUDIENCE", JWT_AUDIENCE)] if not val]
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

# Token lifetime – 15 minutes
TOKEN_EXPIRY_MINUTES = 15

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #
app = Flask(__name__)

# --------------------------------------------------------------------------- #
# In‑memory user store (username → {id, password_hash})
# --------------------------------------------------------------------------- #
# NOTE: In production use a real database and never store plain passwords.
USERS = {
    "alice": {
        "id": "user-1",
        "password_hash": generate_password_hash("alice_password")
    },
    "bob": {
        "id": "user-2",
        "password_hash": generate_password_hash("bob_password")
    }
}

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def create_jwt(user_id: str) -> str:
    """
    Create a signed JWT for the given user identifier.

    The payload contains:
        * sub   – subject (user id)
        * iat   – issued at
        * exp   – expiration time
        * iss   – issuer
        * aud   – audience
    """
    now = datetime.datetime.utcnow()
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # PyJWT 2.x returns a string; 1.x returns bytes
    return token if isinstance(token, str) else token.decode("utf-8")

def decode_jwt(token: str) -> dict:
    """
    Decode and validate a JWT.

    Raises jwt.PyJWTError on failure.
    """
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=["HS256"],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE
    )

def jwt_required(fn):
    """
    Decorator that enforces JWT authentication on a view.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, description="Missing or malformed Authorization header")
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_jwt(token)
        except jwt.PyJWTError as exc:
            abort(401, description=f"Invalid token: {exc}")
        # Attach user info to request context if needed
        request.user_id = payload["sub"]
        return fn(*args, **kwargs)
    return wrapper

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT.

    Expected JSON payload:
        {
            "username": "<username>",
            "password": "<password>"
        }
    """
    data = request.get_json(silent=True)
    if not data or "username" not in data or "password" not in data:
        abort(400, description="Missing username or password")

    username = data["username"]
    password = data["password"]

    user = USERS.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        abort(401, description="Invalid credentials")

    token = create_jwt(user["id"])
    return jsonify({"access_token": token, "token_type": "Bearer"})

@app.route("/protected", methods=["GET"])
@jwt_required
def protected():
    """
    Example protected endpoint that requires a valid JWT.
    """
    return jsonify({
        "message": f"Hello, user {request.user_id}! You have accessed a protected resource."
    })

# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # In production use a proper WSGI server (gunicorn, uWSGI, etc.)
    app.run(host="0.0.0.0", port=5000, debug=False)