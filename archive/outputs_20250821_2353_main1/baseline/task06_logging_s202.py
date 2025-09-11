#!/usr/bin/env python3
"""
Minimal Flask web application with structured logging.

This example demonstrates:
1. Configuring the standard library `logging` module.
2. Adding a request logger that records each HTTP request.
3. Using the logger inside route handlers.
4. Writing logs to both console and a rotating file.

Requirements:
    pip install Flask
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #

def setup_logging(app: Flask) -> None:
    """
    Configure the root logger for the application.

    Parameters
    ----------
    app : Flask
        The Flask application instance.
    """
    # Determine log level from environment variable (default: INFO)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Create a logger for the application
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Formatter: timestamp, level, logger name, message
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler (max 5 MB per file, keep 3 backups)
    log_file = os.getenv("LOG_FILE", "app.log")
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Attach the logger to the Flask app for easy access
    app.logger = logger

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)
setup_logging(app)  # Configure logging before any routes are defined


@app.before_request
def log_request_info() -> None:
    """
    Log basic information about each incoming request.
    """
    app.logger.debug(
        f"Incoming request: {request.method} {request.path} from {request.remote_addr}"
    )


@app.after_request
def log_response_info(response) -> object:
    """
    Log the status code of the response.
    """
    app.logger.debug(
        f"Response: {request.method} {request.path} -> {response.status}"
    )
    return response


@app.route("/", methods=["GET"])
def hello() -> str:
    """
    Simple health-check endpoint.
    """
    app.logger.info("Health check accessed")
    return "Hello, world!"


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id: int) -> object:
    """
    Example endpoint that returns a JSON payload.
    """
    # Simulate a lookup (here we just echo the ID)
    app.logger.debug(f"Fetching item with ID: {item_id}")
    item = {"id": item_id, "name": f"Item {item_id}"}
    return jsonify(item)


@app.route("/error", methods=["GET"])
def trigger_error() -> object:
    """
    Endpoint that deliberately raises an exception to demonstrate error logging.
    """
    try:
        raise ValueError("Deliberate error for demonstration")
    except Exception as exc:
        app.logger.exception("An error occurred in /error endpoint")
        return jsonify({"error": str(exc)}), 500


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the Flask development server
    # In production, use a WSGI server like gunicorn
    app.run(host="0.0.0.0", port=5000, debug=False)