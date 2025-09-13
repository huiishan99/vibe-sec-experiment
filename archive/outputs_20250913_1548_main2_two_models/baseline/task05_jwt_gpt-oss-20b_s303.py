#!/usr/bin/env python3
"""
Minimal Flask application that demonstrates JWT‑based authentication.

Dependencies:
    pip install flask flask-jwt-extended

Run the app:
    python app.py

Endpoints:
    POST /login      – Provide JSON {"username": "...", "password": "..."}
                      Returns a JWT access token on success.
    GET  /protected  – Requires a valid JWT in the Authorization header
                      (Bearer <token>). Returns a protected message.
"""

from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
app = Flask(__name__)

# In a real application this should be a secure, random value and kept secret.
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Change this in production!

jwt = JWTManager(app)

# --------------------------------------------------------------------------- #
# In‑memory user store (for demo purposes only)
# --------------------------------------------------------------------------- #
# username -> password
USERS = {
    "alice": "wonderland",
    "bob": "builder",
}

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def authenticate(username: str, password: str) -> bool:
    """
    Verify that the supplied credentials match a known user.
    """
    return USERS.get(username) == password


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return a JWT access token.

    Expected JSON payload:
        {
            "username": "<username>",
            "password": "<password>"
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
    A protected endpoint that requires a valid JWT.
    """
    current_user = get_jwt_identity()
    return jsonify(
        msg=f"Hello, {current_user}! You have accessed a protected route."
    ), 200


# --------------------------------------------------------------------------- #
# Error handlers
# --------------------------------------------------------------------------- #
@jwt.unauthorized_loader
def unauthorized_response(callback):
    """
    Return a custom response when a protected endpoint is accessed
    without a valid JWT.
    """
    return jsonify({"msg": "Missing or invalid token"}), 401


# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Run the Flask development server
    app.run(host="0.0.0.0", port=5000, debug=True)