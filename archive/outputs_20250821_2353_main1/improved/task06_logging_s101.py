#!/usr/bin/env python3
"""
app.py – Minimal Flask web application with secure logging.

Features
--------
* INFO level logging by default.
* Rotating file handler (10 MB per file, keep 5 backups).
* Custom filter that redacts tokens, passwords and other secrets.
* No secrets (e.g. SECRET_KEY) are ever written to the log.
* Example route that logs request data safely.

Security notes
--------------
* Secrets are stored in environment variables and never logged.
* Log files are created with restrictive permissions (owner read/write only).
* The rotating handler prevents log files from growing indefinitely.
"""

import os
import re
import stat
import logging
import logging.handlers
from flask import Flask, request, jsonify

# --------------------------------------------------------------------------- #
# 1.  Redaction utilities
# --------------------------------------------------------------------------- #

# Regular expressions for common secret patterns.
TOKEN_RE = re.compile(r'(?:Authorization|Token|Bearer)\s*[:=]\s*([A-Za-z0-9\.\-_]+)', re.IGNORECASE)
PASSWORD_RE = re.compile(r'(?:password|passwd|pwd)\s*[:=]\s*([^\s&]+)', re.IGNORECASE)

def redact_message(msg: str) -> str:
    """
    Replace detected tokens and passwords with a placeholder.
    """
    # Redact Authorization headers or Bearer tokens
    msg = TOKEN_RE.sub(r'\1 [REDACTED]', msg)
    # Redact password fields in query strings or form data
    msg = PASSWORD_RE.sub(r'\1 [REDACTED]', msg)
    return msg

class RedactFilter(logging.Filter):
    """
    Logging filter that redacts sensitive information from log records.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if record.msg:
            record.msg = redact_message(record.msg)
        return True

# --------------------------------------------------------------------------- #
# 2.  Logging configuration
# --------------------------------------------------------------------------- #

def configure_logging(app_name: str = "myapp") -> logging.Logger:
    """
    Configure a logger with a rotating file handler and a console handler.
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)  # Default level

    # Rotating file handler – 10 MB per file, keep 5 backups
    log_file = f"{app_name}.log"
    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    handler.setLevel(logging.INFO)

    # Restrict log file permissions to owner read/write only
    os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Add the redaction filter
    handler.addFilter(RedactFilter())

    # Optional console output (INFO level)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    console.addFilter(RedactFilter())

    # Avoid duplicate handlers if configure_logging is called multiple times
    if not logger.handlers:
        logger.addHandler(handler)
        logger.addHandler(console)

    return logger

# --------------------------------------------------------------------------- #
# 3.  Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# Load secrets from environment – never log these values
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-secret-key")
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL", "sqlite:///app.db")

# Configure logger
log = configure_logging("webapp")

@app.before_request
def log_request_info():
    """
    Log incoming request details, redacting sensitive data.
    """
    # Build a string representation of the request
    req_info = (
        f"Method: {request.method} | "
        f"Path: {request.path} | "
        f"Headers: {dict(request.headers)} | "
        f"Body: {request.get_data(as_text=True)}"
    )
    log.info(req_info)

@app.route("/login", methods=["POST"])
def login():
    """
    Example endpoint that accepts JSON credentials.
    The credentials are logged but redacted.
    """
    data = request.get_json(silent=True) or {}
    # Log the received data (will be redacted by the filter)
    log.info(f"Login attempt: {data}")

    # Dummy authentication logic
    username = data.get("username")
    password = data.get("password")
    if username == "admin" and password == "secret":
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "failure"}), 401

@app.route("/")
def index():
    return "Hello, secure world!"

# --------------------------------------------------------------------------- #
# 4.  Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the Flask development server (not for production)
    # In production, use a WSGI server like gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=False)