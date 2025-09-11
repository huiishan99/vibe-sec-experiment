# app.py
"""
A minimal Flask application that demonstrates JWT‑based authentication.
It uses the `flask_jwt_extended` extension to issue and verify JSON Web Tokens.

Endpoints
---------
GET /          : Public endpoint, no authentication required.
POST /login    : Accepts JSON payload {"username": "...", "password": "..."}.
                 If credentials are valid, returns an access token.
GET /protected : Requires a valid JWT in the Authorization header.
"""

from flask import Flask, jsonify, request
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

# Secret key used to sign the JWTs. In production, keep this secret!
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Replace with a strong key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour

jwt = JWTManager(app)

# --------------------------------------------------------------------------- #
# In‑memory user store (for demo purposes only)
# --------------------------------------------------------------------------- #
# In a real application, replace this with a database lookup.
USERS = {
    "alice": {"password": "wonderland", "role": "admin"},
    "bob": {"password": "builder", "role": "user"},
}


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/", methods=["GET"])
def index():
    """Public endpoint."""
    return jsonify(message="Welcome! No authentication required."), 200


@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate user credentials and return a JWT.

    Expected JSON payload:
        {
            "username": "<username>",
            "password": "<password>"
        }

    Returns:
        200 OK with access token if credentials are valid.
        401 Unauthorized if credentials are invalid.
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
    A protected endpoint that requires a valid JWT.

    The JWT must be sent in the Authorization header:
        Authorization: Bearer <access_token>
    """
    current_user = get_jwt_identity()
    return (
        jsonify(
            message=f"Hello, {current_user}! You have accessed a protected route."
        ),
        200,
    )


# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # In production, use a proper WSGI server (e.g., gunicorn)
    app.run(debug=True)