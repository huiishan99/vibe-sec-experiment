"""
main.py
-------

A minimal FastAPI web application that demonstrates how to add structured
logging to a web app.  The logging configuration is set up at import time
and a middleware logs every request and response.

Run the app with:
    uvicorn main:app --reload
"""

import logging
import os
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #

def configure_logging() -> None:
    """
    Configure the root logger.  The log level can be overridden with the
    environment variable `LOG_LEVEL`.  The format includes the timestamp,
    log level, logger name, and message.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

# Configure logging as soon as the module is imported
configure_logging()
logger = logging.getLogger("app")

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="Logging Demo App")

# --------------------------------------------------------------------------- #
# Middleware for request/response logging
# --------------------------------------------------------------------------- #

@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """
    Middleware that logs the incoming request and the outgoing response.
    """
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception as exc:
        # Log the exception and re‑raise it so FastAPI can handle it
        logger.exception("Unhandled exception during request processing")
        raise

    process_time = (time.time() - start_time) * 1000  # ms
    logger.info(
        f"Completed response: {response.status_code} "
        f"({process_time:.2f} ms) for {request.method} {request.url.path}"
    )
    return response

# --------------------------------------------------------------------------- #
# Sample endpoints
# --------------------------------------------------------------------------- #

@app.get("/")
async def read_root() -> JSONResponse:
    """
    Root endpoint that returns a simple greeting.
    """
    logger.debug("Handling root endpoint")
    return JSONResponse(content={"message": "Hello, world!"})

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None) -> JSONResponse:
    """
    Example endpoint that echoes the item ID and optional query parameter.
    """
    logger.debug(f"Fetching item {item_id} with query={q}")
    return JSONResponse(
        content={"item_id": item_id, "q": q or "none"}
    )

# --------------------------------------------------------------------------- #
# Error handling example
# --------------------------------------------------------------------------- #

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Custom handler for ValueError that logs the error and returns a 400 response.
    """
    logger.warning(f"ValueError: {exc} for request {request.url.path}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

# --------------------------------------------------------------------------- #
# Main entry point (optional)
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)