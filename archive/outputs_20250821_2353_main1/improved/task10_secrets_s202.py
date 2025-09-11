#!/usr/bin/env python3
"""
api_client.py

A minimal, secure example of how to connect to a third‑party API
using an API key that is loaded from environment variables.

Key points:
* Secrets are never hard‑coded.
* The `python-dotenv` package is used to load a local `.env` file
  (only for development; in production the variables should be
  injected by the deployment environment).
* The API key is read once at import time and stored in a module‑level
  constant.  It is never logged or printed.
* The `requests` library is used with a timeout and a session object
  for connection pooling.
* Errors are handled gracefully and logged at an appropriate level.

Usage
-----
1. Install dependencies:
   pip install requests python-dotenv

2. Create a `.env` file in the same directory (see the sample below).

3. Run the script:
   python api_client.py

"""

import os
import logging
from typing import Any, Dict

import requests
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Load environment variables from a .env file if present.
# In production, the environment will already contain the variables.
load_dotenv()

# Retrieve the API key from the environment.
# If the key is missing, the program will exit with an error message.
API_KEY: str = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError(
        "Missing required environment variable 'API_KEY'. "
        "Please set it in your environment or in a .env file."
    )

# Base URL for the API.  Replace with the actual endpoint you need.
API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.example.com/v1")

# Configure logging.  In production, you might want to set the level to WARNING
# or ERROR to reduce noise.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _get_headers() -> Dict[str, str]:
    """
    Construct the HTTP headers required for the API request.
    The API key is included in the Authorization header.
    """
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def _handle_response(response: requests.Response) -> Any:
    """
    Validate the HTTP response and return the parsed JSON data.
    Raise an exception for non‑2xx status codes.
    """
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        logger.error(
            "API request failed: %s %s",
            response.status_code,
            response.text,
        )
        raise exc

    try:
        return response.json()
    except ValueError:
        logger.error("Failed to parse JSON response.")
        raise

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def get_resource(resource_id: str) -> Any:
    """
    Fetch a single resource from the API.

    Parameters
    ----------
    resource_id : str
        The unique identifier of the resource to retrieve.

    Returns
    -------
    Any
        The parsed JSON response from the API.

    Raises
    ------
    requests.HTTPError
        If the HTTP request fails.
    """
    url = f"{API_BASE_URL}/resources/{resource_id}"
    logger.info("Fetching resource %s from %s", resource_id, url)

    with requests.Session() as session:
        try:
            response = session.get(
                url,
                headers=_get_headers(),
                timeout=10,  # seconds
            )
        except requests.RequestException as exc:
            logger.exception("Network error while requesting %s", url)
            raise exc

    return _handle_response(response)

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Replace '12345' with a real resource ID for your API.
    try:
        data = get_resource("12345")
        logger.info("Received data: %s", data)
    except Exception as exc:
        logger.error("An error occurred: %s", exc)
        exit(1)