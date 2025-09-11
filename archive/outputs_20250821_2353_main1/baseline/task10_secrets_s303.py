#!/usr/bin/env python3
"""
Minimal example of connecting to a REST API that requires an API key.

The key is read from the environment variable `API_KEY`.  The script
performs a simple GET request to a placeholder endpoint and prints the
JSON response.

Dependencies:
    - requests (install with `pip install requests`)

Usage:
    export API_KEY="your_api_key_here"
    python api_example.py
"""

import os
import sys
import requests
from typing import Any, Dict

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Base URL of the API – replace with the real endpoint.
API_BASE_URL = "https://api.example.com/v1"

# Endpoint to query – replace with the real path.
ENDPOINT = "/data"

# Timeout for the HTTP request (seconds).
REQUEST_TIMEOUT = 10


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Raises:
        RuntimeError: If the API_KEY environment variable is missing.
    """
    key = os.getenv("API_KEY")
    if not key:
        raise RuntimeError(
            "API key not found. Set the environment variable 'API_KEY'."
        )
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


def fetch_data(url: str, headers: Dict[str, str]) -> Any:
    """
    Perform a GET request to the specified URL.

    Args:
        url: Full URL to request.
        headers: HTTP headers to include.

    Returns:
        Parsed JSON response.

    Raises:
        requests.HTTPError: If the HTTP request returned an error status.
    """
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()


# --------------------------------------------------------------------------- #
# Main execution
# --------------------------------------------------------------------------- #

def main() -> None:
    """
    Main entry point: fetch data from the API and print it.
    """
    try:
        api_key = get_api_key()
        headers = build_headers(api_key)
        full_url = f"{API_BASE_URL}{ENDPOINT}"
        data = fetch_data(full_url, headers)
        print("Response JSON:")
        print(data)
    except RuntimeError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        # JSON decoding failed
        print("Failed to parse JSON response.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()