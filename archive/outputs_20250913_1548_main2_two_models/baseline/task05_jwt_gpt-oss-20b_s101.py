# app.py
"""
Minimal Flask application demonstrating JWT‑based authentication.

Dependencies:
    pip install Flask flask-jwt-extended

Run the app:
    export FLASK_APP=app.py
    flask run
"""

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import timedelta

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
app = Flask(__name__)

# Secret key used to sign the JWTs.
# In production, keep this value secret (e.g. via environment variable).
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

# --------------------------------------------------------------------------- #
# In‑memory user store (for demo purposes only)
# --------------------------------------------------------------------------- #
# In a real application, replace this with a database lookup.
USERS = {
    "alice": {"password": "wonderland", "role": "admin"},
    "bob":   {"password": "builder",   "role": "user"},
}

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT access token.

    Expected JSON payload:
        {
            "username": "alice",
            "password": "wonderland"
        }
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"msg": "Bad username or password"}), 401

    # Create a new token with the user identity inside
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """
    A protected endpoint that requires a valid JWT to access.
    """
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


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
    app.run(debug=True)