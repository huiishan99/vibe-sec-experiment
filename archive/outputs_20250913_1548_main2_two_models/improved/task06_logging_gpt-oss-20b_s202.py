#!/usr/bin/env python3
"""
Minimal Flask web application with secure logging.

Features:
- INFO level logging by default.
- Rotating file handler (10 MB per file, 5 backups).
- Redacts secrets (passwords, tokens, API keys, etc.) from logs.
- Does not log environment secrets.
- Uses a custom logging filter to scrub log messages.

Author: Senior Python Engineer
"""

import os
import re
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Log file location – can be overridden by the LOG_FILE environment variable.
LOG_FILE = os.getenv("LOG_FILE", "app.log")

# Maximum size of a single log file (bytes) before rotation.
MAX_BYTES = 10 * 1024 * 1024  # 10 MB

# Number of backup log files to keep.
BACKUP_COUNT = 5

# List of keys that should be redacted when logging dictionaries.
SECRET_KEYS = {
    "password",
    "token",
    "api_key",
    "secret",
    "key",
    "access_token",
    "refresh_token",
    "authorization",
    "auth",
}

# Regular expression to find token-like patterns in strings.
TOKEN_REGEX = re.compile(
    r"""
    (?P<key>token|access_token|refresh_token|authorization|auth)\s*[:=]\s*
    (?P<value>[^\s,]+)
    """,
    re.IGNORECASE | re.VERBOSE,
)

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def redact_dict(data):
    """
    Recursively redact sensitive keys in a dictionary.
    Returns a new dictionary with secrets replaced by '[REDACTED]'.
    """
    if not isinstance(data, dict):
        return data
    redacted = {}
    for k, v in data.items():
        if k.lower() in SECRET_KEYS:
            redacted[k] = "[REDACTED]"
        else:
            redacted[k] = redact_dict(v) if isinstance(v, dict) else v
    return redacted

def redact_string(text):
    """
    Redact token-like patterns in a string.
    """
    def repl(match):
        return f"{match.group('key')}=[REDACTED]"
    return TOKEN_REGEX.sub(repl, text)

class RedactFilter(logging.Filter):
    """
    Logging filter that redacts secrets from log messages.
    """
    def filter(self, record):
        # Redact message
        record.msg = redact_string(record.msg)
        # Redact any dict in the record's args
        if isinstance(record.args, dict):
            record.args = redact_dict(record.args)
        return True

# --------------------------------------------------------------------------- #
# Logging setup
# --------------------------------------------------------------------------- #

def setup_logging():
    """
    Configure the root logger with a rotating file handler and redaction filter.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Rotating file handler
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
    )
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    handler.addFilter(RedactFilter())

    logger.addHandler(handler)

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

@app.before_request
def log_request_info():
    """
    Log incoming request details, redacting sensitive data.
    """
    logger = logging.getLogger("app.request")
    # Redact headers that may contain secrets
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() != "authorization"
    }
    # Redact JSON body if present
    if request.is_json:
        try:
            body = request.get_json(silent=True) or {}
            body = redact_dict(body)
        except Exception:
            body = "[UNABLE TO PARSE JSON]"
    else:
        body = request.get_data(as_text=True)
        body = redact_string(body)

    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "path": request.path,
            "headers": headers,
            "body": body,
        },
    )

@app.after_request
def log_response_info(response):
    """
    Log outgoing response status.
    """
    logger = logging.getLogger("app.response")
    logger.info(
        "Response",
        extra={
            "status": response.status,
            "headers": dict(response.headers),
        },
    )
    return response

@app.route("/login", methods=["POST"])
def login():
    """
    Example endpoint that accepts JSON with a password and token.
    The values are redacted in the logs.
    """
    data = request.get_json() or {}
    # In a real app, you would authenticate here.
    return jsonify({"message": "Login successful"}), 200

# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    setup_logging()
    # Run the Flask development server (not for production use).
    app.run(host="0.0.0.0", port=5000, debug=False)