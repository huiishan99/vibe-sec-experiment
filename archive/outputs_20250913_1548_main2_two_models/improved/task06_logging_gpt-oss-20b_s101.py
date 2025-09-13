#!/usr/bin/env python3
"""
Minimal Flask web application demonstrating secure logging.

Features
--------
* Uses Python's built‑in logging module with INFO level by default.
* Logs requests and responses while redacting sensitive data
  (e.g. tokens, passwords, API keys).
* Uses a RotatingFileHandler to keep log files manageable.
* Secrets (e.g. database passwords) are never logged and are
  loaded from environment variables.

Author: Senior Python Engineer
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, g

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Load secrets from environment variables (never hard‑code them!)
SECRET_KEY = os.getenv("APP_SECRET_KEY", "default-secret-key")  # Flask secret key
DB_PASSWORD = os.getenv("DB_PASSWORD", "super-secret")          # Example DB password

# Logging configuration
LOG_FILE = "app.log"
MAX_BYTES = 5 * 1024 * 1024  # 5 MB per log file
BACKUP_COUNT = 3            # Keep 3 backup files

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def redact_sensitive(data: dict) -> dict:
    """
    Return a copy of *data* with sensitive keys redacted.
    Sensitive keys are defined in REDACT_KEYS.
    """
    REDACT_KEYS = {"password", "token", "api_key", "secret", "pwd"}
    redacted = {}
    for key, value in data.items():
        if key.lower() in REDACT_KEYS:
            redacted[key] = "***REDACTED***"
        else:
            redacted[key] = value
    return redacted

def log_request():
    """
    Log the incoming request details, redacting sensitive data.
    """
    # Gather request data
    data = {}
    if request.is_json:
        data = request.get_json(silent=True) or {}
    elif request.form:
        data = request.form.to_dict()
    # Redact sensitive fields
    safe_data = redact_sensitive(data)
    # Log the request
    logging.info(
        f"Incoming request: {request.method} {request.path} | "
        f"Headers: {dict(request.headers)} | Body: {safe_data}"
    )

def log_response(response):
    """
    Log the outgoing response status and optionally body.
    """
    # Avoid logging large bodies; log only status code
    logging.info(
        f"Response: {request.method} {request.path} | "
        f"Status: {response.status_code}"
    )
    return response

# --------------------------------------------------------------------------- #
# Logging setup
# --------------------------------------------------------------------------- #

def setup_logging():
    """
    Configure the root logger with a RotatingFileHandler.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Default level

    # Rotating file handler
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
    )
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Optional: also log to console (useful during development)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Use the loaded secret key

# Register request/response hooks
@app.before_request
def before_request():
    log_request()

@app.after_request
def after_request(response):
    return log_response(response)

# --------------------------------------------------------------------------- #
# Example routes
# --------------------------------------------------------------------------- #

@app.route("/login", methods=["POST"])
def login():
    """
    Example login endpoint that expects a JSON body with
    'username' and 'password'. The password is never logged.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Dummy authentication logic (replace with real auth)
    if username == "admin" and password == "admin123":
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route("/protected", methods=["GET"])
def protected():
    """
    Example protected endpoint that requires an Authorization header.
    The token is redacted in logs.
    """
    auth_header = request.headers.get("Authorization", "")
    # In a real app, validate the token here
    return jsonify({"data": "Sensitive data"}), 200

# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    setup_logging()
    # Run the Flask development server (not for production)
    app.run(host="0.0.0.0", port=5000, debug=False)