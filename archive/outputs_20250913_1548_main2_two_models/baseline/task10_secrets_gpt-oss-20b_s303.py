#!/usr/bin/env python3
"""
Minimal example of calling a REST API that requires an API key.

Requirements
------------
- Python 3.8+
- requests library (install with `pip install requests`)

How to run
----------
1. Set your API key in an environment variable named `API_KEY`:
   export API_KEY="your‑secret‑key"

   (On Windows use `set API_KEY=your‑secret‑key`)

2. Run the script:
   python api_example.py

The script will perform a GET request to a placeholder endpoint
and print the JSON response (or an error message if the request fails).
"""

import os
import sys
from typing import Any, Dict

import requests


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Replace this with the actual endpoint you want to call.
API_ENDPOINT = "https://api.example.com/v1/data"

# Optional: add any query parameters you need.
QUERY_PARAMS: Dict[str, str] = {
    "limit": "10",
    "format": "json",
}


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Raises
    ------
    RuntimeError
        If the API_KEY environment variable is missing.
    """
    key = os.getenv("API_KEY")
    if not key:
        raise RuntimeError(
            "API key not found. Set the 'API_KEY' environment variable."
        )
    return key


def fetch_data(endpoint: str, params: Dict[str, str]) -> Any:
    """
    Perform a GET request to the given endpoint with the provided params.

    Parameters
    ----------
    endpoint : str
        The full URL of the API endpoint.
    params : dict
        Query parameters to include in the request.

    Returns
    -------
    Any
        The parsed JSON response from the API.

    Raises
    ------
    requests.HTTPError
        If the HTTP request returned an unsuccessful status code.
    """
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Accept": "application/json",
    }

    response = requests.get(endpoint, headers=headers, params=params, timeout=10)

    # Raise an exception for HTTP error codes (4xx, 5xx)
    response.raise_for_status()

    # Parse JSON; if the response is not JSON, raise an error
    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("Response is not valid JSON") from exc


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

def main() -> None:
    try:
        data = fetch_data(API_ENDPOINT, QUERY_PARAMS)
    except Exception as exc:
        # Print a user‑friendly error message and exit with a non‑zero status.
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Pretty‑print the JSON response
    import json

    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()