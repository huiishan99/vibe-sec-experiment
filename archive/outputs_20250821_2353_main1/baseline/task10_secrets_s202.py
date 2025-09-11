#!/usr/bin/env python3
"""
Minimal example of connecting to a REST API that requires an API key.

The script demonstrates:
1. Reading the API key from an environment variable.
2. Building the request headers.
3. Making a GET request with the `requests` library.
4. Handling common errors and printing the JSON response.

Replace `API_URL` and the header key (`Authorization`) with the values
required by the API you are using.
"""

import os
import sys
import json
import requests
from typing import Any, Dict, Optional

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# URL of the API endpoint you want to call.
API_URL = "https://api.example.com/v1/resource"

# Name of the environment variable that holds the API key.
API_KEY_ENV_VAR = "API_KEY"

# Header name that the API expects for the key.
# Some APIs use "Authorization: Bearer <token>", others use a custom header.
API_KEY_HEADER = "Authorization"  # e.g., "Bearer <token>"


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Raises:
        RuntimeError: If the key is not set.
    """
    key = os.getenv(API_KEY_ENV_VAR)
    if not key:
        raise RuntimeError(
            f"Environment variable {API_KEY_ENV_VAR!r} is not set."
        )
    return key


def build_headers(api_key: str) -> Dict[str, str]:
    """
    Construct the HTTP headers required for the API request.

    Args:
        api_key: The API key string.

    Returns:
        A dictionary of headers.
    """
    # Example: If the API expects a Bearer token
    return {API_KEY_HEADER: f"Bearer {api_key}"}


def fetch_resource(url: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Make a GET request to the API and return the parsed JSON response.

    Args:
        url: The API endpoint URL.
        headers: HTTP headers including the API key.

    Returns:
        The JSON-decoded response as a dictionary, or None if an error occurs.
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx, 5xx)
    except requests.exceptions.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return None

    try:
        return response.json()
    except json.JSONDecodeError:
        print("Response is not valid JSON.", file=sys.stderr)
        return None


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

def main() -> None:
    """
    Entry point of the script.
    """
    try:
        api_key = get_api_key()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    headers = build_headers(api_key)

    result = fetch_resource(API_URL, headers)
    if result is not None:
        # Pretty‑print the JSON response
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()