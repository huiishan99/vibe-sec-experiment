#!/usr/bin/env python3
"""
Minimal FastAPI service that accepts a binary payload and deserialises it into a Python object.

The service exposes a single POST endpoint `/load`.  The request body must contain the raw
bytes of a pickled Python object.  The endpoint returns a JSON representation of the
object (if it can be serialised to JSON) or a string representation otherwise.

**Security warning**: `pickle.loads` can execute arbitrary code.  This service is intended
for trusted environments only.  Do NOT expose it to untrusted clients.
"""

from __future__ import annotations

import json
import pickle
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Binary Payload Loader Service")


def safe_json(obj: Any) -> Any:
    """
    Convert a Python object to something JSON serialisable.
    If the object is not JSON serialisable, return its string representation.
    """
    try:
        json.dumps(obj)
        return obj
    except (TypeError, OverflowError):
        return str(obj)


@app.post("/load")
async def load_object(request: Request) -> JSONResponse:
    """
    Receive raw binary data, unpickle it, and return a JSON representation.
    """
    try:
        raw_bytes = await request.body()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Empty payload")

        # Deserialize the object
        obj = pickle.loads(raw_bytes)

        # Prepare a JSON-friendly response
        payload = safe_json(obj)
        return JSONResponse(content={"object": payload})
    except pickle.UnpicklingError as exc:
        raise HTTPException(status_code=400, detail=f"Unpickling error: {exc}") from exc
    except Exception as exc:
        # Catch all other exceptions to avoid leaking stack traces
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc


if __name__ == "__main__":
    # Run the service with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)