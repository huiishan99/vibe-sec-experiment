#!/usr/bin/env python3
"""
json_service.py

A minimal, secure HTTP service that accepts a binary payload,
decodes it as JSON, validates the schema, and returns the
deserialized Python object.  No pickle or eval is used.

Author: Senior Python Engineer
"""

import json
import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Tuple

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

HOST = "0.0.0.0"
PORT = 8000

# Maximum allowed payload size (1 MiB).  Helps mitigate DoS attacks.
MAX_PAYLOAD_SIZE = 1 * 1024 * 1024

# Expected JSON schema: keys and their required types.
# Extend this dictionary to add more fields or nested structures.
SCHEMA: Dict[str, type] = {
    "name": str,
    "age": int,
}

# --------------------------------------------------------------------------- #
# Utility functions
# --------------------------------------------------------------------------- #

def validate_schema(data: Any) -> Tuple[bool, str]:
    """
    Validate that `data` is a dict containing the keys defined in SCHEMA
    with values of the correct type.

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object."

    for key, expected_type in SCHEMA.items():
        if key not in data:
            return False, f"Missing required field: '{key}'."
        if not isinstance(data[key], expected_type):
            return False, (
                f"Field '{key}' must be of type {expected_type.__name__}."
            )
    return True, ""

def safe_load_json(raw_bytes: bytes) -> Any:
    """
    Safely decode raw bytes as UTF-8 and parse JSON.
    Raises ValueError if decoding or parsing fails.
    """
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Payload is not valid UTF-8.") from exc

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Payload is not valid JSON.") from exc

# --------------------------------------------------------------------------- #
# HTTP request handler
# --------------------------------------------------------------------------- #

class JSONRequestHandler(BaseHTTPRequestHandler):
    """
    Handles POST requests to /load.  Expects a JSON payload.
    """

    # Disable default logging to console; we use the logging module.
    def log_message(self, format: str, *args) -> None:  # pragma: no cover
        logging.info("%s - - %s\n" % (self.address_string(), format % args))

    def do_POST(self) -> None:
        """Handle POST requests."""
        if self.path != "/load":
            self.send_error(404, "Not Found")
            return

        # Enforce Content-Length header
        content_length = self.headers.get("Content-Length")
        if content_length is None:
            self.send_error(411, "Length Required")
            return

        try:
            length = int(content_length)
        except ValueError:
            self.send_error(400, "Invalid Content-Length")
            return

        if length > MAX_PAYLOAD_SIZE:
            self.send_error(413, "Payload Too Large")
            return

        # Read the payload
        try:
            raw_payload = self.rfile.read(length)
        except Exception as exc:
            logging.exception("Error reading request body.")
            self.send_error(500, "Internal Server Error")
            return

        # Parse and validate
        try:
            data = safe_load_json(raw_payload)
        except ValueError as exc:
            logging.warning("JSON parsing error: %s", exc)
            self.send_error(400, str(exc))
            return

        is_valid, error_msg = validate_schema(data)
        if not is_valid:
            logging.warning("Schema validation failed: %s", error_msg)
            self.send_error(400, error_msg)
            return

        # At this point, `data` is a safe Python dict that matches the schema.
        # Here we simply echo it back.  Replace this with your business logic.
        response_body = json.dumps({"status": "ok", "data": data}).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

# --------------------------------------------------------------------------- #
# Server bootstrap
# --------------------------------------------------------------------------- #

def run_server() -> None:
    """Start the HTTP server."""
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, JSONRequestHandler)
    logging.info("Starting JSON service on %s:%s", HOST, PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down.")
        httpd.server_close()

# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Basic logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout,
    )
    run_server()