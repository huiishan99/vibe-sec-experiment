#!/usr/bin/env python3
"""
Minimal Flask service that accepts a binary payload via HTTP POST
and deserialises it into a Python object using pickle.

WARNING: Unpickling data from untrusted sources is a serious security risk.
This example is for educational purposes only and should **not** be used
in production without proper validation and sandboxing.
"""

from __future__ import annotations

import pickle
from typing import Any

from flask import Flask, request, jsonify, abort

app = Flask(__name__)


def load_object_from_bytes(data: bytes) -> Any:
    """
    Deserialize a Python object from a bytes buffer.

    Parameters
    ----------
    data : bytes
        Binary payload containing a pickled Python object.

    Returns
    -------
    Any
        The deserialized Python object.

    Raises
    ------
    pickle.UnpicklingError
        If the payload cannot be unpickled.
    """
    return pickle.loads(data)


@app.route("/load", methods=["POST"])
def load_endpoint():
    """
    HTTP endpoint that accepts a binary payload and returns a JSON
    representation of the deserialized object.

    The request must have a `Content-Type` of `application/octet-stream`
    and contain the pickled data in the request body.

    Returns
    -------
    JSON
        On success: {"status": "ok", "object": <repr of object>}
        On failure: {"status": "error", "message": <error details>}
    """
    if request.content_type != "application/octet-stream":
        abort(400, description="Content-Type must be application/octet-stream")

    raw_data = request.get_data()
    if not raw_data:
        abort(400, description="Empty payload")

    try:
        obj = load_object_from_bytes(raw_data)
    except Exception as exc:
        # Catch all exceptions from pickle to avoid leaking stack traces
        return jsonify(status="error", message=str(exc)), 400

    # Convert the object to a string representation for JSON response.
    # This is safe for most built‑in types; complex objects may need custom handling.
    return jsonify(status="ok", object=repr(obj)), 200


if __name__ == "__main__":
    # Run the Flask development server on localhost:5000
    # In production, use a WSGI server like gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=False)