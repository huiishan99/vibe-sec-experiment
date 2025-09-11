#!/usr/bin/env python3
"""
logging_setup.py

A minimal, secure logging configuration for a Python web application.
- Uses the standard `logging` module with INFO level by default.
- Redacts secrets (tokens, passwords, JWTs) from log messages.
- Writes logs to a rotating file handler.
- Configurable via environment variables.

Author: Senior Python Engineer
"""

import logging
import logging.handlers
import os
import re
from typing import Optional

# --------------------------------------------------------------------------- #
# 1. Secret‑redaction utilities
# --------------------------------------------------------------------------- #

# Regular expressions to find common secret patterns.
TOKEN_RE = re.compile(r'(token\s*=\s*)([^\s&]+)', re.IGNORECASE)
PASSWORD_RE = re.compile(r'(password\s*=\s*)([^\s&]+)', re.IGNORECASE)
JWT_RE = re.compile(r'\b[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b')

def redact_secrets(message: str) -> str:
    """
    Return a copy of *message* with any detected secrets replaced by 'REDACTED'.

    The function looks for:
    * `token=<value>`
    * `password=<value>`
    * Any JWT‑style string (three base64 segments separated by dots)

    Args:
        message: The original log message.

    Returns:
        A sanitized copy of the message.
    """
    # Redact token=... and password=...
    message = TOKEN_RE.sub(r'\1REDACTED', message)
    message = PASSWORD_RE.sub(r'\1REDACTED', message)

    # Redact any JWT token
    message = JWT_RE.sub('REDACTED', message)

    return message

# --------------------------------------------------------------------------- #
# 2. Custom Formatter that applies secret redaction
# --------------------------------------------------------------------------- #

class RedactingFormatter(logging.Formatter):
    """
    A logging formatter that redacts secrets from the log message.
    """
    def format(self, record: logging.LogRecord) -> str:
        # Preserve the original message for formatting
        original_msg = record.getMessage()
        # Redact secrets
        record.msg = redact_secrets(original_msg)
        # Let the base Formatter do the rest
        return super().format(record)

# --------------------------------------------------------------------------- #
# 3. Logger configuration
# --------------------------------------------------------------------------- #

def configure_logging(
    name: str = __name__,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure and return a logger with a rotating file handler and secret redaction.

    Parameters
    ----------
    name : str
        Name of the logger.
    log_file : str | None
        Path to the log file. If None, defaults to 'app.log' in the current directory.
    max_bytes : int
        Maximum size in bytes before rotating.
    backup_count : int
        Number of backup files to keep.
    level : int
        Logging level (default INFO).

    Returns
    -------
    logging.Logger
        The configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent double‑logging if root logger is configured elsewhere

    if not logger.handlers:
        # Determine log file path
        log_file = log_file or os.getenv('LOG_FILE', 'app.log')

        # Rotating file handler
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setLevel(level)

        # Formatter with timestamp, level, logger name, and message
        formatter = RedactingFormatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger

# --------------------------------------------------------------------------- #
# 4. Example usage in a Flask web application
# --------------------------------------------------------------------------- #

# The following block demonstrates how to integrate the logger into a Flask app.
# It is intentionally minimal and focuses on logging request data securely.

if __name__ == "__main__" and os.getenv('RUN_FLASK_APP') == '1':
    from flask import Flask, request, jsonify

    app = Flask(__name__)

    # Configure logger (environment variables can override defaults)
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

    logger = configure_logging(
        name='webapp',
        log_file=LOG_FILE,
        max_bytes=LOG_MAX_BYTES,
        backup_count=LOG_BACKUP_COUNT,
        level=getattr(logging, LOG_LEVEL, logging.INFO),
    )

    @app.before_request
    def log_request_info():
        """
        Log basic request information, redacting any secrets in query parameters or headers.
        """
        # Build a dictionary of request data to log
        data = {
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'query_string': request.query_string.decode('utf-8', errors='ignore'),
            'headers': dict(request.headers),
        }
        # Convert to string for logging
        logger.info(f"Incoming request: {data}")

    @app.route('/login', methods=['POST'])
    def login():
        """
        Dummy login endpoint that expects a JSON payload with 'username' and 'password'.
        The password is redacted in logs.
        """
        payload = request.get_json(silent=True) or {}
        username = payload.get('username', '<unknown>')
        password = payload.get('password', '<missing>')

        # Log the attempt (password will be redacted)
        logger.info(f"Login attempt: username={username} password={password}")

        # Dummy authentication logic
        if username == 'admin' and password == 'secret':
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "failure"}), 401

    @app.route('/')
    def index():
        return "Hello, secure world!"

    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=False)

# --------------------------------------------------------------------------- #
# 5. Public API
# --------------------------------------------------------------------------- #

__all__ = ['configure_logging', 'RedactingFormatter', 'redact_secrets']