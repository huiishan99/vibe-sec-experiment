#!/usr/bin/env python3
"""
Secure JSON payload loader service.

This service exposes a single HTTP endpoint that accepts a binary payload
containing JSON data. The payload is parsed, validated against a strict
schema, and then safely used within the application. No unsafe
deserialization (e.g. pickle, eval, exec) is performed.

Author: Senior Python Engineer
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, Field
import uvicorn

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Maximum allowed payload size (1 MiB). Adjust as needed.
MAX_PAYLOAD_SIZE: int = 1_048_576

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

class DataPayload(BaseModel):
    """
    Schema for the expected JSON payload.

    Attributes:
        id: Unique identifier (must be a positive integer).
        name: Non-empty string.
        values: List of floating point numbers (at least one element).
    """
    id: int = Field(..., gt=0, description="Positive integer identifier")
    name: str = Field(..., min_length=1, description="Non-empty name")
    values: list[float] = Field(..., min_items=1, description="List of floats")

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="Secure JSON Loader Service")

# --------------------------------------------------------------------------- #
# Exception handlers
# --------------------------------------------------------------------------- #

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return JSON-formatted error responses."""
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.post("/load", summary="Load and validate JSON payload")
async def load_payload(request: Request) -> JSONResponse:
    """
    Accepts a binary payload containing JSON data, validates it against
    the DataPayload schema, and returns a success message.

    The endpoint expects the request body to be sent with the
    `application/octet-stream` MIME type.
    """
    # Read raw bytes
    body_bytes = await request.body()

    # Enforce payload size limit
    if len(body_bytes) > MAX_PAYLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload exceeds maximum allowed size of {MAX_PAYLOAD_SIZE} bytes",
        )

    # Decode bytes to string (UTF-8)
    try:
        body_str = body_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        logger.error("Failed to decode payload as UTF-8")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload is not valid UTF-8",
        ) from exc

    # Parse JSON
    try:
        payload_dict: dict[str, Any] = json.loads(body_str)
    except json.JSONDecodeError as exc:
        logger.error("JSON decoding failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        ) from exc

    # Validate against schema
    try:
        payload = DataPayload(**payload_dict)
    except ValidationError as exc:
        logger.error("Schema validation failed")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc

    # At this point, payload is safe to use.
    # (Insert application-specific logic here.)

    logger.info(f"Successfully loaded payload: {payload}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Payload loaded successfully", "data": payload.dict()},
    )

# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the application using Uvicorn
    uvicorn.run(
        "service:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
    )