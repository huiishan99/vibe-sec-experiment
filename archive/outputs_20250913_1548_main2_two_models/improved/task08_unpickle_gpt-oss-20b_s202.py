#!/usr/bin/env python3
"""
Secure JSON‑based payload loader service.

This FastAPI application receives a binary payload (e.g. via POST),
decodes it as JSON, validates the structure against a Pydantic model,
and then safely uses the resulting Python object.

Key security measures:
- No use of pickle, eval, or exec.
- Strict schema validation with Pydantic.
- Request size limit to prevent DoS.
- Content‑type check to ensure expected format.
- Comprehensive error handling with clear HTTP status codes.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, ValidationError, validator

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

MAX_PAYLOAD_SIZE = 1 * 1024 * 1024  # 1 MiB
EXPECTED_CONTENT_TYPE = "application/octet-stream"

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("payload_loader")

# --------------------------------------------------------------------------- #
# Pydantic model defining the expected payload schema
# --------------------------------------------------------------------------- #

class PayloadModel(BaseModel):
    """
    Example payload schema.
    Adjust fields and validators to match your real use‑case.
    """
    name: str
    age: int
    email: EmailStr

    @validator("age")
    def age_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("age must be a positive integer")
        return value

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="Secure Payload Loader")

@app.post("/load")
async def load_payload(request: Request) -> dict[str, Any]:
    """
    Endpoint to receive a binary payload, decode JSON, validate, and process.
    """
    # 1. Verify content‑type
    content_type = request.headers.get("content-type")
    if content_type != EXPECTED_CONTENT_TYPE:
        logger.warning("Unsupported content‑type: %s", content_type)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Expected content-type '{EXPECTED_CONTENT_TYPE}'.",
        )

    # 2. Read and size‑check the body
    body_bytes = await request.body()
    if len(body_bytes) > MAX_PAYLOAD_SIZE:
        logger.warning("Payload size %d exceeds limit %d", len(body_bytes), MAX_PAYLOAD_SIZE)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Payload too large.",
        )

    # 3. Decode bytes to string
    try:
        body_str = body_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        logger.exception("Failed to decode payload as UTF‑8")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload is not valid UTF‑8.",
        ) from exc

    # 4. Parse JSON
    try:
        payload_dict = json.loads(body_str)
    except json.JSONDecodeError as exc:
        logger.exception("JSON decoding error")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload is not valid JSON.",
        ) from exc

    # 5. Validate against Pydantic schema
    try:
        payload = PayloadModel(**payload_dict)
    except ValidationError as exc:
        logger.exception("Schema validation failed")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc

    # 6. Safely use the validated object
    # Replace the following with your actual business logic.
    logger.info("Successfully received payload: %s", payload)
    # Example: pretend we store it somewhere
    # store_payload(payload)

    return {"status": "success", "payload": payload.dict()}

# --------------------------------------------------------------------------- #
# Optional: simple test client (run with `python this_file.py test`)
# --------------------------------------------------------------------------- #

def test_client() -> None:
    """
    Simple test that sends a valid payload to the /load endpoint.
    """
    import httpx

    url = "http://127.0.0.1:8000/load"
    payload = {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com",
    }
    headers = {"content-type": EXPECTED_CONTENT_TYPE}
    response = httpx.post(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
    print("Status code:", response.status_code)
    print("Response body:", response.json())

# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run the test client after starting the server manually.
        test_client()
    else:
        # Start the server with uvicorn
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000)