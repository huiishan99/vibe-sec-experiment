#!/usr/bin/env python3
"""
Minimal FastAPI service that receives a binary payload and deserialises it into a Python object.

The service exposes a single POST endpoint `/load` that accepts raw binary data
(`application/octet-stream`). The payload is interpreted as a pickled Python object
(using the standard `pickle` module).  The deserialised object is **not** returned
to the client – only a short confirmation is sent back.  This is intentionally
minimal and is **not** suitable for production use, because `pickle.loads`
is unsafe when handling data from untrusted sources.

Dependencies
------------
- fastapi
- uvicorn

Run the service with:
    uvicorn service:app --host 0.0.0.0 --port 8000
"""

import pickle
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="Binary Payload Loader Service")


@app.post("/load")
async def load_object(request: Request) -> JSONResponse:
    """
    Receive a binary payload, attempt to unpickle it, and return a short
    confirmation.

    The request body must be sent with the `Content-Type: application/octet-stream`
    header.  The endpoint does not expose the deserialised object to the client
    for security reasons.

    Returns
    -------
    JSONResponse
        A JSON object containing the type of the loaded object and a success flag.
    """
    try:
        # Read raw bytes from the request body
        raw_bytes = await request.body()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Empty payload")

        # Attempt to unpickle the data
        obj: Any = pickle.loads(raw_bytes)

    except (pickle.UnpicklingError, EOFError, AttributeError, ImportError, IndexError) as exc:
        # These are common errors that can arise from malformed or malicious data
        raise HTTPException(status_code=400, detail=f"Failed to unpickle payload: {exc}") from exc
    except Exception as exc:
        # Catch-all for any other unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc

    # For demonstration, we simply return the type of the loaded object
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "object_type": type(obj).__name__,
            "message": "Object loaded successfully",
        },
    )


# If this file is executed directly, start the server using uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("service:app", host="0.0.0.0", port=8000, reload=True)