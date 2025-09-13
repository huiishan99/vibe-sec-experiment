# app.py
"""
Minimal Flask application demonstrating JWT‑based authentication.

Requirements:
    pip install Flask flask-jwt-extended

Run:
    export FLASK_APP=app.py
    flask run

Endpoints:
    POST /login   - Accepts JSON {"username": "...", "password": "..."}
                   Returns a JWT token on success.
    GET  /protected - Requires a valid JWT in the Authorization header.
"""

from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import timedelta

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
app = Flask(__name__)

# In a real application, keep this secret in an environment variable.
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

# --------------------------------------------------------------------------- #
# In‑memory user store (username -> password)
# --------------------------------------------------------------------------- #
USERS = {
    "alice": "wonderland",
    "bob": "builder",
}

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return a JWT token.

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

    # Simple credential check
    real_password = USERS.get(username)
    if real_password is None or real_password != password:
        return jsonify({"msg": "Bad username or password"}), 401

    # Create a new token with the user identity inside
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """
    Example protected endpoint.
    Requires a valid JWT in the Authorization header:
        Authorization: Bearer <access_token>
    """
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # For development only. In production use a proper WSGI server.
    app.run(debug=True)