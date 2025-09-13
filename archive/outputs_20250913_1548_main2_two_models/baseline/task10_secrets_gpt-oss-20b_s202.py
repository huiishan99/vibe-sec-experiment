#!/usr/bin/env python3
"""
Minimal example of connecting to a REST API that requires an API key.

The key is read from the environment variable `API_KEY`.  The script
performs a simple GET request to a placeholder endpoint and prints the
JSON response.

Dependencies:
    pip install requests
"""

import os
import sys
import requests
from typing import Any, Dict

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# The base URL of the API you want to call.
# Replace this with the real endpoint you need.
API_BASE_URL = "https://api.example.com/v1"

# The specific resource you want to fetch.
# For example, "/users/me" or "/data".
API_ENDPOINT = "/resource"

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Raises:
        RuntimeError: If the key is not set.
    """
    key = os.getenv("API_KEY")
    if not key:
        raise RuntimeError("API_KEY environment variable is not set.")
    return key

def build_headers(api_key: str) -> Dict[str, str]:
    """
    Construct the HTTP headers required for authentication.

    Args:
        api_key: The API key string.

    Returns:
        A dictionary of HTTP headers.
    """
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

def fetch_resource(endpoint: str, headers: Dict[str, str]) -> Any:
    """
    Perform a GET request to the specified endpoint.

    Args:
        endpoint: The API path (e.g., "/resource").
        headers: HTTP headers including authentication.

    Returns:
        The parsed JSON response.

    Raises:
        requests.HTTPError: If the HTTP request fails.
    """
    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Raises an error for 4xx/5xx responses
    return response.json()

# --------------------------------------------------------------------------- #
# Main execution
# --------------------------------------------------------------------------- #

def main() -> None:
    """
    Main entry point of the script.
    """
    try:
        api_key = get_api_key()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    headers = build_headers(api_key)

    try:
        data = fetch_resource(API_ENDPOINT, headers)
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Pretty‑print the JSON response
    import json
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()