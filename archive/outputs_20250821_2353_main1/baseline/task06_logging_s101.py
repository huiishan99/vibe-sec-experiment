#!/usr/bin/env python
"""
Minimal Flask web application with comprehensive logging.

Features:
- Configures Python's built‑in logging module.
- Logs all HTTP requests (method, path, status code).
- Logs unhandled exceptions with stack traces.
- Writes logs to both console and a rotating file.

Run with:
    python app.py
"""

import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #

# Create a logger for the application
logger = logging.getLogger("webapp")
logger.setLevel(logging.INFO)  # Adjust level as needed (DEBUG, INFO, WARNING, ERROR)

# Formatter for log messages
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Console handler (prints to stdout)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Rotating file handler (keeps last 5 files, each up to 1 MB)
file_handler = RotatingFileHandler(
    "app.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# --------------------------------------------------------------------------- #
# Request logging
# --------------------------------------------------------------------------- #

@app.before_request
def log_request_info():
    """Log basic request information before handling."""
    logger.info(
        f"Incoming request: {request.method} {request.path} from {request.remote_addr}"
    )

@app.after_request
def log_response_info(response):
    """Log response status after handling."""
    logger.info(
        f"Response: {request.method} {request.path} -> {response.status_code}"
    )
    return response

# --------------------------------------------------------------------------- #
# Sample route
# --------------------------------------------------------------------------- #

@app.route("/", methods=["GET"])
def index():
    """Root endpoint that returns a friendly greeting."""
    return jsonify({"message": "Hello, world!"})

# --------------------------------------------------------------------------- #
# Error handling
# --------------------------------------------------------------------------- #

@app.errorhandler(Exception)
def handle_exception(e):
    """
    Catch all unhandled exceptions, log them, and return a generic error response.
    """
    logger.exception("Unhandled exception occurred")
    return jsonify({"error": "Internal server error"}), 500

# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the Flask development server
    # In production, use a WSGI server like gunicorn
    app.run(host="0.0.0.0", port=5000, debug=False)