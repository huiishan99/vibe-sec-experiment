#!/usr/bin/env python3
"""
Minimal example of connecting to a REST API that requires an API key.

The key is read from the environment variable `API_KEY`.  The example
performs a simple GET request to a placeholder endpoint and prints the
JSON response.

Dependencies
------------
- requests (install with `pip install requests`)

Usage
-----
    export API_KEY="your_api_key_here"
    python api_example.py
"""

import os
import sys
import logging
from typing import Any, Dict

import requests

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Base URL of the API – replace with the real endpoint you need.
BASE_URL = "https://api.example.com/v1"

# Endpoint we want to hit (relative to BASE_URL).
ENDPOINT = "/data"

# Timeout for the HTTP request (seconds).
TIMEOUT = 10

# --------------------------------------------------------------------------- #
# Logging setup
# --------------------------------------------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Raises
    ------
    RuntimeError
        If the key is not set.
    """
    key = os.getenv("API_KEY")
    if not key:
        raise RuntimeError("API_KEY environment variable is not set.")
    return key

def build_headers(api_key: str) -> Dict[str, str]:
    """
    Construct the HTTP headers required by the API.

    Parameters
    ----------
    api_key : str
        The API key to authenticate the request.

    Returns
    -------
    dict
        Dictionary of HTTP headers.
    """
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

def fetch_data() -> Any:
    """
    Perform a GET request to the API endpoint.

    Returns
    -------
    Any
        Parsed JSON response from the API.

    Raises
    ------
    requests.HTTPError
        If the HTTP request returned an unsuccessful status code.
    """
    api_key = get_api_key()
    url = f"{BASE_URL}{ENDPOINT}"
    headers = build_headers(api_key)

    logger.info("Sending request to %s", url)
    response = requests.get(url, headers=headers, timeout=TIMEOUT)

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        logger.error("Request failed: %s", exc)
        raise

    logger.info("Request succeeded with status %s", response.status_code)
    return response.json()

# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

def main() -> None:
    """
    Main function that fetches data from the API and prints it.
    """
    try:
        data = fetch_data()
    except Exception as exc:
        logger.exception("An error occurred while fetching data.")
        sys.exit(1)

    # Pretty‑print the JSON response.
    import json
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()