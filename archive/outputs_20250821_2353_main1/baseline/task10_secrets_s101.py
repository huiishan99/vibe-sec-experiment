#!/usr/bin/env python3
"""
Minimal example of connecting to a REST API that requires an API key.

Requirements:
    pip install requests

Usage:
    1. Set your API key in the environment variable `API_KEY`.
    2. Run the script: `python api_example.py`
"""

import os
import sys
import requests
from typing import Any, Dict, Optional

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Base URL of the API you want to call.
# Replace this with the actual endpoint you need.
BASE_URL = "https://api.example.com/v1"

# The name of the HTTP header that the API expects for the key.
# Common names are "Authorization" or "X-API-Key".
API_KEY_HEADER = "X-API-Key"

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Raises:
        RuntimeError: If the key is not found.
    """
    key = os.getenv("API_KEY")
    if not key:
        raise RuntimeError("API key not found. Set the 'API_KEY' environment variable.")
    return key

def make_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform a GET request to the API.

    Args:
        endpoint: Path relative to BASE_URL (e.g., "/users").
        params: Optional query parameters.

    Returns:
        Parsed JSON response.

    Raises:
        requests.HTTPError: If the response status is not 2xx.
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {API_KEY_HEADER: get_api_key()}

    response = requests.get(url, headers=headers, params=params, timeout=10)

    # Raise an exception for HTTP error codes (4xx, 5xx)
    response.raise_for_status()

    # Return the JSON payload
    return response.json()

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #

def main() -> None:
    """
    Example: Fetch a list of resources from the API.
    """
    try:
        # Replace '/resources' with the actual endpoint you need.
        data = make_request("/resources")
        print("API response:")
        print(data)
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {http_err.response.text}")
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    main()