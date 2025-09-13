#!/usr/bin/env python3
"""
Minimal Flask web application that demonstrates secure logging.

Features:
- INFO level logging by default.
- Rotating file handler (max 5 MB per file, keep 3 backups).
- Custom filter that redacts sensitive keys (token, password, secret, api_key).
- No secrets are logged; environment variables are used for configuration.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Use environment variables for secrets; do not hard‑code them.
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
# Example API token that should never appear in logs
API_TOKEN = os.getenv("API_TOKEN", "super-secret-token")

# --------------------------------------------------------------------------- #
# Logging setup
# --------------------------------------------------------------------------- #

def get_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger with a rotating file handler.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        # Logger already configured
        return logger

    logger.setLevel(logging.INFO)

    # Rotating file handler: 5 MB per file, keep 3 backups
    handler = RotatingFileHandler(
        filename="app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Add custom filter to redact sensitive data
    handler.addFilter(SensitiveDataFilter())

    logger.addHandler(handler)
    return logger

class SensitiveDataFilter(logging.Filter):
    """
    Redact values of keys that are considered sensitive.
    """
    # Keys that should never be logged in plain text
    SENSITIVE_KEYS = {"token", "password", "secret", "api_key", "apikey"}

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Replace sensitive values in the log message with '[REDACTED]'.
        """
        if record.args:
            # If the log message uses %-style formatting
            try:
                record.msg = record.msg % record.args
            except Exception:
                # If formatting fails, skip redaction
                return True
        # Simple regex to find key=value pairs
        import re

        def repl(match):
            key = match.group(1).lower()
            if key in self.SENSITIVE_KEYS:
                return f"{match.group(1)}=[REDACTED]"
            return match.group(0)

        record.msg = re.sub(r"(\b\w+\b)=([^\s,]+)", repl, record.msg)
        return True

# Create a module‑level logger
log = get_logger(__name__)

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Used by Flask for sessions, etc.

@app.before_request
def log_request_info():
    """
    Log basic request information, redacting sensitive query parameters.
    """
    # Build a dictionary of query parameters
    params = request.args.to_dict(flat=True)
    # Log the request method and path
    log.info(
        "Incoming request: %s %s | Params: %s",
        request.method,
        request.path,
        params,
    )

@app.route("/login", methods=["POST"])
def login():
    """
    Example endpoint that expects a JSON body with username and password.
    The password is redacted in logs.
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    # Log the attempt (password will be redacted by the filter)
    log.info("Login attempt: username=%s password=%s", username, password)

    # Dummy authentication logic
    if username == "admin" and password == "admin123":
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failure"}), 401

@app.route("/protected")
def protected():
    """
    Example protected endpoint that requires an API token in the header.
    The token is redacted in logs.
    """
    token = request.headers.get("Authorization", "")
    log.info("Accessing protected resource with token=%s", token)

    if token == f"Bearer {API_TOKEN}":
        return jsonify({"data": "Here is your protected data"}), 200
    else:
        return jsonify({"error": "Unauthorized"}), 403

# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the Flask development server
    # In production, use a WSGI server like gunicorn
    app.run(host="0.0.0.0", port=5000, debug=False)