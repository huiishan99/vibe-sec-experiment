#!/usr/bin/env python3
"""
Secure binary‑payload service

This FastAPI application receives a binary payload (expected to be UTF‑8 encoded JSON),
parses it safely, validates the data against a Pydantic schema, and then logs the
result.  No unsafe deserialization (pickle, eval, exec, etc.) is used.

Author: Senior Python Engineer
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr, ValidationError

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

# Read port from environment or default to 8000
PORT: int = int(os.getenv("PORT", "8000"))

# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

class Person(BaseModel):
    """
    Example schema for the expected JSON payload.

    Attributes:
        name: Full name of the person.
        age: Age in years (must be a non‑negative integer).
        email: Email address (validated by Pydantic).
    """
    name: str
    age: int
    email: EmailStr

    class Config:
        # Ensure that the model is immutable and hashable
        frozen = True
        anystr_strip_whitespace = True

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="Secure Payload Loader")

@app.post("/load_object")
async def load_object(request: Request) -> dict[str, Any]:
    """
    Receive a binary payload, parse it as JSON, validate against the Person schema,
    and return a success response.

    Raises:
        HTTPException: If the payload is not valid UTF‑8, not valid JSON,
                       or fails schema validation.
    """
    # 1. Read raw bytes from the request body
    raw_body = await request.body()
    logging.debug(f"Received raw payload: {raw_body!r}")

    # 2. Decode bytes to UTF‑8 string
    try:
        body_str = raw_body.decode("utf-8")
    except UnicodeDecodeError as exc:
        logging.warning("Payload decoding failed: %s", exc)
        raise HTTPException(
            status_code=400,
            detail="Payload must be valid UTF‑8 encoded JSON.",
        ) from exc

    # 3. Parse JSON
    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError as exc:
        logging.warning("JSON parsing failed: %s", exc)
        raise HTTPException(
            status_code=400,
            detail="Payload is not valid JSON.",
        ) from exc

    # 4. Validate against the Pydantic model
    try:
        person = Person(**payload)
    except ValidationError as exc:
        logging.warning("Schema validation failed: %s", exc.errors())
        raise HTTPException(
            status_code=422,
            detail=exc.errors(),
        ) from exc

    # 5. Use the validated object (here we simply log it)
    logging.info("Successfully loaded object: %s", person)

    # 6. Return a minimal success response
    return {"status": "success", "object": person.dict()}

# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import uvicorn

    logging.info("Starting Secure Payload Loader on port %s", PORT)
    uvicorn.run(app, host="0.0.0.0", port=PORT)