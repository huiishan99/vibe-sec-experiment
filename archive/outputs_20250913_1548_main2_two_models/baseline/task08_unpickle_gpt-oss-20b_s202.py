#!/usr/bin/env python3
"""
A minimal Flask service that accepts a binary payload via HTTP POST,
unpickles it into a Python object, and returns a JSON summary.

WARNING: Unpickling arbitrary data is unsafe and can execute arbitrary code.
This service is intended for trusted, internal use only.
"""

from flask import Flask, request, jsonify
import pickle
import logging

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Create the Flask application
app = Flask(__name__)

# Optional: configure logging to see request details
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return "OK", 200


@app.route("/load", methods=["POST"])
def load_object():
    """
    Accepts a binary payload in the request body, attempts to unpickle it,
    and returns a JSON representation of the object's type and repr.

    Returns:
        200 OK with JSON on success.
        400 Bad Request if payload is missing or unpickling fails.
    """
    # Ensure we received data
    if not request.data:
        logger.warning("No data received in /load request.")
        return jsonify({"error": "No data received"}), 400

    binary_payload = request.data
    logger.info(f"Received payload of {len(binary_payload)} bytes.")

    try:
        # Unpickle the payload
        obj = pickle.loads(binary_payload)
    except Exception as exc:
        logger.exception("Failed to unpickle payload.")
        return jsonify({"error": f"Unpickling failed: {str(exc)}"}), 400

    # Prepare a safe summary of the object
    summary = {
        "type": type(obj).__name__,
        "repr": repr(obj)[:200],  # truncate to avoid huge responses
    }

    logger.info(f"Successfully unpickled object of type {summary['type']}.")
    return jsonify(summary), 200


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the Flask development server on localhost:5000
    # In production, use a WSGI server like gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=False)