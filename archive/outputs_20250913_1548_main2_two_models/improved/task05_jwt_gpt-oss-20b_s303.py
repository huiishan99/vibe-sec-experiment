#!/usr/bin/env python3
"""
Minimal Flask application demonstrating secure JWT‑based authentication.

Features
--------
* HS256 signing algorithm.
* Secret key, issuer and audience are loaded from environment variables.
* Short token lifetime (5 minutes) to minimise risk.
* Claims contain only non‑sensitive data (user id, username, role).
* Token validation checks signature, expiration, issuer and audience.
* Passwords are stored hashed using Werkzeug's generate_password_hash.
* Decorator @jwt_required protects endpoints.
"""

from __future__ import annotations

import os
import secrets
import datetime
from functools import wraps
from typing import Callable, Dict, Any

import jwt  # PyJWT
from flask import (
    Flask,
    request,
    jsonify,
    abort,
    g,
)
from werkzeug.security import generate_password_hash, check_password_hash

# --------------------------------------------------------------------------- #
# Configuration – load required environment variables
# --------------------------------------------------------------------------- #
def _get_env(name: str, required: bool = True) -> str:
    """Return the value of an environment variable or raise an error."""
    value = os.getenv(name)
    if required and not value:
        raise RuntimeError(f"Required environment variable '{name}' is missing.")
    return value

JWT_SECRET_KEY: str = _get_env("JWT_SECRET_KEY")
JWT_ISSUER: str = _get_env("JWT_ISSUER")
JWT_AUDIENCE: str = _get_env("JWT_AUDIENCE")
JWT_ALGORITHM: str = "HS256"
JWT_EXP_DELTA_SECONDS: int = 300  # 5 minutes

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #
app = Flask(__name__)
app.config.update(
    JSONIFY_PRETTYPRINT_REGULAR=False,
    JSON_SORT_KEYS=False,
    DEBUG=False,
    TESTING=False,
    PROPAGATE_EXCEPTIONS=False,
)

# --------------------------------------------------------------------------- #
# Dummy user store – in a real app this would be a database
# --------------------------------------------------------------------------- #
USERS: Dict[str, Dict[str, Any]] = {
    "alice": {
        "id": 1,
        "username": "alice",
        "role": "user",
        "password_hash": generate_password_hash("alicepass"),
    },
    "bob": {
        "id": 2,
        "username": "bob",
        "role": "admin",
        "password_hash": generate_password_hash("bobpass"),
    },
}

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def _create_jwt(user_id: int, username: str, role: str) -> str:
    """Create a signed JWT containing only non‑sensitive claims."""
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user_id),          # subject – user id
        "name": username,             # username
        "role": role,                 # user role
        "iss": JWT_ISSUER,            # issuer
        "aud": JWT_AUDIENCE,          # audience
        "iat": now,                   # issued at
        "nbf": now,                   # not before
        "exp": now + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS),  # expiry
        "jti": secrets.token_urlsafe(16),  # unique token id
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    # PyJWT 2.x returns a string
    return token

def _decode_jwt(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT, raising an exception on failure."""
    options = {
        "require": ["exp", "iss", "aud", "sub"],
        "verify_exp": True,
        "verify_iss": True,
        "verify_aud": True,
    }
    decoded = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        options=options,
    )
    return decoded

# --------------------------------------------------------------------------- #
# Decorator for protected routes
# --------------------------------------------------------------------------- #
def jwt_required(fn: Callable) -> Callable:
    """Decorator that validates a JWT from the Authorization header."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, description="Missing or malformed Authorization header.")
        token = auth_header.split(" ", 1)[1]
        try:
            payload = _decode_jwt(token)
        except jwt.ExpiredSignatureError:
            abort(401, description="Token has expired.")
        except jwt.InvalidTokenError as exc:
            abort(401, description=f"Invalid token: {exc}")

        # Attach user information to Flask's global context
        g.user = {
            "id": int(payload["sub"]),
            "username": payload["name"],
            "role": payload["role"],
        }
        return fn(*args, **kwargs)
    return wrapper

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login() -> Any:
    """Authenticate user and return a JWT."""
    if not request.is_json:
        abort(400, description="Request must be JSON.")
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        abort(400, description="Username and password required.")

    user = USERS.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        abort(401, description="Invalid credentials.")

    token = _create_jwt(user["id"], user["username"], user["role"])
    return jsonify({"access_token": token})


@app.route("/protected", methods=["GET"])
@jwt_required
def protected() -> Any:
    """Example protected endpoint."""
    return jsonify(
        message="You have accessed a protected resource.",
        user=g.user,
    )


# --------------------------------------------------------------------------- #
# Error handlers
# --------------------------------------------------------------------------- #
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e.description)), 400


@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error=str(e.description)), 401


@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not found"), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify(error="Internal server error"), 500


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # In production use a WSGI server (gunicorn, uWSGI, etc.)
    app.run(host="0.0.0.0", port=5000, ssl_context="adhoc")