#!/usr/bin/env python3
"""
Minimal Flask web application with secure logging.

Features
--------
* INFO level logging by default.
* Rotating file handler (max 5 MB per file, keep 3 backups).
* Custom filter that redacts common secret patterns (tokens, passwords, API keys).
* No logging of environment variables or request bodies that may contain secrets.
* Secure coding practices: secrets are read from environment variables and never logged.

Author: Senior Python Engineer
"""

import os
import re
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify

# --------------------------------------------------------------------------- #
# 1. Redaction utilities
# --------------------------------------------------------------------------- #

# Regular expressions for common secret patterns.
# These are intentionally simple; adjust as needed for your environment.
TOKEN_RE = re.compile(r"(?:token|access_token|api_key|secret|password)\s*=\s*[^&\s]+", re.IGNORECASE)
# Example: "token=abcd1234" -> "token=REDACTED"

def redact_secrets(text: str) -> str:
    """
    Replace any detected secret patterns with the string 'REDACTED'.
    """
    return TOKEN_RE.sub(r"\1=REDACTED", text)

class RedactFilter(logging.Filter):
    """
    Logging filter that redacts secrets from log messages.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if record.msg:
            record.msg = redact_secrets(record.msg)
        return True

# --------------------------------------------------------------------------- #
# 2. Logging configuration
# --------------------------------------------------------------------------- #

def configure_logging() -> None:
    """
    Configure the root logger:
    * INFO level
    * Rotating file handler
    * Redaction filter
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Rotating file handler: 5 MB per file, keep 3 backups
    log_file = os.path.join(os.path.dirname(__file__), "app.log")
    handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    handler.addFilter(RedactFilter())

    logger.addHandler(handler)

# --------------------------------------------------------------------------- #
# 3. Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# Load secret key from environment (never log it)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# Configure logging once at startup
configure_logging()
logger = logging.getLogger(__name__)

@app.before_request
def log_request_info() -> None:
    """
    Log basic request information, redacting sensitive headers.
    """
    # Copy headers to avoid mutating the original request object
    headers = dict(request.headers)
    # Redact Authorization header if present
    if "Authorization" in headers:
        headers["Authorization"] = "REDACTED"

    logger.info(
        f"Incoming request: {request.method} {request.path} | Headers: {headers}"
    )

@app.route("/health", methods=["GET"])
def health() -> jsonify:
    """
    Simple health check endpoint.
    """
    return jsonify(status="ok")

@app.route("/echo", methods=["POST"])
def echo() -> jsonify:
    """
    Echo back JSON payload. Demonstrates that request bodies are not logged.
    """
    data = request.get_json(silent=True) or {}
    return jsonify(received=data)

# --------------------------------------------------------------------------- #
# 4. Run the application
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Use environment variable to set the port; default to 5000
    port = int(os.getenv("PORT", 5000))
    # In production, use a proper WSGI server (gunicorn, uWSGI, etc.)
    app.run(host="0.0.0.0", port=port, debug=False)