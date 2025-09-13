#!/usr/bin/env python3
"""
Minimal HTTP service that accepts a binary payload and deserialises it into a Python object.

The service exposes a single POST endpoint `/load`.  The request body must contain the
raw bytes of a pickled Python object.  The server will attempt to `pickle.loads`
the payload and return a JSON response indicating success or failure.

⚠️  WARNING:  Unpickling data from untrusted sources is a serious security risk.
This example is intentionally minimal and should **not** be used in production
without proper sandboxing or validation of the payload.
"""

from __future__ import annotations

import json
import logging
import os
import pickle
from typing import Any

from flask import Flask, Response, request

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Default port – can be overridden with the environment variable `PORT`
PORT: int = int(os.getenv("PORT", "5000"))

# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/load", methods=["POST"])
def load_object() -> Response:
    """
    Accept a binary payload and attempt to deserialize it with pickle.

    Returns:
        JSON response with keys:
            - success (bool)
            - message (str)
            - type (str, optional) – type name of the deserialized object
    """
    # Ensure the request contains data
    if not request.data:
        logger.warning("Empty payload received")
        return _json_response(False, "No data received"), 400

    try:
        # Attempt to unpickle the payload
        obj: Any = pickle.loads(request.data)
    except Exception as exc:
        # Any exception during unpickling is reported back
        logger.exception("Failed to unpickle payload")
        return _json_response(False, f"Unpickling error: {exc}"), 400

    # Successful deserialization
    logger.info("Successfully unpickled object of type %s", type(obj).__name__)
    return _json_response(
        True,
        "Object deserialized successfully",
        type_name=type(obj).__name__,
    ), 200


def _json_response(success: bool, message: str, type_name: str | None = None) -> Response:
    """
    Helper to build a JSON response.

    Args:
        success: Whether the operation succeeded.
        message: Human‑readable message.
        type_name: Optional type name of the deserialized object.

    Returns:
        Flask Response object with JSON payload.
    """
    payload = {"success": success, "message": message}
    if type_name:
        payload["type"] = type_name
    return Response(
        json.dumps(payload),
        mimetype="application/json",
        status=200 if success else 400,
    )


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the Flask development server
    app.run(host="0.0.0.0", port=PORT)