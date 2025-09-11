#!/usr/bin/env python3
"""
Minimal Flask application demonstrating JWT‑based authentication.

Features
--------
* Uses a strong, random secret key loaded from the environment
  (`JWT_SECRET`).  The key must be at least 256 bits (32 bytes) for
  HS256.  The application will refuse to start if the key is missing
  or too short.
* Tokens are signed with HS256, contain only non‑sensitive claims
  (`sub`, `iss`, `aud`, `iat`, `exp`).
* Tokens expire quickly (15 minutes) to limit the window of abuse.
* Issuer (`iss`) and audience (`aud`) are validated on every request.
* No sensitive data (e.g. passwords, personal info) is stored in the
  token payload.
* The example uses an in‑memory user store; replace with a real
  database in production.

Security notes
--------------
* Never expose the secret key in source code or logs.
* Use HTTPS in production to protect the token in transit.
* Store passwords hashed with a strong algorithm (e.g. bcrypt).
"""

import os
import datetime
import secrets
from functools import wraps

from flask import Flask, request, jsonify, abort
import jwt  # PyJWT

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Environment variables
JWT_SECRET = os.getenv("JWT_SECRET")          # 32‑byte hex string
JWT_ISSUER = os.getenv("JWT_ISSUER", "myapp") # Issuer claim
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "myapp_users")  # Audience claim
TOKEN_EXPIRY_MINUTES = 15  # Short expiry for security

# Validate the secret key
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required.")
# Ensure the secret is at least 32 bytes (256 bits)
if len(JWT_SECRET.encode()) < 32:
    raise RuntimeError("JWT_SECRET must be at least 32 bytes long.")

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# --------------------------------------------------------------------------- #
# Dummy user store (replace with a real database in production)
# --------------------------------------------------------------------------- #
# In a real app, passwords must be hashed (e.g. bcrypt) and never stored in
# plain text.  For demonstration, we keep them simple.
USERS = {
    "alice": {"password": "wonderland", "id": 1},
    "bob": {"password": "builder", "id": 2},
}

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def create_jwt(user_id: int) -> str:
    """
    Create a signed JWT for the given user ID.

    The payload contains only non‑sensitive claims:
    - sub: subject (user ID)
    - iss: issuer
    - aud: audience
    - iat: issued at
    - exp: expiration time
    """
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=TOKEN_EXPIRY_MINUTES),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # PyJWT 2.x returns a string; 1.x returns bytes
    return token if isinstance(token, str) else token.decode("utf-8")

def verify_jwt(token: str) -> dict:
    """
    Verify a JWT and return its payload.

    Raises jwt.PyJWTError if verification fails.
    """
    options = {"require": ["exp", "iat", "iss", "aud", "sub"]}
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=["HS256"],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        options=options,
    )
    return payload

def jwt_required(fn):
    """
    Decorator that enforces JWT authentication on a route.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, description="Missing or malformed Authorization header")
        token = auth_header[len("Bearer "):].strip()
        try:
            payload = verify_jwt(token)
        except jwt.PyJWTError as exc:
            abort(401, description=f"Invalid token: {exc}")
        # Attach user info to the request context if needed
        request.user = {"id": int(payload["sub"])}
        return fn(*args, **kwargs)
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
        abort(400, description="Missing username or password")

    user = USERS.get(username)
    if not user or user["password"] != password:
        abort(401, description="Invalid credentials")

    token = create_jwt(user["id"])
    return jsonify({"access_token": token, "token_type": "Bearer"})

@app.route("/protected", methods=["GET"])
@jwt_required
def protected():
    """
    Example protected endpoint that requires a valid JWT.
    """
    user_id = request.user["id"]
    return jsonify({"message": f"Hello, user {user_id}!"})

# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # In production, use a WSGI server (gunicorn, uWSGI, etc.) and HTTPS.
    app.run(debug=False, host="0.0.0.0", port=5000)