#!/usr/bin/env python3
"""
Secure JSON payload loader service.

This FastAPI application exposes a single endpoint `/load` that accepts a binary
payload (raw bytes). The payload is expected to be a UTF‑8 encoded JSON document.
The service validates the JSON against a predefined schema before using it,
ensuring that only expected data structures are processed.

Key security measures:
- No use of pickle or other unsafe deserialization mechanisms.
- Strict JSON schema validation via `jsonschema`.
- Payload size limit to mitigate DoS attacks.
- Comprehensive error handling with clear HTTP status codes.
- Logging of request metadata without exposing sensitive data.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

import jsonschema
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
import uvicorn

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Maximum allowed payload size (bytes). Adjust as needed.
MAX_PAYLOAD_SIZE: int = 1_048_576  # 1 MiB

# JSON schema definition for incoming payloads.
# Example: expects an object with a string `name`, integer `age`, and optional
# list of string `tags`.
SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": True,
        },
    },
    "required": ["name", "age"],
    "additionalProperties": False,
}

# --------------------------------------------------------------------------- #
# Application setup
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="Secure JSON Loader",
    description="Loads and validates JSON payloads without using pickle.",
    version="1.0.0",
)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("secure_json_loader")


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _validate_schema(data: Any) -> None:
    """
    Validate `data` against the predefined JSON schema.

    Raises:
        jsonschema.exceptions.ValidationError: If validation fails.
    """
    jsonschema.validate(instance=data, schema=SCHEMA)


# --------------------------------------------------------------------------- #
# API endpoints
# --------------------------------------------------------------------------- #

@app.post("/load", response_class=JSONResponse)
async def load(request: Request) -> Dict[str, Any]:
    """
    Accept a binary payload, decode it as UTF‑8 JSON, validate against the schema,
    and return the parsed data.

    Returns:
        A JSON response containing the parsed data on success.

    Raises:
        HTTPException: 400 for bad requests, 413 for payload too large.
    """
    # Read raw body
    body = await request.body()
    logger.debug("Received raw payload of %d bytes", len(body))

    # Enforce payload size limit
    if len(body) > MAX_PAYLOAD_SIZE:
        logger.warning("Payload size %d exceeds maximum allowed %d",
                       len(body), MAX_PAYLOAD_SIZE)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Payload too large",
        )

    # Decode bytes to string
    try:
        payload_str = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        logger.warning("Failed to decode payload as UTF-8: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload must be valid UTF-8",
        ) from exc

    # Parse JSON
    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError as exc:
        logger.warning("JSON decoding error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        ) from exc

    # Validate against schema
    try:
        _validate_schema(data)
    except jsonschema.exceptions.ValidationError as exc:
        logger.warning("Schema validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Schema validation error: {exc.message}",
        ) from exc

    # At this point, `data` is safe to use.
    logger.info("Successfully validated payload from %s", request.client.host)

    return {"status": "success", "data": data}


# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

def main() -> None:
    """
    Run the FastAPI application using Uvicorn.
    """
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()