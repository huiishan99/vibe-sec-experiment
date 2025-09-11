"""
Minimal FastAPI web application with structured logging.

This file demonstrates how to:
1. Configure Python's built‑in logging module to write logs to both the console
   and a file.
2. Add a simple request/response logging middleware.
3. Log application events from within route handlers.

Run the app with:
    uvicorn this_file_name:app --reload
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #

# Create a log directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Define log format
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,          # Minimum level to capture
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler(
            LOG_DIR / "app.log",
            mode="a",
            encoding="utf-8",
        ),
    ],
)

# Create a module‑specific logger
logger = logging.getLogger("webapp")

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="Logging Demo App")

# --------------------------------------------------------------------------- #
# Middleware to log each request and response
# --------------------------------------------------------------------------- #

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming request and outgoing response."""
    # Log request details
    logger.info(
        f"Incoming request: {request.method} {request.url.path}"
    )

    # Process request
    response: Response = await call_next(request)

    # Log response status
    logger.info(
        f"Response status: {response.status_code} for {request.method} {request.url.path}"
    )
    return response

# --------------------------------------------------------------------------- #
# Sample route
# --------------------------------------------------------------------------- #

@app.get("/hello")
async def hello_world():
    """Return a friendly greeting."""
    logger.debug("hello_world endpoint called")
    return JSONResponse(content={"message": "Hello, world!"})

# --------------------------------------------------------------------------- #
# Health check route
# --------------------------------------------------------------------------- #

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    logger.debug("health_check endpoint called")
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import uvicorn

    # Run the app with uvicorn
    uvicorn.run(
        "this_file_name:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )