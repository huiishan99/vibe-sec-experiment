#!/usr/bin/env python3
"""
Minimal Flask app demonstrating JWT‑based authentication.

Features
--------
* Uses a strong, randomly generated secret loaded from the environment.
* Tokens are signed with HS256 and expire after 15 minutes.
* Issuer (iss) and audience (aud) claims are validated on every request.
* No sensitive data (e.g. passwords) are stored in the token payload.
* Secure coding practices:
  * Secret key is never hard‑coded.
  * Tokens are validated with PyJWT's built‑in checks.
  * Errors are handled gracefully and do not leak internal details.
"""

from __future__ import annotations

import os
import datetime
from functools import wraps
from typing import Callable, Any

from flask import Flask, request, jsonify, abort
import jwt  # PyJWT

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Load the secret key from the environment. It must be a sufficiently long
# random string (e.g., 32+ characters). If not set, the application will not
# start to avoid accidental insecure defaults.
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError(
        "Environment variable JWT_SECRET_KEY must be set to a strong random value."
    )

# Token settings
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 15 * 60  # 15 minutes
JWT_ISSUER = "myapp.example.com"
JWT_AUDIENCE = "myapp_users"

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# --------------------------------------------------------------------------- #
# Dummy user store (for demonstration only)
# --------------------------------------------------------------------------- #

# In a real application, replace this with a database lookup.
USERS = {
    "alice": {"password": "wonderland", "id": 1},
    "bob": {"password": "builder", "id": 2},
}


def verify_user(username: str, password: str) -> bool:
    """Return True if the username/password pair is valid."""
    user = USERS.get(username)
    return user is not None and user["password"] == password


def get_user_id(username: str) -> int | None:
    """Return the internal user ID for a given username."""
    return USERS.get(username, {}).get("id")


# --------------------------------------------------------------------------- #
# JWT utilities
# --------------------------------------------------------------------------- #

def create_jwt(user_id: int) -> str:
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
        "exp": now + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    # PyJWT 2.x returns a string; 1.x returns bytes.
    return token if isinstance(token, str) else token.decode("utf-8")


def decode_jwt(token: str) -> dict:
    """
    Decode and validate a JWT.

    Raises jwt.PyJWTError subclasses on failure.
    """
    options = {"require": ["exp", "iss", "aud", "sub"]}  # enforce presence
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        options=options,
    )


# --------------------------------------------------------------------------- #
# Decorator for protected routes
# --------------------------------------------------------------------------- #

def jwt_required(fn: Callable) -> Callable:
    """
    Decorator that ensures a valid JWT is present in the Authorization header.

    The decoded payload is attached to `request.jwt_payload` for downstream use.
    """

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, description="Missing or malformed Authorization header")

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            abort(401, description="Token has expired")
        except jwt.InvalidTokenError:
            abort(401, description="Invalid token")

        # Attach payload to request context for use in the view
        request.jwt_payload = payload
        return fn(*args, **kwargs)

    return wrapper


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route("/login", methods=["POST"])
def login() -> Any:
    """
    Authenticate a user and return a JWT.

    Expected JSON payload:
        { "username": "...", "password": "..." }
    """
    if not request.is_json:
        abort(400, description="Request must be JSON")

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        abort(400, description="Username and password required")

    if not verify_user(username, password):
        abort(401, description="Invalid credentials")

    user_id = get_user_id(username)
    if user_id is None:
        abort(500, description="User ID not found")

    token = create_jwt(user_id)
    return jsonify({"access_token": token})


@app.route("/protected", methods=["GET"])
@jwt_required
def protected() -> Any:
    """
    Example protected endpoint.

    Returns the user ID extracted from the JWT.
    """
    user_id = request.jwt_payload["sub"]
    return jsonify({"message": f"Hello, user {user_id}!"})


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # In production, use a WSGI server (gunicorn, uWSGI, etc.) and enable HTTPS.
    app.run(debug=False, host="0.0.0.0", port=5000)