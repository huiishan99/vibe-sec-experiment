#!/usr/bin/env python3
"""
Minimal Flask application demonstrating JWT‑based authentication.

Dependencies:
    pip install flask flask_jwt_extended

Run the app:
    export FLASK_APP=jwt_demo.py
    flask run

Endpoints:
    POST /login      – Accepts JSON {"username": "...", "password": "..."}.
                       Returns a JWT access token on success.
    GET  /protected  – Requires a valid JWT in the Authorization header.
                       Returns a protected message.
"""

from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import timedelta

# --------------------------------------------------------------------------- #
# Application configuration
# --------------------------------------------------------------------------- #
app = Flask(__name__)

# Secret key used to sign the JWTs. In production, keep this secret!
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Replace with a secure key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

jwt = JWTManager(app)

# --------------------------------------------------------------------------- #
# In‑memory user store (for demo purposes only)
# --------------------------------------------------------------------------- #
USERS = {
    "alice": {"password": "wonderland", "role": "admin"},
    "bob":   {"password": "builder",   "role": "user"},
}

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def authenticate(username: str, password: str) -> bool:
    """Return True if the username/password pair is valid."""
    user = USERS.get(username)
    return user is not None and user["password"] == password

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return a JWT access token.

    Expected JSON payload:
        {
            "username": "alice",
            "password": "wonderland"
        }
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if not authenticate(username, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Create a new token with the user identity inside
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """
    Example protected endpoint that requires a valid JWT.

    The JWT must be sent in the Authorization header:
        Authorization: Bearer <access_token>
    """
    current_user = get_jwt_identity()
    return jsonify(
        msg=f"Hello, {current_user}! You have accessed a protected route."
    ), 200


# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # For development only – do not use debug=True in production
    app.run(debug=True)