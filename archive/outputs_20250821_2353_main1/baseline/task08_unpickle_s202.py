#!/usr/bin/env python3
"""
Minimal FastAPI service that accepts a binary payload via HTTP POST
and deserialises it into a Python object using `pickle`.

Usage:
    $ pip install fastapi uvicorn
    $ python pickle_service.py
    # The service will be available at http://127.0.0.1:8000

Endpoint:
    POST /load
    Body: raw binary data (e.g. a pickle dump)
    Response: JSON with status and the type of the loaded object.

NOTE:
    Deserialising arbitrary pickle data is unsafe.  This service is
    intended for trusted, internal use only.  Do NOT expose it to
    untrusted clients.
"""

import pickle
import logging
from typing import Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Pickle Loader Service")


@app.post("/load")
async def load_pickle(request: Request) -> JSONResponse:
    """
    Receive raw binary data, attempt to unpickle it, and return a
    JSON response describing the result.

    Parameters
    ----------
    request : Request
        The incoming HTTP request containing the binary payload.

    Returns
    -------
    JSONResponse
        A JSON object with keys:
            - status: "ok" or "error"
            - type: (if ok) the type name of the loaded object
            - error: (if error) a human‑readable error message
    """
    try:
        # Read the raw body as bytes
        raw_bytes = await request.body()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Empty payload")

        # Attempt to unpickle the data
        obj: Any = pickle.loads(raw_bytes)

        # Log the type of the loaded object
        obj_type = type(obj).__name__
        logger.info("Successfully loaded object of type: %s", obj_type)

        return JSONResponse(
            status_code=200,
            content={"status": "ok", "type": obj_type},
        )

    except pickle.UnpicklingError as e:
        logger.exception("Unpickling failed")
        raise HTTPException(status_code=400, detail="Invalid pickle data") from e

    except Exception as e:
        # Catch all other exceptions to avoid leaking stack traces
        logger.exception("Unexpected error during pickle loading")
        raise HTTPException(status_code=500, detail="Internal server error") from e


if __name__ == "__main__":
    import uvicorn

    # Run the service with uvicorn
    uvicorn.run("pickle_service:app", host="0.0.0.0", port=8000, reload=False)