"""
main.py
-------

A minimal FastAPI web application that demonstrates how to add structured
logging to a web app.  The example configures the standard `logging`
module to write JSON‑style logs to a file and to the console, and it
adds a middleware that logs every incoming HTTP request and its
response status.

Run the app with:

    uvicorn main:app --reload

The logs will be written to `app.log` and printed to the console.
"""

import logging
import logging.config
import sys
from datetime import datetime
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    # Formatters define the log message layout
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "simple": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    # Handlers send the log records to a destination
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "simple",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "json",
            "level": "DEBUG",
        },
    },
    # Root logger configuration
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}

# Apply the configuration
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="Logging Demo App")

# --------------------------------------------------------------------------- #
# Middleware to log requests and responses
# --------------------------------------------------------------------------- #

@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """
    Log the incoming request and the outgoing response.

    Parameters
    ----------
    request : Request
        The incoming HTTP request.
    call_next : Callable
        The next middleware or route handler.

    Returns
    -------
    Response
        The HTTP response returned by the downstream handler.
    """
    # Log request details
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "headers": dict(request.headers),
        },
    )

    # Process the request
    try:
        response = await call_next(request)
    except Exception as exc:
        # Log unexpected errors
        logger.exception("Unhandled exception while processing request")
        raise

    # Log response details
    logger.info(
        "Outgoing response",
        extra={
            "status_code": response.status_code,
            "headers": dict(response.headers),
        },
    )

    return response

# --------------------------------------------------------------------------- #
# Sample routes
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
    Endpoint that returns an item by ID, optionally filtered by a query string.

    Parameters
    ----------
    item_id : int
        The ID of the item to retrieve.
    q : str, optional
        Optional query string for filtering.

    Returns
    -------
    JSONResponse
        The item data.
    """
    logger.debug("Handling read_item", extra={"item_id": item_id, "q": q})
    item = {"item_id": item_id, "value": f"Item {item_id}"}
    if q:
        item["query"] = q
    return JSONResponse(content=item)

# --------------------------------------------------------------------------- #
# Application startup/shutdown events
# --------------------------------------------------------------------------- #

@app.on_event("startup")
async def startup_event() -> None:
    """
    Log a message when the application starts.
    """
    logger.info("Application startup")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Log a message when the application shuts down.
    """
    logger.info("Application shutdown")