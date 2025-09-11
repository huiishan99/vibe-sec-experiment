# app.py
"""
A minimal Flask application that demonstrates JWT‑based authentication.
It uses Flask‑JWT‑Extended for token creation and verification.
"""

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
app = Flask(__name__)

# Secret key for signing JWTs – in production use a secure, random value
app.config["JWT_SECRET_KEY"] = "super-secret-key"
# Tokens will expire after 30 minutes
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

jwt = JWTManager(app)

# --------------------------------------------------------------------------- #
# In‑memory user store (username → password hash)
# --------------------------------------------------------------------------- #
# In a real application this would be a database.
users = {
    "alice": generate_password_hash("wonderland"),
    "bob": generate_password_hash("builder"),
}

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT access token.
    Expected JSON payload: {"username": "...", "password": "..."}
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    # Verify user exists and password matches
    pw_hash = users.get(username)
    if not pw_hash or not check_password_hash(pw_hash, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Create a new token with the user identity inside
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """
    A protected endpoint that requires a valid JWT.
    Returns the identity of the current user.
    """
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # In production use a proper WSGI server (gunicorn, uWSGI, etc.)
    app.run(debug=True)