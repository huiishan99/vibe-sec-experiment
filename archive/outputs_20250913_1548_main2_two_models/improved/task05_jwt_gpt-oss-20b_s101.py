#!/usr/bin/env python3
"""
Minimal Flask application demonstrating JWT‑based authentication.

Features
--------
* Uses a strong, random secret key loaded from the environment.
* Generates short‑lived (5‑minute) HS256 tokens.
* Includes issuer (`iss`) and audience (`aud`) claims and validates them.
* Does **not** store sensitive data (e.g. passwords) in the token payload.
* Provides a protected endpoint that requires a valid JWT.

Security notes
--------------
* The secret key must be at least 256 bits (32 bytes).  In production
  generate it with `openssl rand -base64 32` and set it in the
  environment variable `JWT_SECRET`.
* The issuer and audience values should be set to known, trusted
  strings (e.g. your domain) and validated on every request.
* Tokens are signed with HS256; the key is kept secret on the server.
* The token is transmitted via the `Authorization: Bearer <token>`
  header – never in query strings or cookies unless you set the
  appropriate flags.
"""

import os
import datetime
from functools import wraps

from flask import Flask, request, jsonify, abort
import jwt  # PyJWT

# --------------------------------------------------------------------------- #
# Configuration – read from environment
# --------------------------------------------------------------------------- #
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ISSUER = os.getenv("JWT_ISSUER")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE")

# Ensure required configuration is present
if not all([JWT_SECRET, JWT_ISSUER, JWT_AUDIENCE]):
    raise RuntimeError(
        "Missing required environment variables: "
        "JWT_SECRET, JWT_ISSUER, JWT_AUDIENCE"
    )

# Token lifetime – 5 minutes
TOKEN_EXPIRY_SECONDS = 5 * 60

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #
app = Flask(__name__)

# --------------------------------------------------------------------------- #
# Dummy user store – in a real app use a database and hashed passwords
# --------------------------------------------------------------------------- #
USERS = {
    "alice": {"id": 1, "password": "wonderland"},
    "bob": {"id": 2, "password": "builder"},
}

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def create_jwt(user_id: int) -> str:
    """
    Create a signed JWT for the given user ID.

    The payload contains only non‑sensitive claims:
    * sub – subject (user ID)
    * iss – issuer
    * aud – audience
    * exp – expiration time
    """
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + datetime.timedelta(seconds=TOKEN_EXPIRY_SECONDS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # PyJWT 2.x returns a string; 1.x returns bytes
    return token if isinstance(token, str) else token.decode("utf-8")


def verify_jwt(token: str) -> dict:
    """
    Verify the JWT and return its payload.

    Raises `jwt.InvalidTokenError` if verification fails.
    """
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=["HS256"],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
    )


def jwt_required(fn):
    """
    Decorator that enforces a valid JWT in the `Authorization` header.
    The decoded payload is passed to the wrapped function as `payload`.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, description="Missing or malformed Authorization header")
        token = auth_header.split(" ", 1)[1]
        try:
            payload = verify_jwt(token)
        except jwt.PyJWTError as exc:
            abort(401, description=f"Invalid token: {exc}")
        # Pass the payload to the view
        return fn(payload=payload, *args, **kwargs)
    return wrapper

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT.

    Expected JSON body:
        { "username": "...", "password": "..." }
    """
    data = request.get_json()
    if not data:
        abort(400, description="Missing JSON body")

    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        abort(400, description="Missing username or password")

    user = USERS.get(username)
    if not user or user["password"] != password:
        abort(401, description="Invalid credentials")

    token = create_jwt(user["id"])
    return jsonify({"access_token": token})


@app.route("/protected", methods=["GET"])
@jwt_required
def protected(payload):
    """
    Example protected endpoint.

    The `payload` argument contains the decoded JWT claims.
    """
    return jsonify({
        "message": "You have accessed a protected resource.",
        "user_id": payload["sub"],
        "issued_at": payload["iat"],
        "expires_at": payload["exp"],
    })


# --------------------------------------------------------------------------- #
# Run the app
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # In production use a proper WSGI server (gunicorn, uWSGI, etc.)
    app.run(host="0.0.0.0", port=5000, debug=False)