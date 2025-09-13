#!/usr/bin/env python3
"""
Minimal Flask web application with comprehensive logging.

Features:
- Rotating file handler (max 5 MB per file, keep 3 backups)
- Console output for quick debugging
- Request and response logging via Flask signals
- Exception logging with stack traces
"""

import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, g

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #
def configure_logging(app: Flask) -> None:
    """
    Attach a rotating file handler and a console handler to the Flask app's logger.
    The logger is set to INFO level; DEBUG can be enabled by changing the level.
    """
    # Create a formatter that includes timestamp, level, and message
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler: 5 MB per file, keep 3 backups
    file_handler = RotatingFileHandler(
        filename="app.log", maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Attach handlers to the Flask app's logger
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # Optional: silence Werkzeug's default logger to avoid duplicate logs
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


# --------------------------------------------------------------------------- #
# Flask application setup
# --------------------------------------------------------------------------- #
app = Flask(__name__)
configure_logging(app)


# --------------------------------------------------------------------------- #
# Request/Response logging
# --------------------------------------------------------------------------- #
@app.before_request
def log_request_info() -> None:
    """
    Log basic information about each incoming request.
    """
    app.logger.info(
        f"Incoming request: {request.method} {request.path} from {request.remote_addr}"
    )
    # Store start time for later use
    g.start_time = request.environ.get("werkzeug.request_start_time", None)


@app.after_request
def log_response_info(response) -> object:
    """
    Log the response status code and the time taken to process the request.
    """
    status = response.status
    app.logger.info(f"Response: {status} for {request.method} {request.path}")
    return response


# --------------------------------------------------------------------------- #
# Error handling
# --------------------------------------------------------------------------- #
@app.errorhandler(Exception)
def handle_exception(e: Exception):
    """
    Log unhandled exceptions with stack trace and return a generic error response.
    """
    app.logger.exception("Unhandled exception occurred")
    return jsonify({"error": "Internal Server Error"}), 500


# --------------------------------------------------------------------------- #
# Sample routes
# --------------------------------------------------------------------------- #
@app.route("/")
def hello():
    return "Hello, world!"


@app.route("/items/<int:item_id>")
def get_item(item_id: int):
    """
    Example endpoint that could raise an exception if item_id is negative.
    """
    if item_id < 0:
        raise ValueError("Item ID must be non-negative")
    return jsonify({"item_id": item_id, "name": f"Item {item_id}"})


# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Run the Flask development server
    app.run(debug=False, host="0.0.0.0", port=5000)