#!/usr/bin/env python3
"""
Minimal Flask application demonstrating secure JWT‑based authentication.

Features
--------
* Uses HS256 with a strong secret loaded from the environment.
* Short token lifetime (5 minutes) to reduce risk of token theft.
* Validates issuer (`iss`) and audience (`aud`) claims.
* Does not expose sensitive data in the JWT payload.
* Includes a simple in‑memory user store with hashed passwords.
* Provides a `@token_required` decorator for protected endpoints.
"""

import os
import datetime
import logging
from functools import wraps
from typing import Callable, Dict

import jwt
from flask import Flask, request, jsonify, _request_ctx_stack
from werkzeug.security import generate_password_hash, check_password_hash

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Load the secret key from the environment. It must be at least 32 bytes
# (256 bits) for HS256. Raise an error if missing or too short.
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET")
if not JWT_SECRET_KEY:
    raise RuntimeError("Environment variable JWT_SECRET is required.")
if len(JWT_SECRET_KEY) < 32:
    raise RuntimeError("JWT_SECRET must be at least 32 characters long.")

JWT_ALGORITHM: str = "HS256"
JWT_ISSUER: str = "myapp"
JWT_AUDIENCE: str = "myapp_users"
JWT_EXP_DELTA_SECONDS: int = 300  # 5 minutes

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

# --------------------------------------------------------------------------- #
# In‑memory user store (username -> hashed password)
# --------------------------------------------------------------------------- #

# For demonstration purposes only. In production use a proper database.
USER_DB: Dict[str, str] = {
    "alice": generate_password_hash("wonderland"),
    "bob": generate_password_hash("builder"),
}

# --------------------------------------------------------------------------- #
# Utility functions
# --------------------------------------------------------------------------- #

def create_jwt(user_id: str) -> str:
    """
    Create a signed JWT for the given user ID.

    The payload contains only non‑sensitive claims:
    * sub   – subject (user identifier)
    * iat   – issued at
    * exp   – expiration time
    * iss   – issuer
    * aud   – audience
    """
    now = datetime.datetime.utcnow()
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    # In PyJWT 2.x, encode returns a string; in 1.x it returns bytes.
    return token if isinstance(token, str) else token.decode("utf-8")


def decode_jwt(token: str) -> Dict:
    """
    Decode and validate a JWT.

    Raises jwt.PyJWTError on failure.
    """
    options = {"require": ["exp", "iat", "iss", "aud", "sub"]}
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        options=options,
    )


def get_token_from_header() -> str:
    """
    Extract the bearer token from the Authorization header.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise ValueError("Missing or malformed Authorization header")
    return auth_header.split(" ", 1)[1]


def token_required(f: Callable) -> Callable:
    """
    Decorator that ensures a valid JWT is present in the request.
    The decoded payload is attached to the request context as `jwt_payload`.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            token = get_token_from_header()
            payload = decode_jwt(token)
            _request_ctx_stack.top.jwt_payload = payload
        except (jwt.PyJWTError, ValueError) as exc:
            logging.warning("JWT validation failed: %s", exc)
            return jsonify({"msg": "Invalid or missing token"}), 401
        return f(*args, **kwargs)
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
        return jsonify({"msg": "Missing username or password"}), 400

    username = data["username"]
    password = data["password"]

    hashed = USER_DB.get(username)
    if not hashed or not check_password_hash(hashed, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_jwt(user_id=username)
    return jsonify({"access_token": token})


@app.route("/protected", methods=["GET"])
@token_required
def protected():
    """
    Example protected endpoint that requires a valid JWT.
    """
    payload = _request_ctx_stack.top.jwt_payload
    return jsonify({
        "msg": f"Hello, {payload['sub']}! You have accessed a protected resource.",
        "issued_at": payload["iat"],
        "expires_at": payload["exp"],
    })


# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000, debug=False)